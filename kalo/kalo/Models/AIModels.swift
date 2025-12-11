// File: AIModels.swift
import Foundation

// AI-Generated Meal Plan
struct AIGeneratedMealPlan: Codable {
    let id: UUID
    let week: [DayMealPlan]
    let weekSummary: WeeklySummary
    let groceryItems: [GroceryItemForPlan]
    
    struct DayMealPlan: Codable {
        let day: String
        let meals: [AIGeneratedMeal]
    }
    
    struct WeeklySummary: Codable {
        let avgCalories: Int
        let avgProtein: Int
        let avgCarbs: Int
        let avgFat: Int
    }
}

struct AIGeneratedMeal: Codable {
    let mealType: String
    let recipeName: String
    let estimatedCalories: Int
    let macros: MacroBreakdown
}

struct MacroBreakdown: Codable {
    let protein: Int
    let carbs: Int
    let fat: Int
}

struct GroceryItemForPlan: Codable {
    let item: String
    let quantity: Double
    let unit: String
}

// AI-Generated Workout Plan
struct AIGeneratedWorkoutPlan: Codable {
    let title: String
    let weeks: [WorkoutWeek]
    let progressionNotes: String
}

struct WorkoutWeek: Codable {
    let week: Int
    let workouts: [WorkoutSession]
    let progression: String
}

struct WorkoutSession: Codable {
    let day: String
    let type: String
    let exercises: [WorkoutExercise]
    let totalDurationMinutes: Int
}

struct WorkoutExercise: Codable {
    let name: String
    let sets: Int
    let reps: Int
    let weight: String
    let restSeconds: Int
    let notes: String
}

// AI Insights
struct AIInsight: Codable {
    let id: UUID
    let title: String
    let description: String
    let recommendation: String
    let impact: String // high, medium, low
    let type: String // nutrition, workout, consistency
}

struct InsightReport: Codable {
    let insights: [AIInsight]
    let strengths: [String]
    let areasForImprovement: [String]
    let generatedAt: Date
}

// Running/GPS Data
struct GPSRun: Codable {
    let id: UUID
    let distance: Double // km
    let duration: TimeInterval
    let pace: Double // min/km
    let caloriesBurned: Int
    let coordinates: [GPSPoint]
    let elevationGain: Double?
    let completedAt: Date
}

struct GPSPoint: Codable {
    let latitude: Double
    let longitude: Double
    let altitude: Double?
}

// Note: SocialPost is now defined in SocialModels.swift to avoid ambiguity

// Challenge
struct HealthChallenge: Codable {
    let id: UUID
    let title: String
    let description: String
    let challengeType: String // steps, calories, workout, nutrition
    let startDate: Date
    let endDate: Date
    let targetValue: Double
    let rewardPoints: Int
    let currentProgress: Double?
    let status: String? // active, completed, failed
}

struct ChallengeProof: Codable {
    let id: UUID
    let proofType: String // photo, gps, data
    let proofUrl: URL
    let verified: Bool
    let submittedAt: Date
}
