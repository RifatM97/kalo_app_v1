import SwiftUI

struct HomeView: View {
    @State var homeVM: HomeViewModel
    @State private var showImportSheet = false
    @State private var showChatBottomSheet = false
    
    var body: some View {
        ZStack {
            NavigationStack {
                ScrollView {
                    VStack(spacing: 20) {
                        // Header with greeting
                        HomeHeader()
                        
                        // Calorie summary card
                        CalorieSummaryCard(homeVM: homeVM)
                        
                        // Quick Actions
                        QuickActionsSection(
                            showImportSheet: $showImportSheet,
                            showChatBottomSheet: $showChatBottomSheet
                        )
                        
                        // Today's Plan
                        TodayPlanSection()
                        
                        // Your Recipes Carousel
                        RecipesCarousel()
                        
                        // Workouts & Challenges
                        WorkoutChallengesSection()
                        
                        // Bottom spacing
                        Spacer()
                            .frame(height: 20)
                    }
                    .padding(.horizontal, KaloTheme.padding)
                    .padding(.top, 12)
                    .padding(.bottom, 20)
                }
                .background(Color.gray.opacity(0.15))
                #if os(iOS)
                .navigationBarHidden(true)
                #endif
            }
            .sheet(isPresented: $showImportSheet) {
                ImportRecipeView()
            }
            
            // Chat Bottom Sheet
            if showChatBottomSheet {
                ChatBottomSheetView(isPresented: $showChatBottomSheet)
            }
        }
    }
}

// MARK: - Chat Entry Point

/// Chat entry point - pill button at bottom of home screen
struct ChatPillButton: View {
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: "sparkles")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text("Chat with Kalo")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.white)
                    
                    Text("Ask about your health & fitness")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.8))
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.white.opacity(0.8))
            }
            .frame(maxWidth: .infinity)
            .padding(14)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [
                        KaloTheme.mint,
                        KaloTheme.mint.opacity(0.8)
                    ]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(16)
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .shadow(color: KaloTheme.mint.opacity(0.3), radius: 8, x: 0, y: 4)
        }
    }
}

// MARK: - Calorie Summary

struct CalorieSummaryCard: View {
    let homeVM: HomeViewModel
    
    var body: some View {
        VStack(spacing: 16) {
            CalorieProgressSection(homeVM: homeVM)
            MacrosGridSection(homeVM: homeVM)
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(KaloTheme.cardCornerRadius)
        .shadow(color: Color.black.opacity(0.05), radius: 8, x: 0, y: 2)
    }
}

struct CalorieProgressSection: View {
    let homeVM: HomeViewModel
    
    var body: some View {
        VStack(spacing: 12) {
            CalorieHeader(homeVM: homeVM)
            CalorieProgressBar(homeVM: homeVM)
        }
    }
}

struct CalorieHeader: View {
    let homeVM: HomeViewModel
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Calorie Goal")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.secondary)
                
                HStack(alignment: .center, spacing: 4) {
                    Text(String(format: "%.0f", homeVM.todayCalories))
                        .font(.system(size: 32, weight: .bold))
                    Text("/ \(Int(homeVM.dailyCalorieGoal))")
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            VStack(alignment: .center, spacing: 4) {
                Text(String(format: "%.0f", homeVM.remainingCalories))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.kaloMint)
                Text("Left")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
            }
        }
    }
}

struct CalorieProgressBar: View {
    let homeVM: HomeViewModel
    
    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(Color.kaloDivider)
                
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(KaloTheme.mint)
                    .frame(width: geo.size.width * homeVM.calorieProgress)
            }
            .frame(height: 8)
        }
        .frame(height: 8)
    }
}

struct MacrosGridSection: View {
    let homeVM: HomeViewModel
    
    var body: some View {
        HStack(spacing: 12) {
            MacroCard(label: "Protein", value: String(format: "%.0f", homeVM.todayMacros.protein) + "g", color: .kaloMint)
            MacroCard(label: "Carbs", value: String(format: "%.0f", homeVM.todayMacros.carbs) + "g", color: Color.orange)
            MacroCard(label: "Fat", value: String(format: "%.0f", homeVM.todayMacros.fat) + "g", color: Color.red)
        }
    }
}

// MARK: - Quick Actions

struct QuickActionsSection: View {
    @Binding var showImportSheet: Bool
    @Binding var showChatBottomSheet: Bool
    
    var body: some View {
        VStack(spacing: 12) {
            Text("Quick Actions")
                .font(.system(size: 16, weight: .semibold))
                .frame(maxWidth: .infinity, alignment: .leading)
            
            // First row - AI Coach featured card
            AICoachFeatureCard(action: {
                withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
                    showChatBottomSheet = true
                }
            })
            
            // Second row - other actions
            HStack(spacing: 12) {
                ActionButton(
                    icon: "square.and.arrow.down",
                    label: "Import Recipe",
                    action: { showImportSheet = true }
                )
                ActionButton(
                    icon: "calendar",
                    label: "View Planner",
                    action: {}
                )
                ActionButton(
                    icon: "dumbbell",
                    label: "Log Workout",
                    action: {}
                )
            }
        }
    }
}

/// Featured AI Coach card with beautiful gradient design
struct AICoachFeatureCard: View {
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                // Icon with gradient background
                ZStack {
                    LinearGradient(
                        colors: [
                            KaloTheme.mint,
                            KaloTheme.mint.opacity(0.7)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    .frame(width: 56, height: 56)
                    .cornerRadius(16)
                    .shadow(color: KaloTheme.mint.opacity(0.3), radius: 8, y: 4)
                    
                    Image(systemName: "sparkles")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 6) {
                        Text("AI Coach")
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(KaloTheme.text)
                        
                        Image(systemName: "wand.and.stars")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(KaloTheme.mint)
                    }
                    
                    Text("Get personalized fitness & nutrition advice")
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(KaloTheme.mint.opacity(0.5))
            }
            .padding(16)
            .background(
                ZStack {
                    Color.white
                    
                    LinearGradient(
                        colors: [
                            KaloTheme.mint.opacity(0.05),
                            KaloTheme.mint.opacity(0.02)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                }
            )
            .cornerRadius(20)
            .shadow(color: Color.black.opacity(0.08), radius: 12, x: 0, y: 4)
            .overlay(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(
                        LinearGradient(
                            colors: [
                                KaloTheme.mint.opacity(0.2),
                                KaloTheme.mint.opacity(0.05)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 1
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Helper Views

struct MacroCard: View {
    let label: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Text(label)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
            Text(value)
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
        .padding(12)
        .background(color.opacity(0.08))
        .cornerRadius(12)
    }
}

struct ActionButton: View {
    let icon: String
    let label: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .semibold))
                Text(label)
                    .font(.system(size: 11, weight: .semibold))
            }
            .padding(12)
            .foregroundColor(KaloTheme.mint)
            .background(KaloTheme.mint.opacity(0.1))
            .cornerRadius(12)
        }
    }
}

#Preview {
    HomeView(homeVM: HomeViewModel())
}
