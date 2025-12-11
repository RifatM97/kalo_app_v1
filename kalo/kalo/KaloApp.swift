import SwiftUI

@main
struct KaloApp: App {
    @State private var authVM = AuthViewModel()
    
    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(authVM)
                .preferredColorScheme(.light)
        }
    }
}
