import Foundation
import Combine

@Observable
final class AIChatViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var messages: [AIMessage] = []
    var currentInput: String = ""
    var showTypingIndicator = false
    var sessionId: String?
    var coachMode: Bool = false
    
    private let networkService = NetworkingService.shared
    
    init(coachMode: Bool = false) {
        self.coachMode = coachMode
        // Add initial greeting message
        let greeting = coachMode 
            ? "Hi! I'm your Kalo AI Coach. I'm here to help you reach your fitness and nutrition goals. What would you like to work on today?"
            : "Hi! I'm your Kalo AI assistant. Ask me anything about nutrition, recipes, workouts, or meal planning."
        
        messages.append(AIMessage(
            content: greeting,
            isUserMessage: false
        ))
    }
    
    @MainActor
    func sendMessage(_ text: String, context: ChatContext? = nil) async {
        guard !text.trimmingCharacters(in: .whitespaces).isEmpty else { return }
        
        let userMessage = AIMessage(content: text, isUserMessage: true)
        messages.append(userMessage)
        currentInput = ""
        
        isLoading = true
        showTypingIndicator = true
        error = nil
        defer { 
            isLoading = false
            showTypingIndicator = false
        }
        
        do {
            let request = AIChatRequest(
                message: text,
                sessionId: sessionId,
                coachMode: coachMode,
                context: context
            )
            
            let response: AIChatResponse = try await networkService.post(
                "ai/chat",
                body: request,
                as: AIChatResponse.self
            )
            
            // Save session ID for continuity
            sessionId = response.sessionId
            
            let aiMessage = AIMessage(
                content: response.message,
                isUserMessage: false
            )
            messages.append(aiMessage)
        } catch {
            self.error = "Failed to get AI response: \(error.localizedDescription)"
            let errorMessage = AIMessage(
                content: "Sorry, I encountered an error. Please try again.",
                isUserMessage: false
            )
            messages.append(errorMessage)
        }
    }
    
    func clearMessages() {
        messages.removeAll()
        sessionId = nil
        
        let greeting = coachMode 
            ? "Hi! I'm your Kalo AI Coach. I'm here to help you reach your fitness and nutrition goals. What would you like to work on today?"
            : "Hi! I'm your Kalo AI assistant. Ask me anything about nutrition, recipes, workouts, or meal planning."
        
        messages.append(AIMessage(
            content: greeting,
            isUserMessage: false
        ))
    }
}
