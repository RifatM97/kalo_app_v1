Kalo iOS App (SwiftUI)

Quick start

1. Open Xcode 15+.
2. Create a new project (App) and select SwiftUI lifecycle. Name it `Kalo`.
3. In the project navigator, replace the default files with the `ios/Kalo` folder files in this repository. Alternatively, add the `ios/Kalo` folder as a group and include the Swift files.
4. Ensure the deployment target is iOS 17+ for SwiftData/@Observable features (scaffold uses modern APIs).
5. Run the app in Simulator (iPhone 14 or similar).

Notes
- Networking is stubbed/mocked for demo. `NetworkingService` is ready for async/await calls.
- Tokens are saved to Keychain via `KeychainHelper`.
- Saved recipes are stored in-memory in this scaffold. Replace with SwiftData or CoreData for persistence.

Files of interest
- `KaloApp.swift` – App entry
- `Config.swift` – API base URL & theme
- `Services/NetworkingService.swift` – Networking
- `Services/KeychainHelper.swift` – Token storage
- `Views/` – All SwiftUI views
- `ViewModels/` – ObservableObjects for screens
