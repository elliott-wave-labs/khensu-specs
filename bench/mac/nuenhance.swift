// Host-side nu-media enhancement on a Mac's Neural Engine (macOS 26, Apple silicon).
//
//   nuenhance sr  IN OUT KBPS          4x super resolution (VTSuperResolutionScaler)
//   nuenhance frc IN OUT FACTOR KBPS   frame rate x FACTOR (VTFrameRateConversion)
//
// Output is 10-bit HEVC from the hardware encoder at KBPS, so the next step reads what this step produced.
// The scaler takes at most 1920 x 1080 input and only scales 4x; portrait clips are rotated before and after.

import AVFoundation
import CoreVideo
import Foundation
import VideoToolbox

enum Fail: Error { case msg(String) }

struct Reader {
    let reader: AVAssetReader
    let out: AVAssetReaderTrackOutput
    let fps: Double
    let size: CGSize

    init(_ url: URL) async throws {
        let asset = AVURLAsset(url: url)
        guard let track = try await asset.loadTracks(withMediaType: .video).first else { throw Fail.msg("no video in \(url.path)") }
        size = try await track.load(.naturalSize)
        fps = Double(try await track.load(.nominalFrameRate))
        reader = try AVAssetReader(asset: asset)
        out = AVAssetReaderTrackOutput(track: track, outputSettings: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr10BiPlanarVideoRange,
            kCVPixelBufferIOSurfacePropertiesKey as String: [:],
        ])
        out.alwaysCopiesSampleData = false
        reader.add(out)
        reader.startReading()
    }

    func next() -> (CVPixelBuffer, CMTime)? {
        guard let sb = out.copyNextSampleBuffer(), let px = CMSampleBufferGetImageBuffer(sb) else { return nil }
        return (px, CMSampleBufferGetPresentationTimeStamp(sb))
    }
}

final class Writer {
    let writer: AVAssetWriter
    let input: AVAssetWriterInput
    let adaptor: AVAssetWriterInputPixelBufferAdaptor

    init(_ url: URL, w: Int, h: Int, kbps: Int, fps: Double) throws {
        try? FileManager.default.removeItem(at: url)
        writer = try AVAssetWriter(outputURL: url, fileType: .mov)
        input = AVAssetWriterInput(mediaType: .video, outputSettings: [
            AVVideoCodecKey: AVVideoCodecType.hevc, AVVideoWidthKey: w, AVVideoHeightKey: h,
            AVVideoCompressionPropertiesKey: [
                AVVideoAverageBitRateKey: kbps * 1000,
                AVVideoProfileLevelKey: kVTProfileLevel_HEVC_Main10_AutoLevel,
                AVVideoExpectedSourceFrameRateKey: fps,
                AVVideoMaxKeyFrameIntervalKey: Int(fps.rounded()),
            ],
            AVVideoColorPropertiesKey: [
                AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
                AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
                AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2,
            ],
        ])
        input.expectsMediaDataInRealTime = false
        adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: nil)
        writer.add(input)
        writer.startWriting()
        writer.startSession(atSourceTime: .zero)
    }

    func append(_ px: CVPixelBuffer, _ t: CMTime) throws {
        while !input.isReadyForMoreMediaData { usleep(1000) }
        if !adaptor.append(px, withPresentationTime: t) { throw Fail.msg("append failed: \(String(describing: writer.error))") }
    }

    func finish() async throws {
        input.markAsFinished()
        await writer.finishWriting()
        if writer.status != .completed { throw Fail.msg("writer: \(String(describing: writer.error))") }
    }
}

func pool(_ attrs: [String: Any]) throws -> CVPixelBufferPool {
    var p: CVPixelBufferPool?
    CVPixelBufferPoolCreate(nil, nil, attrs as CFDictionary, &p)
    guard let p else { throw Fail.msg("pixel buffer pool") }
    return p
}

func buffer(_ p: CVPixelBufferPool) throws -> CVPixelBuffer {
    var b: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, p, &b)
    guard let b else { throw Fail.msg("pixel buffer") }
    return b
}

final class Transfer {
    var session: VTPixelTransferSession?
    init() { VTPixelTransferSessionCreate(allocator: nil, pixelTransferSessionOut: &session) }
    func copy(_ src: CVPixelBuffer, into p: CVPixelBufferPool) throws -> CVPixelBuffer {
        let dst = try buffer(p)
        let st = VTPixelTransferSessionTransferImage(session!, from: src, to: dst)
        if st != noErr { throw Fail.msg("transfer \(st)") }
        return dst
    }
}

func waitForModel(_ c: VTSuperResolutionScalerConfiguration) async throws {
    if c.configurationModelStatus == .ready { return }
    print("downloading the super resolution model…")
    try await withCheckedThrowingContinuation { (k: CheckedContinuation<Void, Error>) in
        c.downloadConfigurationModel { e in if let e { k.resume(throwing: e) } else { k.resume() } }
    }
    while c.configurationModelStatus != .ready { try await Task.sleep(for: .milliseconds(200)) }
}

func superResolve(_ inURL: URL, _ outURL: URL, kbps: Int) async throws {
    let r = try await Reader(inURL)
    let w = Int(r.size.width), h = Int(r.size.height)
    guard let c = VTSuperResolutionScalerConfiguration(frameWidth: w, frameHeight: h, scaleFactor: 4, inputType: .video,
                                                       usePrecomputedFlow: false, qualityPrioritization: .normal,
                                                       revision: VTSuperResolutionScalerConfiguration.defaultRevision)
    else { throw Fail.msg("super resolution refuses \(w) x \(h)") }
    try await waitForModel(c)
    let proc = VTFrameProcessor()
    try proc.startSession(configuration: c)
    defer { proc.endSession() }
    let srcPool = try pool(c.sourcePixelBufferAttributes as! [String: Any])
    let dstPool = try pool(c.destinationPixelBufferAttributes as! [String: Any])
    let xfer = Transfer()
    let wr = try Writer(outURL, w: w * 4, h: h * 4, kbps: kbps, fps: r.fps)
    var prevSrc: VTFrameProcessorFrame?, prevOut: VTFrameProcessorFrame?
    var n = 0, busy = 0.0
    let t0 = Date()
    while let (px, t) = r.next() {
        let src = try xfer.copy(px, into: srcPool)
        let dst = try buffer(dstPool)
        guard let sf = VTFrameProcessorFrame(buffer: src, presentationTimeStamp: t),
              let df = VTFrameProcessorFrame(buffer: dst, presentationTimeStamp: t),
              let p = VTSuperResolutionScalerParameters(sourceFrame: sf, previousFrame: prevSrc, previousOutputFrame: prevOut,
                                                        opticalFlow: nil, submissionMode: .sequential, destinationFrame: df)
        else { throw Fail.msg("frame setup") }
        let s = Date()
        try await proc.process(parameters: p)
        busy += Date().timeIntervalSince(s)
        try wr.append(dst, t)
        prevSrc = sf; prevOut = df
        n += 1
        if n % 100 == 0 { print("sr \(n) frames, \(String(format: "%.1f", Double(n) / busy)) fps on the Neural Engine") }
    }
    try await wr.finish()
    let report: [String: Any] = ["step": "sr", "frames": n, "in": "\(w)x\(h)", "out": "\(w * 4)x\(h * 4)",
                                 "neural_fps": Double(n) / busy, "seconds": Date().timeIntervalSince(t0)]
    print(String(data: try JSONSerialization.data(withJSONObject: report), encoding: .utf8)!)
}

func convertRate(_ inURL: URL, _ outURL: URL, factor: Int, kbps: Int) async throws {
    let r = try await Reader(inURL)
    let w = Int(r.size.width), h = Int(r.size.height)
    guard let c = VTFrameRateConversionConfiguration(frameWidth: w, frameHeight: h, usePrecomputedFlow: false,
                                                     qualityPrioritization: .quality,
                                                     revision: VTFrameRateConversionConfiguration.defaultRevision)
    else { throw Fail.msg("frame rate conversion refuses \(w) x \(h)") }
    let proc = VTFrameProcessor()
    try proc.startSession(configuration: c)
    defer { proc.endSession() }
    let srcPool = try pool(c.sourcePixelBufferAttributes as! [String: Any])
    let dstPool = try pool(c.destinationPixelBufferAttributes as! [String: Any])
    let xfer = Transfer()
    let outFps = r.fps * Double(factor)
    let wr = try Writer(outURL, w: w, h: h, kbps: kbps, fps: outFps)
    let step = CMTime(value: 1, timescale: CMTimeScale((outFps * 1000).rounded()) / 1000)
    let phases = (1..<factor).map { Float($0) / Float(factor) }
    var prev: (CVPixelBuffer, Int)?
    var i = 0, n = 0, busy = 0.0
    let t0 = Date()
    func at(_ k: Int) -> CMTime { CMTimeMultiply(step, multiplier: Int32(k)) }
    while let (px, _) = r.next() {
        let cur = try xfer.copy(px, into: srcPool)
        if let (p, pi) = prev {
            try wr.append(p, at(pi * factor))
            let dsts = try phases.map { _ in try buffer(dstPool) }
            guard let sf = VTFrameProcessorFrame(buffer: p, presentationTimeStamp: at(pi * factor)),
                  let nf = VTFrameProcessorFrame(buffer: cur, presentationTimeStamp: at(i * factor))
            else { throw Fail.msg("frame setup") }
            let dfs = try dsts.enumerated().map { k, b in
                guard let f = VTFrameProcessorFrame(buffer: b, presentationTimeStamp: at(pi * factor + k + 1)) else { throw Fail.msg("dst") }
                return f
            }
            guard let params = VTFrameRateConversionParameters(sourceFrame: sf, nextFrame: nf, opticalFlow: nil, interpolationPhase: phases,
                                                               submissionMode: .sequential, destinationFrames: dfs)
            else { throw Fail.msg("parameters") }
            let s = Date()
            try await proc.process(parameters: params)
            busy += Date().timeIntervalSince(s)
            for (k, b) in dsts.enumerated() { try wr.append(b, at(pi * factor + k + 1)) }
            n += 1
            if n % 50 == 0 { print("frc \(n) source frames, \(String(format: "%.1f", Double(n * (factor - 1)) / busy)) new frames/s") }
        }
        prev = (cur, i)
        i += 1
    }
    if let (p, pi) = prev {
        for k in 0..<factor { try wr.append(p, at(pi * factor + k)) }
    }
    try await wr.finish()
    let report: [String: Any] = ["step": "frc", "source_frames": i, "frames": i * factor, "fps_in": r.fps, "fps_out": outFps,
                                 "size": "\(w)x\(h)", "new_frames_per_s": Double(n * (factor - 1)) / busy,
                                 "seconds": Date().timeIntervalSince(t0)]
    print(String(data: try JSONSerialization.data(withJSONObject: report), encoding: .utf8)!)
}

@main
struct Main {
    static func main() async {
        let a = CommandLine.arguments
        do {
            switch a.count > 1 ? a[1] : "" {
            case "sr" where a.count == 5:
                try await superResolve(URL(fileURLWithPath: a[2]), URL(fileURLWithPath: a[3]), kbps: Int(a[4])!)
            case "frc" where a.count == 6:
                try await convertRate(URL(fileURLWithPath: a[2]), URL(fileURLWithPath: a[3]), factor: Int(a[4])!, kbps: Int(a[5])!)
            default:
                print("usage: nuenhance sr IN OUT KBPS | nuenhance frc IN OUT FACTOR KBPS")
                exit(2)
            }
        } catch {
            print("error: \(error)")
            exit(1)
        }
    }
}
