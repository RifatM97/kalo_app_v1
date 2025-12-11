import SwiftUI

struct LoginView: View {
    @Environment(AuthViewModel.self) var authVM
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Text("Welcome Back")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.kaloText)
                    
                    Text("Sign in to continue")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.top, 20)
                
                // Form
                VStack(spacing: 12) {
                    TextField("Email", text: Binding(get: { authVM.email }, set: { authVM.email = $0 }))
                        .keyboardType(.emailAddress)
                        .textContentType(.emailAddress)
                        .autocorrectionDisabled()
                        .padding(12)
                        .background(Color(white: 0.97))
                        .cornerRadius(10)
                    
                    SecureField("Password", text: Binding(get: { authVM.password }, set: { authVM.password = $0 }))
                        .textContentType(.password)
                        .padding(12)
                        .background(Color(white: 0.97))
                        .cornerRadius(10)
                }
                
                // Error Message
                if let error = authVM.error {
                    Text(error)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.red)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(12)
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(8)
                }
                
                // Login Button
                Button(action: {
                    Task {
                        await authVM.login()
                    }
                }) {
                    if authVM.isLoading {
                        HStack {
                            ProgressView()
                                .tint(.white)
                            Text("Signing In...")
                        }
                    } else {
                        Text("Log In")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding(12)
                .background(KaloTheme.mint)
                .foregroundColor(.white)
                .cornerRadius(KaloTheme.buttonCornerRadius)
                .disabled(authVM.isLoading || authVM.email.isEmpty || authVM.password.isEmpty)
                
                Spacer()
                
                // Sign Up Link
                HStack {
                    Text("Don't have an account?")
                        .foregroundColor(.secondary)
                    NavigationLink("Sign Up", destination: SignupView())
                        .foregroundColor(.kaloMint)
                        .fontWeight(.semibold)
                }
            }
            .padding(KaloTheme.padding)
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
        }
    }
}

#Preview {
    LoginView()
        .environment(AuthViewModel())
}
