import Foundation
import Combine

@Observable
final class HomeViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var todayCalories: Double = 1850
    var dailyCalorieGoal: Double = 2000
    var todayMacros: Macro = Macro(protein: 120, carbs: 180, fat: 65)
    var todayMeals: [MealSlot] = []
    
    private let networkService = NetworkingService.shared
    
    init() {
        // Initialize with mock data
        let today = Date()
        todayMeals = [
            MealSlot(id: UUID().uuidString, mealType: .breakfast, recipe: nil, date: today),
            MealSlot(id: UUID().uuidString, mealType: .lunch, recipe: nil, date: today),
            MealSlot(id: UUID().uuidString, mealType: .dinner, recipe: nil, date: today)
        ]
    }
    
    // MARK: - Load Today's Data
    @MainActor
    func loadTodayData() {
        // Data already initialized in init()
    }
    
    // MARK: - Calculate Progress
    var calorieProgress: Double {
        min(todayCalories / dailyCalorieGoal, 1.0)
    }
    
    var remainingCalories: Double {
        max(dailyCalorieGoal - todayCalories, 0)
    }
    
    var macroProgress: (protein: Double, carbs: Double, fat: Double) {
        return (
            protein: todayMacros.protein / 150,
            carbs: todayMacros.carbs / 250,
            fat: todayMacros.fat / 70
        )
    }
    
    // MARK: - Refresh Data
    @MainActor
    func refreshData() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            try await Task.sleep(nanoseconds: 500_000_000)
            loadTodayData()
        } catch {
            self.error = "Failed to refresh data"
        }
    }
}
