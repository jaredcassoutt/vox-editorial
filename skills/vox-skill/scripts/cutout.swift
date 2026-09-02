// Subject lift via Vision, mirroring barrier_swiftui/Helpers/SubjectExtractor.swift
// usage: cutout <in.png|jpg> <out.png>
import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else { FileHandle.standardError.write("usage: subject_cutout in out\n".data(using:.utf8)!); exit(2) }
let inURL = URL(fileURLWithPath: args[1]), outURL = URL(fileURLWithPath: args[2])
guard let src = CIImage(contentsOf: inURL) else { FileHandle.standardError.write("cannot read image\n".data(using:.utf8)!); exit(1) }

let request = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: src, options: [:])
do { try handler.perform([request]) } catch {
    FileHandle.standardError.write("vision failed: \(error)\n".data(using:.utf8)!); exit(1)
}
guard let result = request.results?.first else {
    FileHandle.standardError.write("no subject detected\n".data(using:.utf8)!); exit(3)
}
// prefer the single most prominent instance when several are found
let instances: IndexSet = result.allInstances.count > 1
    ? IndexSet(integer: result.allInstances.first!)
    : result.allInstances
do {
    let buf = try result.generateMaskedImage(ofInstances: instances, from: handler, croppedToInstancesExtent: true)
    let ci = CIImage(cvPixelBuffer: buf)
    let ctx = CIContext()
    guard let cg = ctx.createCGImage(ci, from: ci.extent) else { exit(1) }
    let rep = NSBitmapImageRep(cgImage: cg)
    guard let png = rep.representation(using: .png, properties: [:]) else { exit(1) }
    try png.write(to: outURL)
    print("ok \(cg.width)x\(cg.height)")
} catch {
    FileHandle.standardError.write("mask failed: \(error)\n".data(using:.utf8)!); exit(1)
}
