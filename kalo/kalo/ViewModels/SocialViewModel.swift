import Foundation
import SwiftUI

@Observable
final class SocialViewModel {
    var posts: [SocialPost] = []
    var selectedFilter: FilterType = .all
    var isLoading = false
    var error: String?
    
    enum FilterType {
        case all, workouts, milestones, recipes, progress
    }
    
    var filteredPosts: [SocialPost] {
        switch selectedFilter {
        case .all:
            return posts
        case .workouts:
            return posts.filter { $0.postType == .workout }
        case .milestones:
            return posts.filter { $0.postType == .milestone }
        case .recipes:
            return posts.filter { $0.postType == .recipe }
        case .progress:
            return posts.filter { $0.postType == .progress }
        }
    }
    
    init() {
        // Load sample data for MVP
        loadSampleData()
    }
    
    private func loadSampleData() {
        posts = SocialPost.samplePosts
    }
    
    @MainActor
    func refresh() async {
        isLoading = true
        defer { isLoading = false }
        
        // Simulate network delay
        try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
        
        // In production, this would fetch from backend
        // For now, reload sample data
        loadSampleData()
    }
    
    func likePost(_ postId: String) {
        // In production, would call backend API
        // For now, just log the action
        if posts.contains(where: { $0.id == postId }) {
            print("Liked post: \(postId)")
        }
    }
    
    func commentOnPost(_ postId: String, comment: String) {
        // In production, would call backend API
        print("Comment on \(postId): \(comment)")
    }
}
