# 🍎 KALO iOS APP - RECIPE EXTRACTION INTEGRATION GUIDE

This guide explains how to integrate the recipe extraction pipeline with your iOS app.

---

## 📱 iOS IMPLEMENTATION

### 1. **API Client Setup**

```swift
// KaloAPI.swift
import Foundation

class KaloAPI {
    static let shared = KaloAPI()
    
    let baseURL = "http://localhost:8000"  // Development
    // let baseURL = "https://api.kalo.app"  // Production
    
    enum RecipeExtractionError: Error {
        case invalidURL
        case networkError(Error)
        case decodingError(Error)
        case taskNotFound
        case extractionFailed(String)
    }
    
    // MARK: - Recipe Extraction
    
    /// Start recipe extraction from video URL
    func startRecipeExtraction(videoURL: String) async throws -> String {
        let endpoint = "\(baseURL)/api/ai/extract-recipe"
        
        guard var urlComponents = URLComponents(string: endpoint) else {
            throw RecipeExtractionError.invalidURL
        }
        
        guard let url = urlComponents.url else {
            throw RecipeExtractionError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let payload: [String: String] = ["url": videoURL]
        request.httpBody = try JSONEncoder().encode(payload)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw RecipeExtractionError.networkError(NSError(domain: "HTTP", code: -1))
        }
        
        let result = try JSONDecoder().decode(RecipeExtractionResponse.self, from: data)
        return result.taskId ?? ""
    }
    
    /// Poll extraction status
    func getExtractionStatus(taskID: String) async throws -> RecipeExtractionResponse {
        let endpoint = "\(baseURL)/api/ai/extract-recipe/\(taskID)/status"
        
        guard let url = URL(string: endpoint) else {
            throw RecipeExtractionError.invalidURL
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw RecipeExtractionError.taskNotFound
        }
        
        let result = try JSONDecoder().decode(RecipeExtractionResponse.self, from: data)
        return result
    }
    
    /// Poll until completion
    func waitForExtraction(taskID: String, maxWaitSeconds: Int = 300) async throws -> RecipeExtractionResponse {
        let startTime = Date()
        let maxWait = TimeInterval(maxWaitSeconds)
        
        while Date().timeIntervalSince(startTime) < maxWait {
            let status = try await getExtractionStatus(taskID: taskID)
            
            switch status.status {
            case "completed":
                return status
            case "failed":
                throw RecipeExtractionError.extractionFailed(status.error ?? "Unknown error")
            case "processing":
                try await Task.sleep(nanoseconds: 2_000_000_000)  // 2 second delay
                continue
            default:
                throw RecipeExtractionError.extractionFailed("Unknown status: \(status.status)")
            }
        }
        
        throw RecipeExtractionError.extractionFailed("Extraction timeout after \(maxWaitSeconds) seconds")
    }
}

// MARK: - Data Models (Swift Codable)

struct RecipeExtractionResponse: Codable {
    let taskId: String?
    let status: String
    let title: String?
    let description: String?
    let ingredients: [RecipeIngredient]?
    let steps: [RecipeStep]?
    let cookTimeMinutes: Int?
    let prepTimeMinutes: Int?
    let difficulty: String?
    let servings: Int?
    let macros: MacroInfo?
    let error: String?
    
    enum CodingKeys: String, CodingKey {
        case taskId = "task_id"
        case status
        case title
        case description
        case ingredients
        case steps
        case cookTimeMinutes = "cook_time_minutes"
        case prepTimeMinutes = "prep_time_minutes"
        case difficulty
        case servings
        case macros
        case error
    }
}

struct RecipeIngredient: Codable {
    let name: String
    let quantity: Double?
    let unit: String?
}

struct RecipeStep: Codable {
    let step: Int
    let instruction: String
}

struct MacroInfo: Codable {
    let calories: Double?
    let protein: Double?
    let carbs: Double?
    let fat: Double?
}
```

### 2. **View Model Implementation**

```swift
// RecipeExtractionViewModel.swift
import Foundation

@MainActor
class RecipeExtractionViewModel: ObservableObject {
    @Published var isProcessing = false
    @Published var extractedRecipe: RecipeExtractionResponse?
    @Published var errorMessage: String?
    @Published var progress: Double = 0.0
    
    enum State {
        case idle
        case processing
        case completed(RecipeExtractionResponse)
        case failed(Error)
    }
    
    @Published var state: State = .idle
    
    private let api = KaloAPI.shared
    
    func extractRecipe(from videoURL: String) {
        Task {
            do {
                isProcessing = true
                errorMessage = nil
                
                // Step 1: Start extraction
                print("[Recipe] Starting extraction for: \(videoURL)")
                let taskID = try await api.startRecipeExtraction(videoURL: videoURL)
                print("[Recipe] Task ID: \(taskID)")
                
                // Step 2: Poll until completion (timeout: 5 minutes)
                print("[Recipe] Waiting for extraction...")
                progress = 0.2
                
                let recipe = try await api.waitForExtraction(taskID: taskID)
                print("[Recipe] Extraction complete: \(recipe.title ?? "Unknown")")
                
                // Step 3: Update UI
                self.extractedRecipe = recipe
                self.state = .completed(recipe)
                self.progress = 1.0
                isProcessing = false
                
            } catch {
                print("[Recipe] Error: \(error.localizedDescription)")
                errorMessage = error.localizedDescription
                state = .failed(error)
                isProcessing = false
            }
        }
    }
}
```

### 3. **UI View**

```swift
// RecipeExtractionView.swift
import SwiftUI

struct RecipeExtractionView: View {
    @StateObject private var viewModel = RecipeExtractionViewModel()
    @State private var selectedVideoURL = ""
    @State private var showingURLInput = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                Text("Extract Recipe from Video")
                    .font(.title2)
                    .fontWeight(.bold)
                
                // Input
                VStack(spacing: 12) {
                    TextField("Video URL", text: $selectedVideoURL)
                        .textFieldStyle(.roundedBorder)
                        .placeholder(when: selectedVideoURL.isEmpty) {
                            Text("Paste YouTube/TikTok URL").foregroundColor(.gray)
                        }
                    
                    Button(action: {
                        viewModel.extractRecipe(from: selectedVideoURL)
                    }) {
                        if viewModel.isProcessing {
                            HStack {
                                ProgressView()
                                    .progressViewStyle(.circular)
                                    .scaleEffect(0.8)
                                Text("Extracting...")
                            }
                        } else {
                            Text("Extract Recipe")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(selectedVideoURL.isEmpty || viewModel.isProcessing)
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                // Progress
                if viewModel.isProcessing {
                    ProgressView(value: viewModel.progress)
                        .tint(.blue)
                }
                
                // Results
                if let recipe = viewModel.extractedRecipe {
                    ScrollView {
                        RecipeResultView(recipe: recipe)
                    }
                }
                
                // Error
                if let error = viewModel.errorMessage {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: "exclamationmark.circle.fill")
                                .foregroundColor(.red)
                            Text("Error")
                                .fontWeight(.semibold)
                        }
                        Text(error)
                            .font(.caption)
                            .lineLimit(3)
                    }
                    .padding()
                    .background(Color(.systemRed).opacity(0.1))
                    .cornerRadius(8)
                }
                
                Spacer()
            }
            .padding()
            .navigationTitle("Import Recipe")
        }
    }
}

struct RecipeResultView: View {
    let recipe: RecipeExtractionResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Title
            Text(recipe.title ?? "Extracted Recipe")
                .font(.title2)
                .fontWeight(.bold)
            
            if let description = recipe.description {
                Text(description)
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
            
            Divider()
            
            // Meta
            HStack(spacing: 20) {
                if let prep = recipe.prepTimeMinutes {
                    VStack(alignment: .center) {
                        Image(systemName: "clock")
                        Text("\(prep)m")
                            .font(.caption)
                    }
                }
                
                if let cook = recipe.cookTimeMinutes {
                    VStack(alignment: .center) {
                        Image(systemName: "flame")
                        Text("\(cook)m")
                            .font(.caption)
                    }
                }
                
                if let servings = recipe.servings {
                    VStack(alignment: .center) {
                        Image(systemName: "person")
                        Text("\(servings)")
                            .font(.caption)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .center)
            
            Divider()
            
            // Macros
            if let macros = recipe.macros {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Nutrition")
                        .fontWeight(.semibold)
                    
                    HStack {
                        Text("Calories: \(Int(macros.calories ?? 0))")
                        Spacer()
                        Text("P: \(Int(macros.protein ?? 0))g | C: \(Int(macros.carbs ?? 0))g | F: \(Int(macros.fat ?? 0))g")
                            .font(.caption)
                    }
                }
            }
            
            // Ingredients
            if let ingredients = recipe.ingredients, !ingredients.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Ingredients")
                        .fontWeight(.semibold)
                    
                    ForEach(ingredients, id: \.name) { ingredient in
                        HStack {
                            Image(systemName: "circle.fill")
                                .font(.caption)
                            Text(ingredient.name)
                            Spacer()
                            if let quantity = ingredient.quantity {
                                Text("\(quantity, specifier: "%.1f") \(ingredient.unit ?? "")")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                        }
                    }
                }
            }
            
            // Steps
            if let steps = recipe.steps, !steps.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Instructions")
                        .fontWeight(.semibold)
                    
                    ForEach(steps, id: \.step) { step in
                        HStack(alignment: .top, spacing: 12) {
                            Text("\(step.step)")
                                .fontWeight(.semibold)
                                .foregroundColor(.blue)
                                .frame(width: 24)
                            Text(step.instruction)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

// Helper
extension View {
    func placeholder<Content: View>(when shouldShow: Bool, alignment: Alignment = .leading, @ViewBuilder placeholder: () -> Content) -> some View {
        ZStack(alignment: alignment) {
            placeholder().opacity(shouldShow ? 1 : 0)
            self
        }
    }
}
```

### 4. **Integration in App**

```swift
// In your navigation or tabbed interface
import SwiftUI

@main
struct KaloApp: App {
    var body: some Scene {
        WindowGroup {
            TabView {
                // Existing tabs...
                
                // New Recipe Extraction Tab
                RecipeExtractionView()
                    .tabItem {
                        Image(systemName: "fork.knife")
                        Text("Import Recipe")
                    }
            }
        }
    }
}
```

---

## 🔧 Backend Configuration

### Make sure your backend is running:

```bash
cd /Users/rifathossain/Desktop/kalo/kalo-backend

# Terminal 1: Start backend
/Users/rifathossain/Desktop/kalo/.venv/bin/python -m uvicorn main:app --reload

# Terminal 2: Start Celery worker
/Users/rifathossain/Desktop/kalo/.venv/bin/celery -A app.celery_app worker -l info

# Terminal 3 (optional): Start Redis
redis-server
```

---

## 🌐 Network Configuration

### **For Local Testing (Development)**
```swift
let baseURL = "http://localhost:8000"  // Local machine
let baseURL = "http://127.0.0.1:8000"  // Same machine
let baseURL = "http://YOUR_IP:8000"    // From another device
```

### **For Remote Testing**
```swift
let baseURL = "https://api.staging.kalo.app"
let baseURL = "https://api.kalo.app"  // Production
```

### **Get Your Local IP (for testing from simulator)**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Copy the IP that starts with 192.168 or 10.
```

---

## 📊 Testing Checklist

- [ ] Backend is running on port 8000
- [ ] Redis is running on port 6379
- [ ] OPENAI_API_KEY is set in .env
- [ ] iOS app can reach backend (test with curl)
- [ ] Video URL is valid (YouTube/TikTok)
- [ ] Task ID is returned from POST /extract-recipe
- [ ] Status polling returns correct state
- [ ] Recipe JSON matches Swift models
- [ ] Recipe displays correctly in UI

---

## 🐛 Debugging

### **Check Backend Health**
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","service":"kalo-api"}
```

### **Test Recipe Extraction**
```bash
curl -X POST http://localhost:8000/api/ai/extract-recipe \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/shorts/dQw4w9WgXcQ"}'
```

### **Check Extraction Status**
```bash
curl http://localhost:8000/api/ai/extract-recipe/TASK_ID/status
```

### **View iOS Logs**
```swift
// Add logging to your ViewModel
print("[Recipe] Task ID: \(taskID)")
print("[Recipe] Status: \(recipe.status)")
print("[Recipe] Title: \(recipe.title ?? "nil")")
```

---

## ✨ Next Features

- [ ] Save extracted recipes to local database
- [ ] Show extraction history
- [ ] Edit extracted recipes
- [ ] Share recipes with friends
- [ ] Rate recipe extraction accuracy
- [ ] Batch extraction from multiple URLs
- [ ] Custom macro targets per recipe

---

**Happy cooking! 🍳**
