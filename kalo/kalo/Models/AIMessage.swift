import Foundation

struct AIMessage: Identifiable, Codable {
    let id: UUID
    let content: String
    let isUserMessage: Bool
    let timestamp: Date
    
    init(id: UUID = UUID(), content: String, isUserMessage: Bool, timestamp: Date = Date()) {
        self.id = id
        self.content = content
        self.isUserMessage = isUserMessage
        self.timestamp = timestamp
    }
}

// MARK: - Codable Types for API
struct AIChatRequest: Codable {
    let message: String
    let sessionId: String?
    let coachMode: Bool?
    let context: ChatContext?
    
    enum CodingKeys: String, CodingKey {
        case message
        case sessionId = "session_id"
        case coachMode = "coach_mode"
        case context
    }
}

struct ChatContext: Codable {
    let goals: String?
    let recentWorkouts: String?
    let stats: String?
    
    enum CodingKeys: String, CodingKey {
        case goals
        case recentWorkouts = "recent_workouts"
        case stats
    }
}

struct AIChatResponse: Codable {
    let message: String
    let sessionId: String
    let provider: String
    
    enum CodingKeys: String, CodingKey {
        case message
        case sessionId = "session_id"
        case provider
    }
}
