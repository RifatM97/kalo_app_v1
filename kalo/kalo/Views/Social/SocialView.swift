import SwiftUI

struct SocialView: View {
    @State private var viewModel = SocialViewModel()
    @State private var showCreatePost = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                // Background
                Color(.systemGroupedBackground)
                    .ignoresSafeArea()
                
                ScrollView {
                    LazyVStack(spacing: 16) {
                        // Header Section
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Community")
                                        .font(.system(size: 32, weight: .bold))
                                        .foregroundColor(KaloTheme.text)
                                    
                                    Text("Share your fitness journey")
                                        .font(.system(size: 15, weight: .medium))
                                        .foregroundColor(.secondary)
                                }
                                
                                Spacer()
                                
                                Button(action: { showCreatePost = true }) {
                                    Image(systemName: "plus.circle.fill")
                                        .font(.system(size: 32))
                                        .foregroundColor(KaloTheme.mint)
                                        .symbolRenderingMode(.hierarchical)
                                }
                            }
                            .padding(.horizontal, 20)
                            .padding(.top, 12)
                        }
                        
                        // Filter Tabs
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 12) {
                                FilterChip(title: "All", isSelected: viewModel.selectedFilter == .all) {
                                    viewModel.selectedFilter = .all
                                }
                                FilterChip(title: "Workouts", isSelected: viewModel.selectedFilter == .workouts) {
                                    viewModel.selectedFilter = .workouts
                                }
                                FilterChip(title: "Milestones", isSelected: viewModel.selectedFilter == .milestones) {
                                    viewModel.selectedFilter = .milestones
                                }
                                FilterChip(title: "Recipes", isSelected: viewModel.selectedFilter == .recipes) {
                                    viewModel.selectedFilter = .recipes
                                }
                                FilterChip(title: "Progress", isSelected: viewModel.selectedFilter == .progress) {
                                    viewModel.selectedFilter = .progress
                                }
                            }
                            .padding(.horizontal, 20)
                        }
                        .padding(.bottom, 8)
                        
                        // Posts Feed
                        ForEach(viewModel.filteredPosts) { post in
                            SocialPostCard(post: post)
                                .padding(.horizontal, 16)
                        }
                        
                        // Empty state
                        if viewModel.filteredPosts.isEmpty {
                            EmptySocialState()
                                .padding(.top, 60)
                        }
                        
                        // Bottom spacing
                        Spacer()
                            .frame(height: 40)
                    }
                    .padding(.top, 8)
                }
                .refreshable {
                    await viewModel.refresh()
                }
            }
            .navigationBarHidden(true)
        }
        .sheet(isPresented: $showCreatePost) {
            CreatePostView()
        }
    }
}

// MARK: - Filter Chip
struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 14, weight: isSelected ? .semibold : .medium))
                .foregroundColor(isSelected ? .white : KaloTheme.text)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? KaloTheme.mint : Color(.systemGray6))
                .cornerRadius(20)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Social Post Card
struct SocialPostCard: View {
    let post: SocialPost
    @State private var isLiked: Bool
    
    init(post: SocialPost) {
        self.post = post
        _isLiked = State(initialValue: post.isLiked)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // User Header
            HStack(spacing: 12) {
                // Avatar
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [KaloTheme.mint.opacity(0.3), KaloTheme.mint.opacity(0.1)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 44, height: 44)
                    .overlay(
                        Text(post.username.prefix(1))
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(KaloTheme.mint)
                    )
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(post.username)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundColor(KaloTheme.text)
                    
                    Text(post.createdAt, style: .relative)
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                // Post type badge
                PostTypeBadge(type: post.postType)
            }
            .padding(16)
            
            // Title & Description
            VStack(alignment: .leading, spacing: 8) {
                Text(post.title)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(KaloTheme.text)
                
                Text(post.description)
                    .font(.system(size: 15, weight: .regular))
                    .foregroundColor(.secondary)
                    .lineLimit(3)
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 12)
            
            // Stats Section (if available)
            if let stats = post.content.stats {
                PostStatsView(stats: stats)
                    .padding(.horizontal, 16)
                    .padding(.bottom, 12)
            }
            
            // Achievement Section (if available)
            if let achievement = post.content.achievement {
                AchievementBadge(achievement: achievement)
                    .padding(.horizontal, 16)
                    .padding(.bottom, 12)
            }
            
            // Tags
            if !post.tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(post.tags, id: \.self) { tag in
                            Text(tag)
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(KaloTheme.mint)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 5)
                                .background(KaloTheme.mint.opacity(0.1))
                                .cornerRadius(12)
                        }
                    }
                    .padding(.horizontal, 16)
                }
                .padding(.bottom, 12)
            }
            
            Divider()
                .padding(.horizontal, 16)
            
            // Action Buttons
            HStack(spacing: 24) {
                Button(action: {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                        isLiked.toggle()
                    }
                }) {
                    HStack(spacing: 6) {
                        Image(systemName: isLiked ? "heart.fill" : "heart")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(isLiked ? .red : .secondary)
                            .symbolEffect(.bounce, value: isLiked)
                        
                        Text("\(post.likes + (isLiked && !post.isLiked ? 1 : 0))")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.secondary)
                    }
                }
                
                Button(action: {}) {
                    HStack(spacing: 6) {
                        Image(systemName: "bubble.right")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.secondary)
                        
                        Text("\(post.comments)")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                Button(action: {}) {
                    Image(systemName: "square.and.arrow.up")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.secondary)
                }
            }
            .padding(16)
        }
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        .shadow(color: .black.opacity(0.06), radius: 10, y: 4)
    }
}

// MARK: - Post Type Badge
struct PostTypeBadge: View {
    let type: SocialPost.PostType
    
    var badgeInfo: (String, Color) {
        switch type {
        case .workout:
            return ("figure.run", .blue)
        case .recipe:
            return ("fork.knife", .orange)
        case .milestone:
            return ("trophy.fill", .yellow)
        case .progress:
            return ("chart.line.uptrend.xyaxis", .green)
        case .challenge:
            return ("flag.fill", .purple)
        }
    }
    
    var body: some View {
        Image(systemName: badgeInfo.0)
            .font(.system(size: 14, weight: .semibold))
            .foregroundColor(badgeInfo.1)
            .frame(width: 32, height: 32)
            .background(badgeInfo.1.opacity(0.15))
            .cornerRadius(8)
    }
}

// MARK: - Post Stats View
struct PostStatsView: View {
    let stats: SocialPost.PostStats
    
    var body: some View {
        HStack(spacing: 16) {
            if let distance = stats.distance {
                SocialStatItem(icon: "location.fill", value: formatDistance(distance), color: .blue)
            }
            if let duration = stats.duration {
                SocialStatItem(icon: "clock.fill", value: formatDuration(duration), color: .orange)
            }
            if let calories = stats.calories {
                SocialStatItem(icon: "flame.fill", value: "\(calories) cal", color: .red)
            }
            if let weight = stats.weight {
                SocialStatItem(icon: "scalemass.fill", value: String(format: "%.1f kg", abs(weight)), color: .purple)
            }
            if let reps = stats.reps {
                SocialStatItem(icon: "repeat", value: "\(reps) reps", color: .green)
            }
        }
        .padding(12)
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    func formatDistance(_ meters: Double) -> String {
        if meters >= 1000 {
            return String(format: "%.1f km", meters / 1000)
        }
        return String(format: "%.0f m", meters)
    }
    
    func formatDuration(_ seconds: Int) -> String {
        let hours = seconds / 3600
        let minutes = (seconds % 3600) / 60
        if hours > 0 {
            return "\(hours)h \(minutes)m"
        }
        return "\(minutes)m"
    }
}

struct SocialStatItem: View {
    let icon: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(color)
            
            Text(value)
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(KaloTheme.text)
        }
    }
}

// MARK: - Achievement Badge
struct AchievementBadge: View {
    let achievement: SocialPost.Achievement
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: achievement.icon)
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(.yellow)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(achievement.type)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.secondary)
                
                Text(achievement.value)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(KaloTheme.text)
            }
            
            Spacer()
        }
        .padding(12)
        .background(
            LinearGradient(
                colors: [Color.yellow.opacity(0.1), Color.orange.opacity(0.05)],
                startPoint: .leading,
                endPoint: .trailing
            )
        )
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.yellow.opacity(0.3), lineWidth: 1)
        )
    }
}

// MARK: - Empty State
struct EmptySocialState: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "person.2.fill")
                .font(.system(size: 60))
                .foregroundColor(.secondary.opacity(0.5))
            
            Text("No posts yet")
                .font(.system(size: 20, weight: .semibold))
                .foregroundColor(KaloTheme.text)
            
            Text("Be the first to share your fitness journey!")
                .font(.system(size: 15, weight: .medium))
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(40)
    }
}

// MARK: - Create Post View (Placeholder)
struct CreatePostView: View {
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationStack {
            VStack {
                Text("Create Post")
                    .font(.title2)
                
                Text("Coming soon!")
                    .foregroundColor(.secondary)
                
                Spacer()
            }
            .padding()
            .navigationTitle("New Post")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    SocialView()
}
