import SwiftUI
import AVFoundation
import Vision

// TODO: Barcode scanning temporarily disabled - requires UIKit which is not available in this build target
// Re-enable when building for a target that supports UIKit (iOS app, not SwiftUI preview only)

/*
struct BarcodeScannerView: UIViewControllerRepresentable {
    @Environment(\.dismiss) var dismiss
    var onBarcodeDetected: (String) -> Void
    
    func makeUIViewController(context: Context) -> BarcodeScannerViewController {
        let controller = BarcodeScannerViewController()
        controller.onBarcodeDetected = { barcode in
            onBarcodeDetected(barcode)
            dismiss()
        }
        return controller
    }
    
    func updateUIViewController(_ uiViewController: BarcodeScannerViewController, context: Context) {}
}

class BarcodeScannerViewController: UIViewController, AVCaptureVideoDataOutputSampleBufferDelegate {
    var onBarcodeDetected: ((String) -> Void)?
    
    private let captureSession = AVCaptureSession()
    private let videoDataOutput = AVCaptureVideoDataOutput()
    private let previewLayer = AVCaptureVideoPreviewLayer()
    private let queue = DispatchQueue(label: "barcode.scan.queue")
    private var isProcessing = false
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        view.backgroundColor = .black
        
        // Setup camera
        setupCamera()
        
        // Add close button
        let closeButton = UIButton(type: .system)
        closeButton.setTitle("Close", for: .normal)
        closeButton.tintColor = .white
        closeButton.backgroundColor = UIColor(red: 0.29, green: 0.89, blue: 0.76, alpha: 0.8)
        closeButton.layer.cornerRadius = 8
        closeButton.addTarget(self, action: #selector(closeScanner), for: .touchUpInside)
        closeButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(closeButton)
        
        NSLayoutConstraint.activate([
            closeButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            closeButton.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            closeButton.widthAnchor.constraint(equalToConstant: 70),
            closeButton.heightAnchor.constraint(equalToConstant: 40)
        ])
    }
    
    private func setupCamera() {
        guard let camera = AVCaptureDevice.default(for: .video) else {
            print("No camera available")
            return
        }
        
        do {
            try captureSession.addInput(AVCaptureDeviceInput(device: camera))
            
            videoDataOutput.setSampleBufferDelegate(self, queue: queue)
            videoDataOutput.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
            
            captureSession.addOutput(videoDataOutput)
            
            previewLayer.session = captureSession
            previewLayer.videoGravity = .resizeAspectFill
            view.layer.addSublayer(previewLayer)
            
            DispatchQueue.global(qos: .userInitiated).async {
                self.captureSession.startRunning()
            }
        } catch {
            print("Camera setup error: \(error)")
        }
    }
    
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        previewLayer.frame = view.bounds
    }
    
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard !isProcessing, let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        isProcessing = true
        
        let request = VNDetectBarcodesRequest { request, error in
            defer { self.isProcessing = false }
            
            guard let results = request.results as? [VNBarcodeObservation], !results.isEmpty else {
                return
            }
            
            for result in results {
                if let payload = result.payloadStringValue, !payload.isEmpty {
                    self.onBarcodeDetected?(payload)
                    return
                }
            }
        }
        
        request.symbologies = [.ean13, .upce]
        
        try? VNImageRequestHandler(cvPixelBuffer: pixelBuffer, options: [:]).perform([request])
    }
    
    @objc private func closeScanner() {
        captureSession.stopRunning()
        dismiss(animated: true)
    }
}
*/

// Placeholder stub for when barcode scanning is re-enabled
struct BarcodeScannerView: View {
    var body: some View {
        Text("Barcode scanning not available in current build")
            .foregroundColor(.secondary)
    }
}
