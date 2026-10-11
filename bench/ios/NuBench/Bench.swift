import AVFoundation
import VideoToolbox

struct Job: Codable {
    let input: String
    let output: String
    let codec: String  // "h264", "hevc", or "sr" (Apple's low-latency super resolution, 2x: raw NV12 out, or HEVC at kbps if kbps > 0)
    let kbps: Int
}

struct JobResult: Codable {
    let output: String
    let frames: Int
    let seconds: Double
    let fps: Double
    let bytes: Int
}

struct Report: Codable {
    let device: String
    let os: String
    let results: [JobResult]
}

/// Collects encoder output; VideoToolbox calls back on its own thread.
final class Sink: @unchecked Sendable {
    private let lock = NSLock()
    private var items: [CMSampleBuffer] = []
    func append(_ b: CMSampleBuffer) { lock.withLock { items.append(b) } }
    var buffers: [CMSampleBuffer] { lock.withLock { items } }
}

enum BenchError: Error {
    case noVideoTrack(String)
    case session(OSStatus)
    case writer(String)
}

enum Bench {
    static func run(in docs: URL) async throws {
        let jobs = try JSONDecoder().decode([Job].self, from: Data(contentsOf: docs.appending(path: "jobs.json")))
        var results: [JobResult] = []
        for job in jobs {
            let r = job.codec == "sr" ? try await superResolve(job, in: docs) : try await encode(job, in: docs)
            print("\(job.output) \(r.frames) frames \(String(format: "%.1f", r.fps)) fps \(r.bytes) B")
            results.append(r)
        }
        var info = utsname()
        uname(&info)
        let model = withUnsafeBytes(of: info.machine) { String(decoding: $0.prefix { $0 != 0 }, as: UTF8.self) }
        let report = Report(device: model, os: ProcessInfo.processInfo.operatingSystemVersionString, results: results)
        let enc = JSONEncoder()
        enc.outputFormatting = [.prettyPrinted, .sortedKeys]
        try enc.encode(report).write(to: docs.appending(path: "results-ios.json"))
    }

    /// Decodes the input and upscales each frame 2x with VTLowLatencySuperResolutionScaler (the Neural Engine
    /// video-call scaler in iOS 26). Writes raw NV12 frames so the Mac scores exactly what the scaler produced.
    static func superResolve(_ job: Job, in docs: URL) async throws -> JobResult {
        let asset = AVURLAsset(url: docs.appending(path: job.input))
        guard let track = try await asset.loadTracks(withMediaType: .video).first else { throw BenchError.noVideoTrack(job.input) }
        let size = try await track.load(.naturalSize)
        let w = Int(size.width), h = Int(size.height)
        guard VTLowLatencySuperResolutionScalerConfiguration.isSupported else { throw BenchError.writer("super resolution not supported") }
        let factors = VTLowLatencySuperResolutionScalerConfiguration.supportedScaleFactors(frameWidth: w, frameHeight: h)
        print("supported scale factors for \(w)x\(h): \(factors)")
        guard factors.contains(2.0) else { throw BenchError.writer("2x not supported for \(w)x\(h): \(factors)") }
        let config = VTLowLatencySuperResolutionScalerConfiguration(frameWidth: w, frameHeight: h, scaleFactor: 2.0)
        let processor = VTFrameProcessor()
        try processor.startSession(configuration: config)
        defer { processor.endSession() }

        let reader = try AVAssetReader(asset: asset)
        let out = AVAssetReaderTrackOutput(track: track, outputSettings: config.sourcePixelBufferAttributes)
        reader.add(out)
        var pool: CVPixelBufferPool?
        CVPixelBufferPoolCreate(nil, nil, config.destinationPixelBufferAttributes as CFDictionary, &pool)
        var srcPool: CVPixelBufferPool?
        CVPixelBufferPoolCreate(nil, nil, config.sourcePixelBufferAttributes as CFDictionary, &srcPool)
        var xfer: VTPixelTransferSession?
        VTPixelTransferSessionCreate(allocator: nil, pixelTransferSessionOut: &xfer)
        guard let pool, let srcPool, let xfer else { throw BenchError.writer("no pixel buffer pools") }

        let url = docs.appending(path: job.output)
        FileManager.default.createFile(atPath: url.path, contents: nil)
        let fh = try FileHandle(forWritingTo: url)
        defer { try? fh.close() }
        // 4K raw frames don't fit on the Mac, so large outputs are re-encoded near-losslessly in hardware instead.
        let compress = job.kbps > 0
        var session: VTCompressionSession?
        let sink = Sink()
        if compress {
            let spec = [kVTVideoEncoderSpecification_RequireHardwareAcceleratedVideoEncoder: true] as CFDictionary
            let st = VTCompressionSessionCreate(allocator: nil, width: Int32(w * 2), height: Int32(h * 2), codecType: kCMVideoCodecType_HEVC,
                                                encoderSpecification: spec, imageBufferAttributes: nil, compressedDataAllocator: nil,
                                                outputCallback: nil, refcon: nil, compressionSessionOut: &session)
            guard st == noErr, let session else { throw BenchError.session(st) }
            VTSessionSetProperty(session, key: kVTCompressionPropertyKey_AverageBitRate, value: (job.kbps * 1000) as CFTypeRef)
            VTSessionSetProperty(session, key: kVTCompressionPropertyKey_Quality, value: 1.0 as CFTypeRef)
            VTCompressionSessionPrepareToEncodeFrames(session)
        }

        reader.startReading()
        var frames = 0
        var busy = 0.0
        var shape = ""
        while let sb = out.copyNextSampleBuffer() {
            guard let decoded = CMSampleBufferGetImageBuffer(sb) else { continue }
            let pts = CMSampleBufferGetPresentationTimeStamp(sb)
            // The scaler needs the padded layout in sourcePixelBufferAttributes, which AVAssetReader doesn't honour.
            var padded: CVPixelBuffer?
            CVPixelBufferPoolCreatePixelBuffer(nil, srcPool, &padded)
            guard let src = padded else { throw BenchError.writer("source buffer") }
            let xs = VTPixelTransferSessionTransferImage(xfer, from: decoded, to: src)
            if xs != noErr { throw BenchError.session(xs) }
            var dst: CVPixelBuffer?
            CVPixelBufferPoolCreatePixelBuffer(nil, pool, &dst)
            guard let dst, let sf = VTFrameProcessorFrame(buffer: src, presentationTimeStamp: pts),
                  let df = VTFrameProcessorFrame(buffer: dst, presentationTimeStamp: pts) else { throw BenchError.writer("frame setup") }
            let t0 = Date()
            try await processor.process(parameters: VTLowLatencySuperResolutionScalerParameters(sourceFrame: sf, destinationFrame: df))
            busy += Date().timeIntervalSince(t0)
            if let session {
                let st = VTCompressionSessionEncodeFrame(session, imageBuffer: dst, presentationTimeStamp: pts, duration: .invalid,
                                                         frameProperties: nil, infoFlagsOut: nil) { status, _, buf in
                    if status == noErr, let buf { sink.append(buf) }
                }
                if st != noErr { throw BenchError.session(st) }
            } else {
                try fh.write(contentsOf: nv12(dst))
            }
            shape = "\(CVPixelBufferGetWidth(dst))x\(CVPixelBufferGetHeight(dst)) format \(CVPixelBufferGetPixelFormatType(dst))"
            frames += 1
        }
        if let session {
            VTCompressionSessionCompleteFrames(session, untilPresentationTimeStamp: .invalid)
            VTCompressionSessionInvalidate(session)
            try? fh.close()
            try await write(sink.buffers, to: url, fileType: .mov)
        }
        let bytes = (try FileManager.default.attributesOfItem(atPath: url.path)[.size] as? Int) ?? 0
        print("sr output \(shape)")
        return JobResult(output: job.output, frames: frames, seconds: busy, fps: Double(frames) / busy, bytes: bytes)
    }

    /// Packs a bi-planar 4:2:0 buffer into tightly packed NV12 bytes, converting other formats first.
    private static func nv12(_ buf: CVPixelBuffer) throws -> Data {
        var b = buf
        let fmt = CVPixelBufferGetPixelFormatType(buf)
        if fmt != kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange {
            var t: VTPixelTransferSession?
            VTPixelTransferSessionCreate(allocator: nil, pixelTransferSessionOut: &t)
            var o: CVPixelBuffer?
            CVPixelBufferCreate(nil, CVPixelBufferGetWidth(buf), CVPixelBufferGetHeight(buf), kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange,
                                [kCVPixelBufferIOSurfacePropertiesKey: [:]] as CFDictionary, &o)
            guard let t, let o else { throw BenchError.writer("transfer setup") }
            let st = VTPixelTransferSessionTransferImage(t, from: buf, to: o)
            if st != noErr { throw BenchError.session(st) }
            b = o
        }
        CVPixelBufferLockBaseAddress(b, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(b, .readOnly) }
        var data = Data()
        let w = CVPixelBufferGetWidth(b), h = CVPixelBufferGetHeight(b)
        for plane in 0..<2 {
            let rows = plane == 0 ? h : h / 2
            let base = CVPixelBufferGetBaseAddressOfPlane(b, plane)!
            let stride = CVPixelBufferGetBytesPerRowOfPlane(b, plane)
            for r in 0..<rows { data.append(base.advanced(by: r * stride).assumingMemoryBound(to: UInt8.self), count: w) }
        }
        return data
    }

    /// Decodes the input in full, feeding frames to a hardware-only VTCompressionSession at the input's size.
    /// Settings match a live call: real time, no frame reordering, average bitrate capped per second.
    static func encode(_ job: Job, in docs: URL) async throws -> JobResult {
        let asset = AVURLAsset(url: docs.appending(path: job.input))
        guard let track = try await asset.loadTracks(withMediaType: .video).first else { throw BenchError.noVideoTrack(job.input) }
        let size = try await track.load(.naturalSize)
        let fps = try await track.load(.nominalFrameRate)

        let reader = try AVAssetReader(asset: asset)
        let out = AVAssetReaderTrackOutput(track: track, outputSettings: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange,
            kCVPixelBufferIOSurfacePropertiesKey as String: [:] as [String: Any],
        ])
        out.alwaysCopiesSampleData = false
        reader.add(out)

        var session: VTCompressionSession?
        let spec = [kVTVideoEncoderSpecification_RequireHardwareAcceleratedVideoEncoder: true] as CFDictionary
        let codec = job.codec == "h264" ? kCMVideoCodecType_H264 : kCMVideoCodecType_HEVC
        var st = VTCompressionSessionCreate(allocator: nil, width: Int32(size.width), height: Int32(size.height), codecType: codec,
                                            encoderSpecification: spec, imageBufferAttributes: nil, compressedDataAllocator: nil,
                                            outputCallback: nil, refcon: nil, compressionSessionOut: &session)
        guard st == noErr, let session else { throw BenchError.session(st) }
        let bps = job.kbps * 1000
        let props: [CFString: Any] = [
            kVTCompressionPropertyKey_RealTime: true,
            kVTCompressionPropertyKey_AllowFrameReordering: false,
            kVTCompressionPropertyKey_ProfileLevel: job.codec == "h264" ? kVTProfileLevel_H264_High_AutoLevel : kVTProfileLevel_HEVC_Main_AutoLevel,
            kVTCompressionPropertyKey_AverageBitRate: bps,
            kVTCompressionPropertyKey_DataRateLimits: [bps / 8, 1] as CFArray,
            kVTCompressionPropertyKey_ExpectedFrameRate: fps,
            kVTCompressionPropertyKey_MaxKeyFrameIntervalDuration: 4,
        ]
        for (k, v) in props {
            st = VTSessionSetProperty(session, key: k, value: v as CFTypeRef)
            if st != noErr { print("property \(k) not set: \(st)") }
        }
        VTCompressionSessionPrepareToEncodeFrames(session)

        let sink = Sink()
        reader.startReading()
        let t0 = Date()
        var frames = 0
        while let sb = out.copyNextSampleBuffer() {
            guard let px = CMSampleBufferGetImageBuffer(sb) else { continue }
            let pts = CMSampleBufferGetPresentationTimeStamp(sb)
            st = VTCompressionSessionEncodeFrame(session, imageBuffer: px, presentationTimeStamp: pts, duration: .invalid,
                                                 frameProperties: nil, infoFlagsOut: nil) { status, _, buf in
                if status == noErr, let buf { sink.append(buf) }
            }
            if st != noErr { throw BenchError.session(st) }
            frames += 1
        }
        VTCompressionSessionCompleteFrames(session, untilPresentationTimeStamp: .invalid)
        let seconds = Date().timeIntervalSince(t0)
        VTCompressionSessionInvalidate(session)

        let url = docs.appending(path: job.output)
        try await write(sink.buffers, to: url, fileType: .mp4)

        let bytes = (try FileManager.default.attributesOfItem(atPath: url.path)[.size] as? Int) ?? 0
        return JobResult(output: job.output, frames: frames, seconds: seconds, fps: Double(frames) / seconds, bytes: bytes)
    }

    /// Writes encoded samples to a file without re-encoding.
    static func write(_ encoded: [CMSampleBuffer], to url: URL, fileType: AVFileType) async throws {
        try? FileManager.default.removeItem(at: url)
        let writer = try AVAssetWriter(outputURL: url, fileType: fileType)
        guard let first = encoded.first else { throw BenchError.writer("no frames encoded") }
        let input = AVAssetWriterInput(mediaType: .video, outputSettings: nil, sourceFormatHint: CMSampleBufferGetFormatDescription(first))
        input.expectsMediaDataInRealTime = false
        writer.add(input)
        writer.startWriting()
        writer.startSession(atSourceTime: CMSampleBufferGetPresentationTimeStamp(first))
        for buf in encoded {
            while !input.isReadyForMoreMediaData { try await Task.sleep(for: .milliseconds(2)) }
            if !input.append(buf) { throw BenchError.writer(writer.error.map { "\($0)" } ?? "append failed") }
        }
        input.markAsFinished()
        await writer.finishWriting()
        if writer.status != .completed { throw BenchError.writer(writer.error.map { "\($0)" } ?? "finish failed") }
    }
}
