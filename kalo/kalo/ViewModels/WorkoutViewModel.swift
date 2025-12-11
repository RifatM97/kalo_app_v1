import Foundation
import Combine

// MARK: - API Schemas
struct CreateWorkoutRequest: Codable {
    let type: String
    let name: String
    let duration: Int
    let exercises: [ExerciseEntry]
    let caloriesBurned: Int?
    
    enum CodingKeys: String, CodingKey {
        case type, name, duration, exercises
        case caloriesBurned = "calories_burned"
    }
}

struct ExerciseEntry: Codable {
    let name: String
    let sets: Int
    let reps: Int
    let weight: String?
}

struct WorkoutResponse: Codable {
    let id: String
    let userId: String
    let type: String
    let name: String
    let duration: Int
    let exercises: [ExerciseEntry]
    let caloriesBurned: Int?
    let completedAt: String
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, type, name, duration, exercises
        case userId = "user_id"
        case caloriesBurned = "calories_burned"
        case completedAt = "completed_at"
        case createdAt = "created_at"
    }
}

// MARK: - PR Tracking
struct ExercisePR {
    let exerciseName: String
    let maxWeight: Double
    let maxReps: Int
    let prDate: Date
    let totalVolume: Double
}

// MARK: - Workout ViewModel
@Observable
final class WorkoutViewModel {
    @ObservationIgnored @Published var isLoading = false
    @ObservationIgnored @Published var error: String?
    
    var workouts: [Workout] = []
    var selectedDate: Date = Date()
    var personalRecords: [String: ExercisePR] = [:]
    var newPRDetected: Bool = false
    var lastPRExercise: String = ""
    
    private let networkService = NetworkingService.shared
    
    init() {
        loadMockWorkouts()
        Task {
            calculatePersonalRecords()
        }
    }
    
    var workoutsForSelectedDate: [Workout] {
        workouts.filter { Calendar.current.isDate($0.date, inSameDayAs: selectedDate) }
    }
    
    /// Get total volume for an exercise
    func totalVolume(for exerciseName: String) -> Double {
        workouts
            .filter { $0.exerciseName.lowercased() == exerciseName.lowercased() }
            .reduce(0) { total, workout in
                let weight = workout.weight ?? 0
                let volume = Double(workout.sets * workout.reps) * weight
                return total + volume
            }
    }
    
    /// Get max weight for an exercise
    func maxWeight(for exerciseName: String) -> Double? {
        workouts
            .filter { $0.exerciseName.lowercased() == exerciseName.lowercased() }
            .compactMap { $0.weight }
            .max()
    }
    
    /// Get estimated 1RM using Epley Formula
    func estimatedOneRM(for exerciseName: String) -> Double? {
        guard let maxWeight = maxWeight(for: exerciseName) else { return nil }
        
        let maxRepsForWeight = workouts
            .filter { $0.exerciseName.lowercased() == exerciseName.lowercased() && $0.weight == maxWeight }
            .map { $0.reps }
            .max() ?? 1
        
        return maxWeight * (1 + Double(maxRepsForWeight) / 30)
    }
    
    /// Calculate all personal records
    private func calculatePersonalRecords() {
        var prs: [String: ExercisePR] = [:]
        
        let exerciseGroups = Dictionary(grouping: workouts) { $0.exerciseName }
        
        for (exerciseName, exerciseWorkouts) in exerciseGroups {
            if let maxWeightWorkout = exerciseWorkouts.max(by: { ($0.weight ?? 0) < ($1.weight ?? 0) }) {
                let maxReps = exerciseWorkouts
                    .filter { $0.weight == maxWeightWorkout.weight }
                    .map { $0.reps }
                    .max() ?? 1
                
                let totalVol = totalVolume(for: exerciseName)
                
                prs[exerciseName.lowercased()] = ExercisePR(
                    exerciseName: exerciseName,
                    maxWeight: maxWeightWorkout.weight ?? 0,
                    maxReps: maxReps,
                    prDate: maxWeightWorkout.date,
                    totalVolume: totalVol
                )
            }
        }
        
        DispatchQueue.main.async {
            self.personalRecords = prs
        }
    }
    
    /// Check if adding this workout creates a new PR
    func isNewPR(exerciseName: String, weight: Double?, reps: Int) -> Bool {
        guard let weight = weight else { return false }
        
        if let existing = personalRecords[exerciseName.lowercased()] {
            return weight > existing.maxWeight || (weight == existing.maxWeight && reps > existing.maxReps)
        }
        
        return true
    }
    
    /// Add workout
    @MainActor
    func addWorkout(exerciseName: String, sets: Int, reps: Int, weight: Double?, duration: Int?, notes: String?) {
        let workout = Workout(
            id: UUID().uuidString,
            date: Date(),
            exerciseName: exerciseName,
            sets: sets,
            reps: reps,
            weight: weight,
            duration: duration,
            notes: notes,
            userId: nil
        )
        workouts.insert(workout, at: 0)
        
        let isPR = isNewPR(exerciseName: exerciseName, weight: weight, reps: reps)
        if isPR {
            newPRDetected = true
            lastPRExercise = exerciseName
            HapticsService.shared.notification(.success)
        } else {
            HapticsService.shared.impact(.medium)
        }
        
        calculatePersonalRecords()
        
        Task {
            await logWorkoutToAPI(
                exerciseName: exerciseName,
                sets: sets,
                reps: reps,
                weight: weight,
                duration: duration,
                notes: notes
            )
        }
    }
    
    /// Log to API
    @MainActor
    private func logWorkoutToAPI(exerciseName: String, sets: Int, reps: Int, weight: Double?, duration: Int?, notes: String?) async {
        let request = CreateWorkoutRequest(
            type: "strength",
            name: exerciseName,
            duration: duration ?? 0,
            exercises: [ExerciseEntry(
                name: exerciseName,
                sets: sets,
                reps: reps,
                weight: weight.map { String(format: "%.0f lbs", $0) }
            )],
            caloriesBurned: nil
        )
        
        do {
            _ = try await networkService.post(
                "workouts",
                body: request,
                as: WorkoutResponse.self
            )
            HapticsService.shared.impact(.light)
        } catch {
            self.error = "Failed to save workout: \(error.localizedDescription)"
            HapticsService.shared.notification(.error)
        }
    }
    
    /// Load workouts
    @MainActor
    func loadWorkouts() async {
        isLoading = true
        error = nil
        defer { isLoading = false }
        
        do {
            let response: [WorkoutResponse] = try await networkService.get(
                "workouts",
                as: [WorkoutResponse].self
            )
            
            workouts = response.map { r in
                let exercise = r.exercises.first
                return Workout(
                    id: r.id,
                    date: ISO8601DateFormatter().date(from: r.completedAt) ?? Date(),
                    exerciseName: exercise?.name ?? r.name,
                    sets: exercise?.sets ?? 0,
                    reps: exercise?.reps ?? 0,
                    weight: exercise?.weight.flatMap { Double($0.filter { $0.isNumber || $0 == "." }) },
                    duration: r.duration,
                    notes: nil,
                    userId: r.userId
                )
            }
            
            calculatePersonalRecords()
        } catch {
            self.error = "Failed to load workouts"
            loadMockWorkouts()
        }
    }
    
    /// Delete workout
    @MainActor
    func deleteWorkout(_ workout: Workout) async {
        workouts.removeAll { $0.id == workout.id }
        calculatePersonalRecords()
        
        do {
            try await networkService.delete("workouts/\(workout.id)")
            HapticsService.shared.impact(.light)
        } catch {
            self.error = "Failed to delete workout"
        }
    }
    
    /// Load mock data
    private func loadMockWorkouts() {
        workouts = Workout.mockWorkouts
        Task {
            calculatePersonalRecords()
        }
    }
}
