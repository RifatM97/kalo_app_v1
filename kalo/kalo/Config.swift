import SwiftUI

// MARK: - API Configuration
enum APIConfig {
    // Environment-based URL selection
    enum Environment {
        case development  // http://localhost:8000 (simulator)
        case devRemote    // http://YOUR_MAC_IP:8000 (device testing)
        case staging      // Staging server
        case production   // Production server
    }
    
    // Change this to match your setup:
    // .development = iOS simulator talking to localhost:8000
    // .devRemote = Physical device talking to Mac IP (e.g., 192.168.1.100:8000)
    private static let activeEnvironment: Environment = .development
    
    private static func baseURLForEnvironment(_ env: Environment) -> URL {
        switch env {
        case .development:
            // For simulator: localhost works fine
            return URL(string: "http://localhost:8000")!
        case .devRemote:
            // For physical device testing: replace with your Mac's IP
            // Run: ifconfig | grep "inet " | grep -v 127.0.0.1
            // Then uncomment and modify below:
            // return URL(string: "http://192.168.x.x:8000")!
            return URL(string: "http://localhost:8000")!  // Fallback
        case .staging:
            return URL(string: "https://staging-api.kaloapp.com")!
        case .production:
            return URL(string: "https://api.kaloapp.com")!
        }
    }
    
    static let baseURL = baseURLForEnvironment(activeEnvironment)
    static let apiPrefix = "/api"  // Changed from /api/v1 to /api
    static let healthEndpoint = "/health"
    
    static var baseAPIURL: URL {
        baseURL.appendingPathComponent(apiPrefix)
    }
    
    // Timeout configuration
    static let requestTimeout: TimeInterval = 30
    static let connectionTimeout: TimeInterval = 10
}

// MARK: - Theme Configuration
enum KaloTheme {
    // Primary Colors
    static let mint = Color(red: 0.29, green: 0.89, blue: 0.76)  // #4BE3C1
    static let background = Color.white
    static let text = Color(red: 0.10, green: 0.10, blue: 0.10)  // #1A1A1A
    static let secondaryText = Color.gray
    static let divider = Color(red: 0.93, green: 0.93, blue: 0.93)
    
    // Component Styling
    static let cardCornerRadius: CGFloat = 16
    static let buttonCornerRadius: CGFloat = 12
    static let padding: CGFloat = 16
    
    // Shadow values (use with .shadow() modifier)
    static let shadowColor = Color.black.opacity(0.08)
    static let shadowRadius: CGFloat = 8
    static let shadowX: CGFloat = 0
    static let shadowY: CGFloat = 2
}

// MARK: - App Constants
enum AppConstants {
    static let appName = "Kalo"
    static let version = "1.0.0"
    static let keychainService = "com.kalo.app"
}
