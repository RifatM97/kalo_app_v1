import Foundation
import Combine
import UIKit

@MainActor
@Observable
final class RecipeExtractionViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var videoURL: String = ""
    var extractedRecipe: RecipeExtractionResponse?
    var isExtracting = false
    var extractionProgress: String = ""
    var taskId: String?
    
    private let networkService = NetworkingService.shared
    @ObservationIgnored private var statusCheckTimer: Timer?
    
    func extractRecipe(from url: String) async {
        guard !url.trimmingCharacters(in: .whitespaces).isEmpty else {
            error = "Please enter a video URL"
            return
        }
        
        isLoading = true
        isExtracting = true
        error = nil
        extractionProgress = "Starting extraction..."
        extractedRecipe = nil
        defer { isLoading = false }
        
        do {
            let request = RecipeExtractionRequest(url: url)
            let response: RecipeExtractionResponse = try await networkService.post(
                "ai/extract-recipe",
                body: request,
                as: RecipeExtractionResponse.self
            )
            
            extractedRecipe = response
            
            if response.status == "processing" {
                taskId = response.taskId
                startStatusPolling()
            } else {
                extractionProgress = "Extraction complete!"
                isExtracting = false
            }
        } catch {
            self.error = "Failed to extract recipe: \(error.localizedDescription)"
            isExtracting = false
        }
    }
    
    func extractFromImage(_ image: UIImage) async {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            error = "Failed to convert image to JPEG"
            return
        }
        
        isLoading = true
        isExtracting = true
        error = nil
        extractionProgress = "Analyzing image..."
        extractedRecipe = nil
        defer {
            isLoading = false
            isExtracting = false
        }
        
        do {
            let response: RecipeExtractionResponse = try await networkService.uploadFile(
                "recipes/extract-from-image",
                fileData: imageData,
                fileName: "recipe.jpg",
                mimeType: "image/jpeg",
                as: RecipeExtractionResponse.self
            )
            
            extractedRecipe = response
            extractionProgress = "Extraction complete!"
        } catch {
            self.error = "Failed to extract recipe from image: \(error.localizedDescription)"
        }
    }
    
    func extractFromVideo(_ videoURL: URL) async {
        guard let videoData = try? Data(contentsOf: videoURL) else {
            error = "Failed to read video file"
            return
        }
        
        isLoading = true
        isExtracting = true
        error = nil
        extractionProgress = "Processing video..."
        extractedRecipe = nil
        defer {
            isLoading = false
            isExtracting = false
        }
        
        do {
            let response: RecipeExtractionResponse = try await networkService.uploadFile(
                "recipes/extract-from-video",
                fileData: videoData,
                fileName: "recipe.mp4",
                mimeType: "video/mp4",
                as: RecipeExtractionResponse.self
            )
            
            extractedRecipe = response
            extractionProgress = "Extraction complete!"
        } catch {
            self.error = "Failed to extract recipe from video: \(error.localizedDescription)"
        }
    }
    
    private func startStatusPolling() {
        // Ensure any existing timer is invalidated
        statusCheckTimer?.invalidate()

        // Timer callback is safe because the class is @MainActor and Timer runs on main thread
        // nonisolated(unsafe) on statusCheckTimer allows Timer to work without Sendable issues
        statusCheckTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            Task {
                await self.checkExtractionStatus()
            }
        }
    }
    
    private func checkExtractionStatus() async {
        guard let taskId = taskId else { return }
        
        do {
            extractionProgress = "Processing video..."
            
            // In a real scenario, you'd call a status endpoint
            // For now, we'll simulate it
            let response: RecipeExtractionResponse = try await networkService.get(
                "ai/extract-recipe/\(taskId)/status",
                as: RecipeExtractionResponse.self
            )
            
            if response.status == "completed" || response.title != nil {
                extractedRecipe = response
                statusCheckTimer?.invalidate()
                statusCheckTimer = nil
                extractionProgress = "Extraction complete!"
                isExtracting = false
            } else if response.status == "failed" {
                error = response.error ?? "Extraction failed"
                statusCheckTimer?.invalidate()
                statusCheckTimer = nil
                isExtracting = false
            }
        } catch {
            // Continue polling
        }
    }
    
    func clearData() {
        videoURL = ""
        extractedRecipe = nil
        error = nil
        taskId = nil
        statusCheckTimer?.invalidate()
        statusCheckTimer = nil
    }
    
    deinit {
        statusCheckTimer?.invalidate()
    }
}

