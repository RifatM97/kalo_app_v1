import Foundation

// MARK: - Recipe Extraction Models
struct RecipeExtractionRequest: Codable {
    let url: String
}

struct RecipeExtractionResponse: Codable {
    let id: Int?
    let taskId: String?
    let title: String?
    let description: String?
    let ingredients: [RecipeIngredient]?
    let steps: [RecipeStep]?
    let cookTimeMinutes: Int?
    let prepTimeMinutes: Int?
    let difficulty: String?
    let servings: Int?
    let macros: MacroInfo?
    let status: String?
    let error: String?
    
    enum CodingKeys: String, CodingKey {
        case id, title, description, ingredients, steps, difficulty, servings, macros, status, error
        case taskId = "task_id"
        case cookTimeMinutes = "cook_time_minutes"
        case prepTimeMinutes = "prep_time_minutes"
    }
}

struct RecipeIngredient: Codable, Identifiable {
    let id = UUID()
    var name: String
    var quantity: Double?
    var unit: String?
    
    enum CodingKeys: String, CodingKey {
        case name, quantity, unit
    }
}

struct RecipeStep: Codable, Identifiable {
    let id = UUID()
    var step: Int
    var instruction: String
    
    enum CodingKeys: String, CodingKey {
        case step, instruction
    }
}

struct MacroInfo: Codable {
    var calories: Double?
    var protein: Double?
    var carbs: Double?
    var fat: Double?
}
