import SwiftUI

struct RootView: View {
    @Environment(AuthViewModel.self) var authVM
    
    var body: some View {
        Group {
            if authVM.isAuthenticated {
                TabRootView()
            } else {
                SplashView()
            }
        }
        .animation(.easeInOut(duration: 0.3), value: authVM.isAuthenticated)
    }
}

struct SplashView: View {
    @Environment(AuthViewModel.self) var authVM
    @State private var showLogin = false
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Spacer()
                
                // Logo & Title
                VStack(spacing: 12) {
                    Text("🥗")
                        .font(.system(size: 64))
                    
                    Text("Kalo")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(.kaloMint)
                    
                    Text("Your Personal Nutrition & Fitness Companion")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                
                Spacer()
                
                // Buttons
                VStack(spacing: 12) {
                    NavigationLink(destination: LoginView()) {
                        Text("Log In")
                            .frame(maxWidth: .infinity)
                            .padding(12)
                            .background(KaloTheme.mint)
                            .foregroundColor(.white)
                            .cornerRadius(KaloTheme.buttonCornerRadius)
                            .fontWeight(.semibold)
                    }
                    
                    NavigationLink(destination: SignupView()) {
                        Text("Create Account")
                            .frame(maxWidth: .infinity)
                            .padding(12)
                            .foregroundColor(KaloTheme.mint)
                            .overlay(
                                RoundedRectangle(cornerRadius: KaloTheme.buttonCornerRadius)
                                    .stroke(KaloTheme.mint, lineWidth: 1.5)
                            )
                            .fontWeight(.semibold)
                    }
                }
                .padding(.bottom, 20)
            }
            .padding(KaloTheme.padding)
            .background(Color.white)
        }
    }
}

#Preview {
    RootView()
        .environment(AuthViewModel())
}
