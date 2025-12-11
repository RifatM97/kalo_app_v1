import Foundation

struct Ingredient: Codable, Identifiable {
    let id: String
    let name: String
    let quantity: String
    let unit: String
    let calories: Double
    let macros: Macro
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case quantity
        case unit
        case calories
        case macros
    }
}
