import AVFoundation
import Foundation
import Combine

@Observable
final class BarcodeScannerViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var scannedCode: String?
    var isScanning = true
    
    private let networkService = NetworkingService.shared
    
    @MainActor
    func fetchNutritionData(for barcode: String) async -> NutritionBarcodeResponse? {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            let request = NutritionBarcodeRequest(barcode: barcode)
            let response: NutritionBarcodeResponse = try await networkService.post(
                "nutrition/barcode",
                body: request,
                as: NutritionBarcodeResponse.self
            )
            return response
        } catch {
            self.error = "Failed to fetch nutrition data: \(error.localizedDescription)"
            return nil
        }
    }
    
    func resetScanner() {
        scannedCode = nil
        isScanning = true
        error = nil
    }
}
