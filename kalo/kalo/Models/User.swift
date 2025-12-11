import Foundation

struct User: Codable, Identifiable {
    let id: String
    let email: String
    let username: String
    let createdAt: Date?
    let updatedAt: Date?
    
    enum CodingKeys: String, CodingKey {
        case id
        case email
        case username
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

struct AuthRequest: Codable {
    let email: String
    let password: String
}

struct AuthResponse: Codable {
    let token: String
    let user: User
}
