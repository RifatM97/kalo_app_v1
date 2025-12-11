import Foundation
import Combine

@Observable
final class PlannerViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var weekDays: [PlannerDay] = []
    var selectedDay: PlannerDay?
    var selectedSlot: MealSlot?
    
    private let networkService = NetworkingService.shared
    
    init() {
        weekDays = PlannerDay.mockWeek()
    }
    
    // MARK: - Load Weekly Plan
    @MainActor
    func loadWeek() {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        weekDays = PlannerDay.mockWeek()
    }
    
    // MARK: - Assign Recipe to Slot
    @MainActor
    func assignRecipe(_ recipe: Recipe, to slot: MealSlot, onDay day: PlannerDay) {
        guard let dayIndex = weekDays.firstIndex(where: { $0.id == day.id }) else { return }
        guard let slotIndex = weekDays[dayIndex].slots.firstIndex(where: { $0.id == slot.id }) else { return }
        
        var updatedSlot = weekDays[dayIndex].slots[slotIndex]
        updatedSlot.recipe = recipe
        weekDays[dayIndex].slots[slotIndex] = updatedSlot
    }
    
    // MARK: - Remove Recipe from Slot
    @MainActor
    func removeRecipe(from slot: MealSlot, onDay day: PlannerDay) {
        guard let dayIndex = weekDays.firstIndex(where: { $0.id == day.id }) else { return }
        guard let slotIndex = weekDays[dayIndex].slots.firstIndex(where: { $0.id == slot.id }) else { return }
        
        var updatedSlot = weekDays[dayIndex].slots[slotIndex]
        updatedSlot.recipe = nil
        weekDays[dayIndex].slots[slotIndex] = updatedSlot
    }
    
    // MARK: - Get Total Macros for Day
    func getTotalMacrosForDay(_ day: PlannerDay) -> Macro {
        let totalProtein = day.slots.compactMap { $0.recipe?.macros.protein }.reduce(0, +)
        let totalCarbs = day.slots.compactMap { $0.recipe?.macros.carbs }.reduce(0, +)
        let totalFat = day.slots.compactMap { $0.recipe?.macros.fat }.reduce(0, +)
        
        return Macro(protein: totalProtein, carbs: totalCarbs, fat: totalFat)
    }
    
    // MARK: - Get Total Calories for Day
    func getTotalCaloriesForDay(_ day: PlannerDay) -> Double {
        day.slots.compactMap { $0.recipe?.calories }.reduce(0, +)
    }
    
    // MARK: - Sync with Backend
    @MainActor
    func syncPlan() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            // Mock sync - in production, POST to /planner/update
            try await Task.sleep(nanoseconds: 500_000_000)
        } catch {
            self.error = "Failed to sync meal plan"
        }
    }
}
