import Foundation
import Combine

@Observable
final class RecipeViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var recipes: [Recipe] = [Recipe.mock]
    var selectedRecipe: Recipe?
    var searchText: String = ""
    
    private let networkService = NetworkingService.shared
    
    var filteredRecipes: [Recipe] {
        if searchText.isEmpty {
            return recipes
        }
        return recipes.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
    }
    
    init() {
        loadMockRecipes()
    }
    
    // MARK: - Load Recipes
    @MainActor
    func loadRecipes() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            // Mock endpoint - replace with actual in production
            try await Task.sleep(nanoseconds: 500_000_000)
            recipes = [Recipe.mock]
        } catch {
            self.error = "Failed to load recipes"
        }
    }
    
    // MARK: - Save Recipe
    @MainActor
    func saveRecipe(_ recipe: Recipe) {
        // In production, save to SwiftData/CoreData and sync with backend
        if !recipes.contains(where: { $0.id == recipe.id }) {
            recipes.insert(recipe, at: 0)
        }
    }
    
    // MARK: - Delete Recipe
    @MainActor
    func deleteRecipe(_ recipe: Recipe) {
        recipes.removeAll { $0.id == recipe.id }
    }
    
    // MARK: - Mock Data
    private func loadMockRecipes() {
        recipes = [
            Recipe.mock,
            Recipe(
                id: "mock-2",
                title: "Salmon Bowl",
                description: "Healthy salmon with vegetables",
                ingredients: [
                    Ingredient(id: "ing-4", name: "Salmon", quantity: "150", unit: "g", calories: 280, macros: Macro(protein: 25, carbs: 0, fat: 20)),
                    Ingredient(id: "ing-5", name: "Brown Rice", quantity: "100", unit: "g", calories: 111, macros: Macro(protein: 2.6, carbs: 23, fat: 0.9))
                ],
                steps: ["Cook salmon", "Cook rice", "Combine"],
                calories: 391,
                macros: Macro(protein: 27.6, carbs: 23, fat: 20.9),
                thumbnailURL: nil,
                source: "user",
                createdAt: Date().addingTimeInterval(-86400)
            )
        ]
    }
}
