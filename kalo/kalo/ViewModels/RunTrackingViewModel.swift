import Foundation

// MARK: - Response Models

struct StartRunResponse: Codable {
    let session_id: String
    let started_at: String
}

struct UpdateRunResponse: Codable {
    let elapsed_time_s: Int
    let current_pace: Double?
}

struct FinishRunResponse: Codable {
    let id: String
    let distance_m: Float
    let duration_s: Int
    let avg_pace_s_per_km: Float
    let calories_burned: Int
}

// MARK: - ViewModel

@MainActor
class RunTrackingViewModel: ObservableObject {
    @Published var sessionId: String?
    @Published var isRunning = false
    @Published var elapsedSeconds: Int = 0
    @Published var distance_m: Float = 0.0
    @Published var currentPace: Float?
    @Published var caloriesBurned: Int = 0
    @Published var error: String?
    @Published var isLoading = false
    @Published var finishedRun: FinishRunResponse?
    
    private var timer: Timer?
    private var updateTimer: Timer?
    private var startTime: Date?
    
    private let baseURL = URL(string: "http://localhost:8000/api/runs")!
    private let mockToken = "mock-token-12345"
    
    deinit {
        timer?.invalidate()
        updateTimer?.invalidate()
    }
    
    // MARK: - Public Methods
    
    func startRun() async {
        isLoading = true
        error = nil
        
        do {
            let response = try await startRemoteRun()
            sessionId = response.session_id
            isRunning = true
            startTime = Date()
            startTimers()
            isLoading = false
        } catch {
            self.error = "Failed to start run: \(error.localizedDescription)"
            isLoading = false
        }
    }
    
    func updateDistance(_ distance: Float) {
        distance_m = distance
    }
    
    func finishRun() async {
        guard let sessionId = sessionId else {
            error = "No active session"
            return
        }
        
        isLoading = true
        error = nil
        
        do {
            let response = try await finishRemoteRun(sessionId: sessionId)
            finishedRun = response
            isRunning = false
            stopTimers()
            resetState()
            isLoading = false
        } catch {
            self.error = "Failed to finish run: \(error.localizedDescription)"
            isLoading = false
        }
    }
    
    func cancelRun() {
        isRunning = false
        resetState()
        error = nil
    }
    
    // MARK: - Private Methods
    
    private func updateRunWithCurrentData() async {
        guard let sessionId = sessionId, isRunning else { return }
        
        do {
            let url = baseURL.appendingPathComponent(sessionId).appendingPathComponent("update")
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
            
            let payload: [String: Any] = [
                "distance_m": distance_m,
                "elapsed_time_s": elapsedSeconds
            ]
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                throw NSError(domain: "API Error", code: -1)
            }
            
            let updateResponse = try JSONDecoder().decode(UpdateRunResponse.self, from: data)
            currentPace = updateResponse.current_pace.flatMap { Float($0) }
        } catch {
            // Silently fail on update (don't interrupt run)
            print("Update error: \(error)")
        }
    }
    
    private func startRemoteRun() async throws -> StartRunResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("start"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "API Error", code: -1)
        }
        
        return try JSONDecoder().decode(StartRunResponse.self, from: data)
    }
    
    private func finishRemoteRun(sessionId: String) async throws -> FinishRunResponse {
        let url = baseURL.appendingPathComponent(sessionId).appendingPathComponent("finish")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(mockToken)", forHTTPHeaderField: "Authorization")
        
        let payload: [String: Any] = [
            "distance_m": distance_m,
            "elapsed_time_s": elapsedSeconds
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "API Error", code: -1)
        }
        
        return try JSONDecoder().decode(FinishRunResponse.self, from: data)
    }
    
    private func startTimers() {
        // Local timer: updates UI every second
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.elapsedSeconds += 1
                // Update calorie estimate: ~15 cal/min for moderate running
                self?.caloriesBurned = Int(Float((self?.elapsedSeconds ?? 0)) / 60.0 * 15.0)
            }
        }
        
        // Update timer: syncs with API every 10 seconds
        updateTimer = Timer.scheduledTimer(withTimeInterval: 10.0, repeats: true) { [weak self] _ in
            Task {
                await self?.updateRunWithCurrentData()
            }
        }
    }
    
    private func stopTimers() {
        timer?.invalidate()
        timer = nil
        updateTimer?.invalidate()
        updateTimer = nil
    }
    
    private func resetState() {
        sessionId = nil
        elapsedSeconds = 0
        distance_m = 0.0
        currentPace = nil
        caloriesBurned = 0
        startTime = nil
    }
}
