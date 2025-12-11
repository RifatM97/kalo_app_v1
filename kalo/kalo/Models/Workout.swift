import Foundation

struct Workout: Codable, Identifiable {
    let id: String
    let date: Date
    let exerciseName: String
    let sets: Int
    let reps: Int
    let weight: Double?  // in pounds
    let duration: Int?   // in minutes
    let notes: String?
    let userId: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case date
        case exerciseName = "exercise_name"
        case sets
        case reps
        case weight
        case duration
        case notes
        case userId = "user_id"
    }
    
    static let mockWorkouts: [Workout] = [
        Workout(id: "w1", date: Date().addingTimeInterval(-3600), exerciseName: "Bench Press", sets: 4, reps: 8, weight: 185, duration: 45, notes: "Great session", userId: "user1"),
        Workout(id: "w2", date: Date().addingTimeInterval(-7200), exerciseName: "Squats", sets: 4, reps: 10, weight: 225, duration: 50, notes: nil, userId: "user1"),
        Workout(id: "w3", date: Date().addingTimeInterval(-86400), exerciseName: "Deadlifts", sets: 3, reps: 5, weight: 315, duration: 40, notes: "PR!", userId: "user1")
    ]
}
