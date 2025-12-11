import Foundation
import Combine

struct GroceryItem: Identifiable, Codable {
    let id: String
    let name: String
    let quantity: String
    let unit: String
    var isChecked: Bool = false
    
    init(id: String = UUID().uuidString, name: String, quantity: String, unit: String) {
        self.id = id
        self.name = name
        self.quantity = quantity
        self.unit = unit
    }
}

@Observable
final class GroceryViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var groceryItems: [GroceryItem] = []
    var searchText: String = ""
    
    private let networkService = NetworkingService.shared
    
    var filteredItems: [GroceryItem] {
        if searchText.isEmpty {
            return groceryItems
        }
        return groceryItems.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }
    
    var checkedCount: Int {
        groceryItems.filter { $0.isChecked }.count
    }
    
    // MARK: - Generate Grocery List
    @MainActor
    func generateFromPlanner(_ plannerDays: [PlannerDay]) {
        var ingredientDict: [String: GroceryItem] = [:]
        
        for day in plannerDays {
            for slot in day.slots {
                if let recipe = slot.recipe {
                    for ingredient in recipe.ingredients {
                        let key = ingredient.name.lowercased()
                        if let existing = ingredientDict[key] {
                            // Combine quantities (for simplicity, just mark as needed)
                            ingredientDict[key] = GroceryItem(
                                name: existing.name,
                                quantity: existing.quantity,
                                unit: existing.unit
                            )
                        } else {
                            ingredientDict[key] = GroceryItem(
                                name: ingredient.name,
                                quantity: ingredient.quantity,
                                unit: ingredient.unit
                            )
                        }
                    }
                }
            }
        }
        
        groceryItems = Array(ingredientDict.values).sorted { $0.name < $1.name }
    }
    
    // MARK: - Toggle Item
    @MainActor
    func toggleItem(_ item: GroceryItem) {
        if let index = groceryItems.firstIndex(where: { $0.id == item.id }) {
            groceryItems[index].isChecked.toggle()
        }
    }
    
    // MARK: - Remove Item
    @MainActor
    func removeItem(_ item: GroceryItem) {
        groceryItems.removeAll { $0.id == item.id }
    }
    
    // MARK: - Add Item
    @MainActor
    func addItem(name: String, quantity: String, unit: String) {
        let newItem = GroceryItem(name: name, quantity: quantity, unit: unit)
        groceryItems.append(newItem)
    }
    
    // MARK: - Clear Checked
    @MainActor
    func clearCheckedItems() {
        groceryItems.removeAll { $0.isChecked }
    }
}
