import SwiftUI
import Foundation

// MARK: - Models for API Responses

struct RunSummary: Codable {
    let total_distance_m: Float
    let total_time_s: Int
    let number_of_runs: Int
    let average_pace_s_per_km: Float
    let total_calories: Int
    let per_day_breakdown: [DayBreakdown]
}

struct DayBreakdown: Codable {
    let date: String
    let distance_m: Float
    let time_s: Int
    let runs_count: Int
}

struct HeatmapResponse: Codable {
    let period: String
    let data: [HeatmapDay]
}

struct HeatmapDay: Codable {
    let date: String
    let distance_m: Float
    let time_s: Int
    let runs_count: Int
    let intensity: Float  // 0-1
}

struct RunDetail: Codable, Identifiable {
    let id: String
    let distance_m: Float
    let duration_s: Int
    let avg_pace_s_per_km: Float
    let calories_burned: Int?
    let elevation_gain_m: Float?
    let started_at: String
    let ended_at: String
    let route_points: [RoutePoint]
    let created_at: String
    let updated_at: String
}

struct RoutePoint: Codable {
    let lat: Float
    let lng: Float
    let timestamp: String?
}

struct AllRunStats: Codable {
    let total_distance_m: Float
    let total_time_s: Int
    let total_runs: Int
    let average_pace_s_per_km: Float
    let average_distance_m: Float
    let personal_records: PersonalRecords
}

struct PersonalRecords: Codable {
    let fastest_pace_s_per_km: Float?
    let longest_distance_m: Float?
    let longest_duration_s: Int?
}

struct Challenge: Codable, Identifiable {
    let id: String
    let title: String
    let description: String
    let challenge_type: String
    let target_value: Float
    let start_date: String
    let end_date: String
    let reward_points: Int
}

struct ChallengeDetail: Codable {
    let id: String
    let title: String
    let description: String
    let challenge_type: String
    let target_value: Float
    let start_date: String
    let end_date: String
    let reward_points: Int
    let user_progress: Float?
    let user_percentage: Float?
    let user_status: String?
    let days_remaining: Int
    let leaderboard: [LeaderboardEntry]
}

struct LeaderboardEntry: Codable {
    let user_id: String
    let username: String
    let current_progress: Float
    let percentage: Float
    let position: Int
    let status: String
}

// MARK: - ActivityViewModel

@MainActor
class ActivityViewModel: ObservableObject {
    @Published var summary: RunSummary?
    @Published var heatmapData: HeatmapResponse?
    @Published var allStats: AllRunStats?
    @Published var recentRuns: [RunDetail] = []
    @Published var challenges: [Challenge] = []
    
    @Published var isLoading = false
    @Published var error: String?
    @Published var selectedPeriod: String = "week"
    
    private let baseURL = URL(string: "http://localhost:8000/api")!
    
    // Mock token - replace with real auth
    private let mockToken = "mock-jwt-token"
    
    // MARK: - Fetch Summary
    
    func fetchSummary(period: String = "week") async {
        isLoading = true
        defer { isLoading = false }
        
        let url = baseURL.appendingPathComponent("runs/summary/stats")
            .appending(queryItems: [URLQueryItem(name: "period", value: period)])
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            summary = try JSONDecoder().decode(RunSummary.self, from: data)
            error = nil
        } catch {
            self.error = "Failed to fetch summary: \(error.localizedDescription)"
        }
    }
    
    // MARK: - Fetch Heatmap
    
    func fetchHeatmap(period: String = "month") async {
        isLoading = true
        defer { isLoading = false }
        
        let url = baseURL.appendingPathComponent("runs/heatmap/data")
            .appending(queryItems: [URLQueryItem(name: "period", value: period)])
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            heatmapData = try JSONDecoder().decode(HeatmapResponse.self, from: data)
            error = nil
        } catch {
            self.error = "Failed to fetch heatmap: \(error.localizedDescription)"
        }
    }
    
    // MARK: - Fetch All Stats
    
    func fetchAllStats() async {
        isLoading = true
        defer { isLoading = false }
        
        let url = baseURL.appendingPathComponent("runs/stats/all")
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            allStats = try JSONDecoder().decode(AllRunStats.self, from: data)
            error = nil
        } catch {
            self.error = "Failed to fetch stats: \(error.localizedDescription)"
        }
    }
    
    // MARK: - Fetch Recent Runs
    
    func fetchRecentRuns(limit: Int = 10) async {
        isLoading = true
        defer { isLoading = false }
        
        let url = baseURL.appendingPathComponent("runs")
            .appending(queryItems: [
                URLQueryItem(name: "limit", value: String(limit)),
                URLQueryItem(name: "offset", value: "0")
            ])
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            recentRuns = try JSONDecoder().decode([RunDetail].self, from: data)
            error = nil
        } catch {
            self.error = "Failed to fetch runs: \(error.localizedDescription)"
        }
    }
    
    // MARK: - Fetch Run Detail
    
    func fetchRunDetail(runId: String) async -> RunDetail? {
        let url = baseURL.appendingPathComponent("runs/\(runId)")
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let run = try JSONDecoder().decode(RunDetail.self, from: data)
            error = nil
            return run
        } catch {
            self.error = "Failed to fetch run: \(error.localizedDescription)"
            return nil
        }
    }
    
    // MARK: - Fetch Challenges
    
    func fetchChallenges() async {
        isLoading = true
        defer { isLoading = false }
        
        let url = baseURL.appendingPathComponent("challenges")
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            challenges = try JSONDecoder().decode([Challenge].self, from: data)
            error = nil
        } catch {
            self.error = "Failed to fetch challenges: \(error.localizedDescription)"
        }
    }
    
    // MARK: - Fetch Challenge Detail
    
    func fetchChallengeDetail(challengeId: String) async -> ChallengeDetail? {
        let url = baseURL.appendingPathComponent("challenges/\(challengeId)")
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let challenge = try JSONDecoder().decode(ChallengeDetail.self, from: data)
            error = nil
            return challenge
        } catch {
            self.error = "Failed to fetch challenge: \(error.localizedDescription)"
            return nil
        }
    }
    
    // MARK: - Join Challenge
    
    func joinChallenge(challengeId: String) async -> Bool {
        let url = baseURL.appendingPathComponent("challenges/\(challengeId)/join")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONEncoder().encode(["": ""])
        
        do {
            let (_, response) = try await URLSession.shared.data(for: request)
            if let httpResponse = response as? HTTPURLResponse, (200..<300).contains(httpResponse.statusCode) {
                error = nil
                return true
            }
            error = "Failed to join challenge"
            return false
        } catch {
            self.error = "Failed to join challenge: \(error.localizedDescription)"
            return false
        }
    }
    
    // MARK: - Format helpers
    
    static func formatDistance(_ meters: Float) -> String {
        let km = meters / 1000
        if km < 1 {
            return String(format: "%.0f m", meters)
        }
        return String(format: "%.2f km", km)
    }
    
    static func formatPace(_ secondsPerKm: Float) -> String {
        let minutes = Int(secondsPerKm) / 60
        let seconds = Int(secondsPerKm) % 60
        return String(format: "%d:%02d /km", minutes, seconds)
    }
    
    static func formatTime(_ seconds: Int) -> String {
        let hours = seconds / 3600
        let minutes = (seconds % 3600) / 60
        let secs = seconds % 60
        
        if hours > 0 {
            return String(format: "%dh %dm %ds", hours, minutes, secs)
        } else if minutes > 0 {
            return String(format: "%dm %ds", minutes, secs)
        } else {
            return String(format: "%ds", secs)
        }
    }
    
    // MARK: - Get Activity Context for AI Coach
    
    func getActivityContext() -> String {
        var context = ""
        
        if let summary = summary {
            let totalDistance = Self.formatDistance(summary.total_distance_m)
            let avgPace = Self.formatPace(summary.average_pace_s_per_km)
            let totalTime = Self.formatTime(summary.total_time_s)
            
            context += "Recent Activity Summary (\(selectedPeriod)):\n"
            context += "- Total Runs: \(summary.number_of_runs)\n"
            context += "- Total Distance: \(totalDistance)\n"
            context += "- Total Time: \(totalTime)\n"
            context += "- Average Pace: \(avgPace)\n"
            context += "- Calories Burned: \(summary.total_calories)\n\n"
        }
        
        if let stats = allStats {
            context += "Personal Records:\n"
            if let fastest = stats.personal_records.fastest_pace_s_per_km {
                context += "- Fastest Pace: \(Self.formatPace(fastest))\n"
            }
            if let longest = stats.personal_records.longest_distance_m {
                context += "- Longest Distance: \(Self.formatDistance(longest))\n"
            }
            if let duration = stats.personal_records.longest_duration_s {
                context += "- Longest Duration: \(Self.formatTime(duration))\n"
            }
            context += "\n"
        }
        
        if !recentRuns.isEmpty {
            context += "Recent Runs:\n"
            for (index, run) in recentRuns.prefix(3).enumerated() {
                let distance = Self.formatDistance(run.distance_m)
                let pace = Self.formatPace(run.avg_pace_s_per_km)
                context += "\(index + 1). \(distance) at \(pace)\n"
            }
        }
        
        return context.isEmpty ? "No recent activity data available." : context
    }
}
