import Foundation

enum MealType: String, Codable, CaseIterable {
    case breakfast
    case lunch
    case dinner
    
    var displayName: String {
        switch self {
        case .breakfast: return "Breakfast"
        case .lunch: return "Lunch"
        case .dinner: return "Dinner"
        }
    }
}

struct MealSlot: Codable, Identifiable {
    let id: String
    let mealType: MealType
    var recipe: Recipe?
    let date: Date?
    
    enum CodingKeys: String, CodingKey {
        case id
        case mealType = "meal_type"
        case recipe
        case date
    }
}

struct PlannerDay: Codable, Identifiable {
    let id: String
    let date: Date
    var slots: [MealSlot]
    
    static func mockWeek() -> [PlannerDay] {
        let today = Date()
        return (0..<7).map { offset in
            let date = Calendar.current.date(byAdding: .day, value: offset, to: today) ?? today
            return PlannerDay(
                id: UUID().uuidString,
                date: date,
                slots: [
                    MealSlot(id: UUID().uuidString, mealType: .breakfast, recipe: nil, date: date),
                    MealSlot(id: UUID().uuidString, mealType: .lunch, recipe: nil, date: date),
                    MealSlot(id: UUID().uuidString, mealType: .dinner, recipe: nil, date: date)
                ]
            )
        }
    }
}
