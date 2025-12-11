import Foundation

struct Recipe: Codable, Identifiable {
    let id: String
    let title: String
    let description: String?
    let ingredients: [Ingredient]
    let steps: [String]
    let calories: Double
    let macros: Macro
    let thumbnailURL: String?
    let source: String?  // e.g., "tiktok", "instagram"
    let createdAt: Date?
    
    enum CodingKeys: String, CodingKey {
        case id
        case title
        case description
        case ingredients
        case steps
        case calories
        case macros
        case thumbnailURL = "thumbnail_url"
        case source
        case createdAt = "created_at"
    }
    
    static let mock = Recipe(
        id: "mock-1",
        title: "Grilled Chicken Pasta",
        description: "Delicious Italian pasta with grilled chicken",
        ingredients: [
            Ingredient(id: "ing-1", name: "Chicken Breast", quantity: "200", unit: "g", calories: 165, macros: Macro(protein: 31, carbs: 0, fat: 3.6)),
            Ingredient(id: "ing-2", name: "Pasta", quantity: "100", unit: "g", calories: 131, macros: Macro(protein: 5, carbs: 25, fat: 1.1)),
            Ingredient(id: "ing-3", name: "Olive Oil", quantity: "1", unit: "tbsp", calories: 119, macros: Macro(protein: 0, carbs: 0, fat: 14))
        ],
        steps: [
            "Preheat grill to 400°F",
            "Season chicken with salt and pepper",
            "Grill chicken for 6-8 minutes per side",
            "Cook pasta according to package directions",
            "Toss pasta with olive oil and grilled chicken",
            "Serve hot"
        ],
        calories: 415,
        macros: Macro(protein: 36, carbs: 25, fat: 18.7),
        thumbnailURL: nil,
        source: "user",
        createdAt: Date()
    )
}
