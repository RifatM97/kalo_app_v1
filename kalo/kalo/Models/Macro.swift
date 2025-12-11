import Foundation

struct Macro: Codable {
    let protein: Double    // grams
    let carbs: Double      // grams
    let fat: Double        // grams
    
    var totalCalories: Double {
        (protein * 4) + (carbs * 4) + (fat * 9)
    }
}
