import SwiftUI

struct ChallengesListView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject var viewModel = ActivityViewModel()
    @State private var selectedChallenge: ChallengeDetail?
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
                            Text("Challenges")
                                .font(.system(size: 24, weight: .bold))
                                .foregroundColor(KaloTheme.text)
                            
                            if !viewModel.challenges.isEmpty {
                                Text("\(viewModel.challenges.count) active")
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
                    
                    if viewModel.isLoading {
                        VStack {
                            ProgressView()
                                .frame(maxHeight: .infinity)
                        }
                    } else if viewModel.challenges.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "flag.circle")
                                .font(.system(size: 48))
                                .foregroundColor(.secondary)
                            
                            Text("No Challenges")
                                .font(.system(size: 18, weight: .semibold))
                                .foregroundColor(KaloTheme.text)
                            
                            Text("Check back soon for new challenges")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.secondary)
                        }
                        .frame(maxHeight: .infinity)
                        .frame(maxWidth: .infinity)
                    } else {
                        ScrollView {
                            VStack(spacing: 8) {
                                ForEach(viewModel.challenges) { challenge in
                                    NavigationLink(
                                        destination: ChallengeDetailView(challengeId: challenge.id)
                                    ) {
                                        ChallengeCardView(challenge: challenge)
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
                    await viewModel.fetchChallenges()
                }
            }
        }
    }
}

struct ChallengeCardView: View {
    let challenge: Challenge
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(challenge.title)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(KaloTheme.text)
                    
                    let typeText = challenge.challenge_type.replacingOccurrences(of: "_", with: " ").capitalized
                    Text(typeText)
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    HStack(spacing: 4) {
                        Image(systemName: "star.fill")
                            .font(.system(size: 11))
                        Text(String(challenge.reward_points))
                            .font(.system(size: 12, weight: .semibold))
                    }
                    .foregroundColor(KaloTheme.mint)
                    
                    Text("pts")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundColor(.secondary)
                }
            }
            
            if !challenge.description.isEmpty {
                Text(challenge.description)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
            
            HStack(spacing: 8) {
                Image(systemName: "target")
                    .font(.system(size: 11))
                    .foregroundColor(KaloTheme.mint)
                
                Text("Target: \(String(format: "%.0f", challenge.target_value))")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.secondary)
            }
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct ChallengeDetailView: View {
    @Environment(\.dismiss) var dismiss
    let challengeId: String
    
    @StateObject private var viewModel = ActivityViewModel()
    @State private var challenge: ChallengeDetail?
    @State private var isLoading = true
    @State private var error: String?
    @State private var isJoining = false
    @State private var joinedSuccessfully = false
    
    var body: some View {
        ZStack {
            Color.gray.opacity(0.15)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // MARK: - Header
                HStack {
                    Text("Challenge")
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
                } else if let challenge = challenge {
                    ScrollView {
                        VStack(spacing: 16) {
                            // MARK: - Title & Description
                            VStack(alignment: .leading, spacing: 8) {
                                Text(challenge.title)
                                    .font(.system(size: 24, weight: .bold))
                                    .foregroundColor(KaloTheme.text)
                                
                                if !challenge.description.isEmpty {
                                    Text(challenge.description)
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.secondary)
                                }
                                
                                HStack(spacing: 12) {
                                    let typeText = challenge.challenge_type.replacingOccurrences(of: "_", with: " ").capitalized
                                    Label(typeText, systemImage: "flag.fill")
                                    
                                    Spacer()
                                    
                                    HStack(spacing: 4) {
                                        Image(systemName: "star.fill")
                                        Text(String(challenge.reward_points))
                                    }
                                    .foregroundColor(KaloTheme.mint)
                                }
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(.secondary)
                            }
                            .padding(16)
                            .background(Color.white)
                            .cornerRadius(16)
                            
                            // MARK: - Progress
                            if let userProgress = challenge.user_progress, let userPercentage = challenge.user_percentage {
                                VStack(spacing: 12) {
                                    HStack {
                                        Text("Your Progress")
                                            .font(.system(size: 14, weight: .semibold))
                                            .foregroundColor(KaloTheme.text)
                                        
                                        Spacer()
                                        
                                        Text(String(format: "%.0f%%", min(userPercentage, 100)))
                                            .font(.system(size: 14, weight: .bold))
                                            .foregroundColor(KaloTheme.mint)
                                    }
                                    
                                    ProgressView(value: min(userPercentage, 100) / 100)
                                        .tint(KaloTheme.mint)
                                    
                                    HStack {
                                        Text("0")
                                            .font(.system(size: 11, weight: .medium))
                                            .foregroundColor(.secondary)
                                        
                                        Spacer()
                                        
                                        Text(String(format: "%.0f / %.0f", userProgress, challenge.target_value))
                                            .font(.system(size: 11, weight: .semibold))
                                            .foregroundColor(KaloTheme.text)
                                    }
                                }
                                .padding(16)
                                .background(Color.white)
                                .cornerRadius(16)
                            }
                            
                            // MARK: - Challenge Info
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Challenge Info")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(KaloTheme.text)
                                
                                HStack {
                                    Text("Days Remaining")
                                        .font(.system(size: 12, weight: .medium))
                                        .foregroundColor(.secondary)
                                    
                                    Spacer()
                                    
                                    Text(String(challenge.days_remaining))
                                        .font(.system(size: 14, weight: .bold))
                                        .foregroundColor(KaloTheme.mint)
                                }
                            }
                            .padding(16)
                            .background(Color.white)
                            .cornerRadius(16)
                            
                            // MARK: - Leaderboard
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Top 5 Leaderboard")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(KaloTheme.text)
                                
                                VStack(spacing: 8) {
                                    let leaderboardTop5 = Array(challenge.leaderboard.prefix(5))
                                    ForEach(Array(leaderboardTop5.enumerated()), id: \.offset) { index, entry in
                                        HStack {
                                            Text("\(entry.position).")
                                                .font(.system(size: 12, weight: .semibold))
                                                .foregroundColor(.secondary)
                                                .frame(width: 24)
                                            
                                            Text(entry.username)
                                                .font(.system(size: 12, weight: .medium))
                                                .foregroundColor(KaloTheme.text)
                                            
                                            Spacer()
                                            
                                            Text(String(format: "%.0f%%", entry.percentage))
                                                .font(.system(size: 12, weight: .semibold))
                                                .foregroundColor(KaloTheme.mint)
                                        }
                                        .padding(.vertical, 8)
                                        
                                        if index < leaderboardTop5.count - 1 {
                                            Divider()
                                        }
                                    }
                                }
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
            
            // MARK: - Action Button
            if let challenge = challenge, !isLoading {
                VStack {
                    Spacer()
                    
                    if challenge.user_status == "active" {
                        Button(action: {}) {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                Text("Joined Challenge")
                            }
                            .frame(maxWidth: .infinity)
                            .padding(14)
                            .background(KaloTheme.mint.opacity(0.2))
                            .foregroundColor(KaloTheme.mint)
                            .cornerRadius(12)
                            .font(.system(size: 14, weight: .semibold))
                        }
                        .disabled(true)
                    } else {
                        Button(action: {
                            Task {
                                isJoining = true
                                let success = await viewModel.joinChallenge(challengeId: challengeId)
                                isJoining = false
                                if success {
                                    joinedSuccessfully = true
                                }
                            }
                        }) {
                            HStack {
                                if isJoining {
                                    ProgressView()
                                        .tint(.white)
                                } else {
                                    Image(systemName: "plus.circle.fill")
                                }
                                Text(isJoining ? "Joining..." : "Join Challenge")
                            }
                            .frame(maxWidth: .infinity)
                            .padding(14)
                            .background(KaloTheme.mint)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                            .font(.system(size: 14, weight: .semibold))
                        }
                        .disabled(isJoining)
                    }
                }
                .padding(16)
                .background(
                    LinearGradient(
                        gradient: Gradient(colors: [Color.clear, Color.white]),
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
            }
        }
        .navigationBarBackButtonHidden(true)
        .alert("Success!", isPresented: $joinedSuccessfully) {
            Button("OK") { dismiss() }
        } message: {
            Text("You've joined the challenge! Start running to earn points.")
        }
        .onAppear {
            Task {
                if let challenge = await viewModel.fetchChallengeDetail(challengeId: challengeId) {
                    self.challenge = challenge
                    isLoading = false
                } else {
                    error = viewModel.error ?? "Failed to load challenge"
                    isLoading = false
                }
            }
        }
    }
}

#Preview {
    ChallengesListView()
}
