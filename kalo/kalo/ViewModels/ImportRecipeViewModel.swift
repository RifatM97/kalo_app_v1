import Foundation
import Combine

struct ExtractRecipeRequest: Codable {
    let url: String
}

struct ExtractRecipeResponse: Codable {
    let title: String
    let description: String?
    let ingredients: [IngredientDTO]
    let steps: [String]
    let calories: Double
    let macros: Macro
}

struct IngredientDTO: Codable {
    let name: String
    let quantity: String
    let unit: String
    let calories: Double
    let macros: Macro
}

@Observable
final class ImportRecipeViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var urlString: String = ""
    var importedRecipe: Recipe?
    
    private let networkService = NetworkingService.shared
    
    // MARK: - Extract Recipe from URL
    @MainActor
    func extractRecipe() async {
        guard !urlString.isEmpty else {
            error = "Please enter a URL"
            return
        }
        
        guard isValidURL(urlString) else {
            error = "Invalid URL format"
            return
        }
        
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        _ = ExtractRecipeRequest(url: urlString)
        
        do {
            // Mock API call - in production, replace with actual endpoint
            try await Task.sleep(nanoseconds: 1_000_000_000)
            
            // Create mock recipe from URL
            importedRecipe = Recipe.mock
            urlString = ""
        } catch {
            self.error = "Failed to extract recipe from URL"
        }
    }
    
    // MARK: - Save Imported Recipe
    @MainActor
    func saveRecipe() {
        // This would be called to save to RecipeViewModel
        importedRecipe = nil
    }
    
    // MARK: - Helper
    private func isValidURL(_ string: String) -> Bool {
        if let url = URL(string: string) {
            return url.scheme != nil && url.host != nil
        }
        return false
    }
}
