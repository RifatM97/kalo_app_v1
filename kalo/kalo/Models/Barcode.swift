import Foundation

// MARK: - Barcode Models
struct BarcodeNutrition: Codable {
    let barcode: String
    let productName: String?
    let calories: Double?
    let protein: Double?
    let carbs: Double?
    let fat: Double?
    let servingSize: String?
}

struct NutritionBarcodeRequest: Codable {
    let barcode: String
}

struct NutritionBarcodeResponse: Codable {
    let barcode: String
    let productName: String?
    let calories: Double?
    let protein: Double?
    let carbs: Double?
    let fat: Double?
    let servingSize: String?
}
