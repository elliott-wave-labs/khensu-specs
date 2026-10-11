import AVFoundation
import VideoToolbox

struct Job: Codable {
    let input: String
    let output: String
    let codec: String  // "h264" or "hevc"
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
            let r = try await encode(job, in: docs)
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
        try? FileManager.default.removeItem(at: url)
        let writer = try AVAssetWriter(outputURL: url, fileType: .mp4)
        let encoded = sink.buffers
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

        let bytes = (try FileManager.default.attributesOfItem(atPath: url.path)[.size] as? Int) ?? 0
        return JobResult(output: job.output, frames: frames, seconds: seconds, fps: Double(frames) / seconds, bytes: bytes)
    }
}
