import SwiftUI

/// Today's meal plan section showing Breakfast, Lunch, and Dinner
struct TodayPlanSection: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Section Title
            VStack(alignment: .leading, spacing: 4) {
                Text("Today's Plan")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                
                Text("3 meals planned")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
            }
            
            // Meals Grid
            VStack(spacing: 12) {
                MealCard(
                    type: "Breakfast",
                    icon: "sun.max.fill",
                    recipeName: "Scrambled Eggs & Toast",
                    calories: 420,
                    time: "7:30 AM"
                )
                
                MealCard(
                    type: "Lunch",
                    icon: "sun.max.fill",
                    recipeName: "Grilled Chicken Salad",
                    calories: 580,
                    time: "12:30 PM"
                )
                
                MealCard(
                    type: "Dinner",
                    icon: "sunset.fill",
                    recipeName: "Baked Salmon & Vegetables",
                    calories: 650,
                    time: "7:00 PM"
                )
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.white)
    }
}

/// Individual meal card component
struct MealCard: View {
    let type: String
    let icon: String
    let recipeName: String
    let calories: Int
    let time: String
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            Image(systemName: icon)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(KaloTheme.mint)
                .frame(width: 32, height: 32)
                .background(KaloTheme.mint.opacity(0.1))
                .cornerRadius(8)
            
            // Content
            VStack(alignment: .leading, spacing: 2) {
                Text(type)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
                
                Text(recipeName)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                    .lineLimit(1)
            }
            
            Spacer()
            
            // Calories & Time
            VStack(alignment: .trailing, spacing: 2) {
                Text("\(calories) kcal")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(KaloTheme.mint)
                
                Text(time)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.secondary)
            }
        }
        .padding(12)
        .background(Color.gray.opacity(0.15))
        .cornerRadius(12)
    }
}

#Preview {
    TodayPlanSection()
}
