import SwiftUI

struct ActivityView: View {
    @StateObject var viewModel = ActivityViewModel()
    @State private var showRunTracking = false
    @State private var showHistory = false
    @State private var showChallenges = false
    @State private var showAICoach = false
    @State private var selectedPeriod: String = "week"
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.gray.opacity(0.15)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) {
                        // MARK: - Header
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Activity")
                                .font(.system(size: 32, weight: .bold))
                                .foregroundColor(KaloTheme.text)
                            
                            Text("Track your runs and progress")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 16)
                        .padding(.top, 8)
                        
                        // MARK: - Quick Actions
                        VStack(spacing: 12) {
                            // AI Coach Card
                            Button(action: { showAICoach = true }) {
                                HStack(spacing: 12) {
                                    Image(systemName: "sparkles")
                                        .font(.system(size: 18, weight: .bold))
                                        .foregroundColor(.white)
                                        .frame(width: 40, height: 40)
                                        .background(
                                            LinearGradient(
                                                colors: [KaloTheme.mint, KaloTheme.mint.opacity(0.7)],
                                                startPoint: .topLeading,
                                                endPoint: .bottomTrailing
                                            )
                                        )
                                        .cornerRadius(10)
                                    
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text("Ask AI Coach")
                                            .font(.system(size: 15, weight: .semibold))
                                            .foregroundColor(KaloTheme.text)
                                        Text("Get personalized training advice")
                                            .font(.system(size: 12, weight: .medium))
                                            .foregroundColor(.secondary)
                                    }
                                    
                                    Spacer()
                                    
                                    Image(systemName: "chevron.right")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundColor(.secondary)
                                }
                                .padding(12)
                                .background(Color.white)
                                .cornerRadius(12)
                                .shadow(color: Color.black.opacity(0.05), radius: 4, y: 2)
                            }
                            
                            HStack(spacing: 12) {
                                Button(action: { showRunTracking = true }) {
                                    Label("Start Run", systemImage: "play.circle.fill")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .padding(.vertical, 12)
                                        .background(KaloTheme.mint)
                                        .cornerRadius(12)
                                }
                                
                                Button(action: { showHistory = true }) {
                                    Label("History", systemImage: "list.bullet")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundColor(KaloTheme.mint)
                                        .frame(maxWidth: .infinity)
                                        .padding(.vertical, 12)
                                        .background(Color.white)
                                        .cornerRadius(12)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                                .stroke(KaloTheme.mint.opacity(0.3), lineWidth: 1)
                                        )
                                }
                                
                                Button(action: { showChallenges = true }) {
                                    Label("Challenges", systemImage: "flag.fill")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundColor(KaloTheme.mint)
                                        .frame(maxWidth: .infinity)
                                        .padding(.vertical, 12)
                                        .background(Color.white)
                                        .cornerRadius(12)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                                .stroke(KaloTheme.mint.opacity(0.3), lineWidth: 1)
                                        )
                                }
                            }
                        }
                        .padding(.horizontal, 16)
                        
                        // MARK: - Period Selector
                        Picker("Period", selection: $selectedPeriod) {
                            Text("Week").tag("week")
                            Text("Month").tag("month")
                            Text("Year").tag("year")
                        }
                        .pickerStyle(.segmented)
                        .padding(.horizontal, 16)
                        .onChange(of: selectedPeriod) {
                            Task {
                                await viewModel.fetchSummary(period: selectedPeriod)
                                await viewModel.fetchHeatmap(period: selectedPeriod)
                            }
                        }
                        
                        // MARK: - Summary Card
                        if let summary = viewModel.summary {
                            SummarySectionCard(summary: summary, period: selectedPeriod)
                                .padding(.horizontal, 16)
                        } else {
                            PlaceholderCard(height: 180)
                                .padding(.horizontal, 16)
                        }
                        
                        // MARK: - Heatmap
                        if let heatmap = viewModel.heatmapData {
                            HeatmapView(data: heatmap.data, period: heatmap.period)
                                .padding(.horizontal, 16)
                        } else {
                            PlaceholderCard(height: 200)
                                .padding(.horizontal, 16)
                        }
                        
                        // MARK: - Recent Runs Section
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                Text("Recent Runs")
                                    .font(.system(size: 18, weight: .bold))
                                    .foregroundColor(KaloTheme.text)
                                
                                Spacer()
                                
                                if !viewModel.recentRuns.isEmpty {
                                    NavigationLink(destination: RunHistoryView()) {
                                        Text("See All")
                                            .font(.system(size: 12, weight: .semibold))
                                            .foregroundColor(KaloTheme.mint)
                                    }
                                }
                            }
                            
                            if viewModel.recentRuns.isEmpty {
                                VStack(spacing: 12) {
                                    Image(systemName: "figure.run")
                                        .font(.system(size: 48))
                                        .foregroundColor(.secondary)
                                    
                                    Text("No runs yet")
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundColor(KaloTheme.text)
                                    
                                    Text("Start your first run to see activity here")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.secondary)
                                        .multilineTextAlignment(.center)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(20)
                                .background(Color.gray.opacity(0.15))
                                .cornerRadius(16)
                            } else {
                                VStack(spacing: 8) {
                                    ForEach(viewModel.recentRuns.prefix(3)) { run in
                                        NavigationLink(destination: RunDetailView(runId: run.id)) {
                                            RunCard(run: run) {}
                                        }
                                    }
                                }
                            }
                        }
                        .padding(.horizontal, 16)
                        
                        // MARK: - Stats Card
                        if let stats = viewModel.allStats {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Personal Records")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(KaloTheme.text)
                                
                                HStack(spacing: 12) {
                                    if let fastest = stats.personal_records.fastest_pace_s_per_km {
                                        SummaryStatCard(
                                            label: "Fastest",
                                            value: ActivityViewModel.formatPace(fastest),
                                            icon: "bolt.fill",
                                            color: KaloTheme.mint
                                        )
                                    }
                                    
                                    if let longest = stats.personal_records.longest_distance_m {
                                        SummaryStatCard(
                                            label: "Longest",
                                            value: ActivityViewModel.formatDistance(longest),
                                            icon: "location.fill",
                                            color: KaloTheme.mint
                                        )
                                    }
                                }
                            }
                            .padding(.horizontal, 16)
                        }
                        
                        Spacer(minLength: 40)
                    }
                    .padding(.vertical, 16)
                }
                
                if viewModel.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.black.opacity(0.1))
                }
            }
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .sheet(isPresented: $showRunTracking) {
                RunTrackingView()
            }
            .sheet(isPresented: $showHistory) {
                RunHistoryView()
            }
            .sheet(isPresented: $showChallenges) {
                ChallengesListView()
            }
            .sheet(isPresented: $showAICoach) {
                ActivityAICoachSheet(
                    isPresented: $showAICoach,
                    activityContext: viewModel.getActivityContext()
                )
            }
            .onAppear {
                Task {
                    await viewModel.fetchSummary(period: selectedPeriod)
                    await viewModel.fetchHeatmap(period: selectedPeriod)
                    await viewModel.fetchRecentRuns()
                    await viewModel.fetchAllStats()
                }
            }
        }
    }
}

/// Placeholder card for loading state
struct PlaceholderCard: View {
    let height: CGFloat
    
    var body: some View {
        ZStack {
            Color.gray.opacity(0.15)
            
            ProgressView()
        }
        .frame(height: height)
        .cornerRadius(16)
    }
}

#Preview {
    ActivityView()
}
