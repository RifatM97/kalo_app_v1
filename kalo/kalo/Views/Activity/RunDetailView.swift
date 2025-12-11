import SwiftUI

struct RunHistoryView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject var viewModel = ActivityViewModel()
    @State private var selectedRun: RunDetail?
    @State private var showDetail = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.gray.opacity(0.15)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // MARK: - Header
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Run History")
                                .font(.system(size: 24, weight: .bold))
                                .foregroundColor(KaloTheme.text)
                            
                            if !viewModel.recentRuns.isEmpty {
                                Text("\(viewModel.recentRuns.count) runs")
                                    .font(.system(size: 12, weight: .medium))
                                    .foregroundColor(.secondary)
                            }
                        }
                        
                        Spacer()
                        
                        Button(action: { dismiss() }) {
                            Image(systemName: "xmark.circle.fill")
                                .font(.system(size: 24))
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(16)
                    .background(Color.white)
                    
                    if viewModel.recentRuns.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "figure.run")
                                .font(.system(size: 48))
                                .foregroundColor(.secondary)
                            
                            Text("No runs yet")
                                .font(.system(size: 18, weight: .semibold))
                                .foregroundColor(KaloTheme.text)
                            
                            Text("Start a run to see your activity here")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.secondary)
                        }
                        .frame(maxHeight: .infinity)
                        .frame(maxWidth: .infinity)
                    } else {
                        ScrollView {
                            VStack(spacing: 8) {
                                ForEach(viewModel.recentRuns) { run in
                                    NavigationLink(destination: RunDetailView(runId: run.id)) {
                                        RunCard(run: run) {
                                            selectedRun = run
                                            showDetail = true
                                        }
                                    }
                                }
                            }
                            .padding(16)
                        }
                    }
                }
            }
            .onAppear {
                Task {
                    await viewModel.fetchRecentRuns(limit: 100)
                }
            }
        }
    }
}

struct RunDetailView: View {
    @Environment(\.dismiss) var dismiss
    let runId: String
    
    @State private var run: RunDetail?
    @State private var isLoading = true
    @State private var error: String?
    
    var body: some View {
        ZStack {
            Color.gray.opacity(0.15)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // MARK: - Header
                HStack {
                    Text("Run Details")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(KaloTheme.text)
                    
                    Spacer()
                    
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.secondary)
                    }
                }
                .padding(16)
                .background(Color.white)
                
                if isLoading {
                    VStack {
                        ProgressView()
                            .frame(maxHeight: .infinity)
                    }
                } else if let run = run {
                    ScrollView {
                        VStack(spacing: 16) {
                            // MARK: - Main Stats
                            VStack(spacing: 16) {
                                // Distance - big number
                                VStack(spacing: 4) {
                                    Text("Distance")
                                        .font(.system(size: 12, weight: .medium))
                                        .foregroundColor(.secondary)
                                    
                                    Text(ActivityViewModel.formatDistance(run.distance_m))
                                        .font(.system(size: 42, weight: .bold))
                                        .foregroundColor(KaloTheme.mint)
                                }
                                .frame(maxWidth: .infinity)
                                
                                Divider()
                                
                                // Stats grid
                                HStack(spacing: 12) {
                                    StatItem(
                                        label: "Duration",
                                        value: ActivityViewModel.formatTime(run.duration_s),
                                        icon: "clock.fill"
                                    )
                                    
                                    StatItem(
                                        label: "Avg Pace",
                                        value: ActivityViewModel.formatPace(run.avg_pace_s_per_km),
                                        icon: "bolt.fill"
                                    )
                                    
                                    if let calories = run.calories_burned {
                                        StatItem(
                                            label: "Calories",
                                            value: String(calories),
                                            icon: "flame.fill"
                                        )
                                    }
                                }
                            }
                            .padding(16)
                            .background(Color.white)
                            .cornerRadius(16)
                            
                            // MARK: - Route Map (Placeholder)
                            VStack(spacing: 12) {
                                Text("Route Map")
                                    .font(.system(size: 16, weight: .semibold))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                
                                ZStack {
                                    Color.gray.opacity(0.2)
                                    
                                    VStack(spacing: 8) {
                                        Image(systemName: "map")
                                            .font(.system(size: 36))
                                            .foregroundColor(.secondary)
                                        
                                        Text("Map coming soon")
                                            .font(.system(size: 12, weight: .medium))
                                            .foregroundColor(.secondary)
                                    }
                                }
                                .frame(height: 200)
                                .cornerRadius(12)
                            }
                            .padding(16)
                            .background(Color.white)
                            .cornerRadius(16)
                            
                            // MARK: - Details
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Run Details")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(KaloTheme.text)
                                
                                DetailRow(label: "Date", value: formatDate(run.started_at))
                                DetailRow(label: "Time", value: formatTime(run.started_at))
                                
                                if let elevation = run.elevation_gain_m {
                                    DetailRow(label: "Elevation", value: String(format: "%.0f m", elevation))
                                }
                                
                                DetailRow(label: "Route Points", value: String(run.route_points.count))
                            }
                            .padding(16)
                            .background(Color.white)
                            .cornerRadius(16)
                            
                            Spacer(minLength: 20)
                        }
                        .padding(16)
                    }
                } else if let error = error {
                    VStack(spacing: 12) {
                        Image(systemName: "exclamationmark.circle")
                            .font(.system(size: 48))
                            .foregroundColor(.red)
                        
                        Text("Error")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(KaloTheme.text)
                        
                        Text(error)
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxHeight: .infinity)
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .navigationBarBackButtonHidden(true)
        .onAppear {
            Task {
                let viewModel = ActivityViewModel()
                if let run = await viewModel.fetchRunDetail(runId: runId) {
                    self.run = run
                    isLoading = false
                } else {
                    error = viewModel.error ?? "Failed to load run"
                    isLoading = false
                }
            }
        }
    }
    
    private func formatDate(_ isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: isoString) {
            let dateFormatter = DateFormatter()
            dateFormatter.dateStyle = .medium
            return dateFormatter.string(from: date)
        }
        return isoString
    }
    
    private func formatTime(_ isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: isoString) {
            let timeFormatter = DateFormatter()
            timeFormatter.timeStyle = .short
            return timeFormatter.string(from: date)
        }
        return isoString
    }
}

struct DetailRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(KaloTheme.text)
        }
        .padding(.vertical, 8)
    }
}

#Preview {
    RunHistoryView()
}
