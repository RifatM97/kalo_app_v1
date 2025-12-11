import SwiftUI
struct RecipesCarousel: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Section Title
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Your Recipes")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(KaloTheme.text)
                    
                    Text("12 saved recipes")
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                NavigationLink(destination: Text("Recipes View")) {
                    Text("See All")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(KaloTheme.mint)
                }
            }
            .padding(.horizontal, 16)
            
            // Horizontal Scrolling List
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(0..<5, id: \.self) { index in
                        RecipeCardCompact(index: index)
                    }
                }
                .padding(.horizontal, 16)
            }
        }
    }
}

/// Compact recipe card for carousel
struct RecipeCardCompact: View {
    let index: Int
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Image placeholder
            RoundedRectangle(cornerRadius: 12)
                .fill(
                    LinearGradient(
                        gradient: Gradient(colors: [
                            KaloTheme.mint.opacity(0.3),
                            KaloTheme.mint.opacity(0.1)
                        ]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .frame(height: 120)
                .overlay(
                    Image(systemName: "photo.fill")
                        .font(.system(size: 24))
                        .foregroundColor(KaloTheme.mint.opacity(0.5))
                )
            
            // Recipe info
            VStack(alignment: .leading, spacing: 4) {
                Text("Recipe \(index + 1)")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                    .lineLimit(1)
                
                HStack(spacing: 6) {
                    Label("High Protein", systemImage: "flame.fill")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.orange)
                }
                
                HStack(spacing: 4) {
                    Text("420 kcal")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(KaloTheme.mint)
                }
            }
        }
        .frame(width: 140)
        .padding(8)
        .background(Color.white)
        .cornerRadius(14)
        .shadow(color: Color.black.opacity(0.05), radius: 8, x: 0, y: 2)
    }
}

#Preview {
    RecipesCarousel()
        .background(Color(.gray))
}


