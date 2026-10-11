// Runs Documents/jobs.json through the iPhone's hardware encoders, writes the encoded files and
// Documents/results-ios.json, then exits. Driven from the Mac by bench/iphone.py over devicectl.

import SwiftUI

@main
struct NuBenchApp: App {
    @State private var status = "Running"

    var body: some Scene {
        WindowGroup {
            Text(status).font(.headline).padding()
                .task {
                    let docs = URL.documentsDirectory
                    do {
                        try await Bench.run(in: docs)
                        status = "Done"
                    } catch {
                        print("FAILED: \(error)")
                        try? "\(error)".write(to: docs.appending(path: "error.txt"), atomically: true, encoding: .utf8)
                        status = "Failed"
                    }
                    exit(0)
                }
        }
    }
}
