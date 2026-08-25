import AppKit
import CoreImage
import Foundation

let arguments = CommandLine.arguments
guard arguments.count == 3, let data = arguments[1].data(using: .utf8) else { fatalError("Usage: generate_qr URL OUTPUT.png") }
let filter = CIFilter.qrCodeGenerator()
filter.message = data
filter.correctionLevel = "M"
guard let qr = filter.outputImage else { fatalError("Could not generate QR") }
let quietZone: CGFloat = 4
let expanded = qr.extent.insetBy(dx: -quietZone, dy: -quietZone)
let white = CIImage(color: .white).cropped(to: expanded)
let positioned = qr.transformed(by: CGAffineTransform(translationX: quietZone, y: quietZone))
let combined = positioned.composited(over: white)
let scale: CGFloat = 12
let output = combined.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
let context = CIContext(options: [.useSoftwareRenderer: false])
guard let image = context.createCGImage(output, from: output.extent),
      let png = NSBitmapImageRep(cgImage: image).representation(using: .png) else { fatalError("Could not encode PNG") }
try png.write(to: URL(fileURLWithPath: arguments[2]))
