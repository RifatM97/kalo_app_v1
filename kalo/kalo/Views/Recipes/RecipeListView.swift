import SwiftUI

struct RecipeListView: View {
    @State var recipeVM: RecipeViewModel
    @State private var showImportSheet = false
    @State private var showExtractionSheet = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                // Search Bar
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.secondary)
                    
                    TextField("Search recipes", text: $recipeVM.searchText)
                        .textFieldStyle(.plain)
                }
                .padding(10)
                .background(Color(white: 0.97))
                .cornerRadius(10)
                .padding(.horizontal, KaloTheme.padding)
                
                // Import Button
                HStack(spacing: 10) {
                    Button(action: { showImportSheet = true }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                            Text("Import Recipe")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(10)
                        .background(KaloTheme.mint.opacity(0.1))
                        .foregroundColor(KaloTheme.mint)
                        .cornerRadius(10)
                        .fontWeight(.semibold)
                    }
                    
                    Button(action: { showExtractionSheet = true }) {
                        HStack {
                            Image(systemName: "video.badge.plus")
                            Text("Extract")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(10)
                        .background(KaloTheme.mint.opacity(0.1))
                        .foregroundColor(KaloTheme.mint)
                        .cornerRadius(10)
                        .fontWeight(.semibold)
                    }
                }
                .padding(.horizontal, KaloTheme.padding)
                
                // Recipe List
                if recipeVM.filteredRecipes.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "book.pages")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        
                        Text("No Recipes")
                            .font(.system(size: 18, weight: .semibold))
                        
                        Text("Import or create your first recipe")
                            .font(.system(size: 14))
                            .foregroundColor(.secondary)
                    }
                    .frame(maxHeight: .infinity)
                    .padding(KaloTheme.padding)
                } else {
                    ScrollView {
                        VStack(spacing: 12) {
                            ForEach(recipeVM.filteredRecipes) { recipe in
                                NavigationLink(destination: RecipeDetailView(recipe: recipe)) {
                                    RecipeListItemView(recipe: recipe)
                                }
                            }
                        }
                        .padding(KaloTheme.padding)
                    }
                }
                
                Spacer()
            }
            .navigationTitle("Recipes")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .sheet(isPresented: $showImportSheet) {
                ImportRecipeView()
            }
            .sheet(isPresented: $showExtractionSheet) {
                RecipeExtractionView()
            }
        }
    }
}

struct RecipeListItemView: View {
    let recipe: Recipe
    
    var body: some View {
        HStack(spacing: 12) {
            // Image Placeholder
            RoundedRectangle(cornerRadius: 12)
                .fill(KaloTheme.mint.opacity(0.15))
                .frame(width: 80, height: 80)
                .overlay {
                    Image(systemName: "fork.knife")
                        .font(.system(size: 24))
                        .foregroundColor(KaloTheme.mint)
                }
            
            // Content
            VStack(alignment: .leading, spacing: 6) {
                Text(recipe.title)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.kaloText)
                
                HStack(spacing: 16) {
                    Label(String(format: "%.0f", recipe.calories), systemImage: "flame.fill")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.orange)
                    
                    Label(String(format: "%.0fg", recipe.macros.protein), systemImage: "p.circle.fill")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.kaloMint)
                }
                
                Text(recipe.ingredients.prefix(2).map { $0.name }.joined(separator: ", ") + (recipe.ingredients.count > 2 ? "..." : ""))
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
                .font(.system(size: 14, weight: .semibold))
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
    }
}

#Preview {
    RecipeListView(recipeVM: RecipeViewModel())
}
