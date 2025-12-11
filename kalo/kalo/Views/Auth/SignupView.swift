import SwiftUI

struct SignupView: View {
    @Environment(AuthViewModel.self) var authVM
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        VStack(spacing: 24) {
            // Header
            VStack(spacing: 8) {
                Text("Create Account")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.kaloText)
                
                Text("Join the Kalo community")
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
                
                TextField("Username", text: Binding(get: { authVM.username }, set: { authVM.username = $0 }))
                    .textContentType(.username)
                    .autocorrectionDisabled()
                    .padding(12)
                    .background(Color(white: 0.97))
                    .cornerRadius(10)
                
                SecureField("Password", text: Binding(get: { authVM.password }, set: { authVM.password = $0 }))
                    .textContentType(.newPassword)
                    .padding(12)
                    .background(Color(white: 0.97))
                    .cornerRadius(10)
                
                SecureField("Confirm Password", text: Binding(get: { authVM.confirmPassword }, set: { authVM.confirmPassword = $0 }))
                    .textContentType(.newPassword)
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
            
            // Sign Up Button
            Button(action: {
                Task {
                    await authVM.signup()
                }
            }) {
                if authVM.isLoading {
                    HStack {
                        ProgressView()
                            .tint(.white)
                        Text("Creating Account...")
                    }
                } else {
                    Text("Sign Up")
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
            
            // Login Link
            HStack {
                Text("Already have an account?")
                    .foregroundColor(.secondary)
                Button("Log In") {
                    dismiss()
                }
                .foregroundColor(.kaloMint)
                .fontWeight(.semibold)
            }
        }
        .padding(KaloTheme.padding)
    }
}

#Preview {
    SignupView()
        .environment(AuthViewModel())
}
