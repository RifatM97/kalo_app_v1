import Foundation
import Combine

@Observable
final class AuthViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var isAuthenticated: Bool {
        KeychainHelper.shared.readToken() != nil
    }
    
    var email: String = ""
    var password: String = ""
    var confirmPassword: String = ""
    var username: String = ""
    
    private let networkService = NetworkingService.shared
    private let keychainHelper = KeychainHelper.shared
    
    // MARK: - Login
    @MainActor
    func login() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        _ = AuthRequest(email: email, password: password)
        
        do {
            // Mock API call - in production, replace with actual endpoint
            try await Task.sleep(nanoseconds: 800_000_000)
            
            // For demo, create a fake response
            let mockResponse = AuthResponse(
                token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock.token",
                user: User(
                    id: UUID().uuidString,
                    email: email,
                    username: email.split(separator: "@").first.map(String.init) ?? "User",
                    createdAt: Date(),
                    updatedAt: Date()
                )
            )
            
            keychainHelper.saveToken(mockResponse.token)
            email = ""
            password = ""
        } catch {
            self.error = "Login failed. Please try again."
        }
    }
    
    // MARK: - Signup
    @MainActor
    func signup() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        guard password == confirmPassword else {
            error = "Passwords do not match"
            return
        }
        
        guard password.count >= 6 else {
            error = "Password must be at least 6 characters"
            return
        }
        
        _ = AuthRequest(email: email, password: password)
        
        do {
            // Mock API call
            try await Task.sleep(nanoseconds: 800_000_000)
            
            let mockResponse = AuthResponse(
                token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock.token",
                user: User(
                    id: UUID().uuidString,
                    email: email,
                    username: username.isEmpty ? email.split(separator: "@").first.map(String.init) ?? "User" : username,
                    createdAt: Date(),
                    updatedAt: Date()
                )
            )
            
            keychainHelper.saveToken(mockResponse.token)
            email = ""
            password = ""
            confirmPassword = ""
            username = ""
        } catch {
            self.error = "Signup failed. Please try again."
        }
    }
    
    // MARK: - Logout
    @MainActor
    func logout() {
        keychainHelper.removeToken()
        email = ""
        password = ""
    }
}
