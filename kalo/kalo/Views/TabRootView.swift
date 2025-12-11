import SwiftUI

struct TabRootView: View {
    @State private var selectedTab: Int = 0
    @State private var homeVM = HomeViewModel()
    @State private var recipeVM = RecipeViewModel()
    @State private var plannerVM = PlannerViewModel()
    @State private var groceryVM = GroceryViewModel()
    @State private var workoutVM = WorkoutViewModel()
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Home Tab
            HomeView(homeVM: homeVM)
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)
            
            // Activity Tab
            ActivityView()
                .tabItem {
                    Label("Activity", systemImage: "figure.run")
                }
                .tag(1)
            
            // Social Tab (New)
            SocialView()
                .tabItem {
                    Label("Social", systemImage: "person.2.fill")
                }
                .tag(2)
            
            // Recipes Tab
            RecipeListView(recipeVM: recipeVM)
                .tabItem {
                    Label("Recipes", systemImage: "book.pages")
                }
                .tag(3)
            
            // Planner Tab
            PlannerView(plannerVM: plannerVM, recipeVM: recipeVM)
                .tabItem {
                    Label("Planner", systemImage: "calendar")
                }
                .tag(4)
            
            // Grocery Tab
            GroceryView(groceryVM: groceryVM, plannerVM: plannerVM)
                .tabItem {
                    Label("Grocery", systemImage: "cart")
                }
                .tag(5)
            
            // Workouts Tab
            WorkoutView(workoutVM: workoutVM)
                .tabItem {
                    Label("Workouts", systemImage: "figure.strengthtraining.traditional")
                }
                .tag(6)
        }
        .accentColor(KaloTheme.mint)
        .onAppear {
            configureTabBarAppearance()
        }
    }
    
    private func configureTabBarAppearance() {
        // SwiftUI-only TabView uses accentColor for styling
        // TabBar appearance is automatically applied via environment
    }
}

#Preview {
    TabRootView()
}
