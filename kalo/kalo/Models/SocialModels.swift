import Foundation

// MARK: - Social Post Models

struct SocialPost: Identifiable, Codable {
    let id: String
    let userId: String
    let username: String
    let userAvatarUrl: String?
    let title: String
    let description: String
    let postType: PostType
    let content: PostContent
    let tags: [String]
    let likes: Int
    let comments: Int
    let createdAt: Date
    let isLiked: Bool
    
    enum PostType: String, Codable {
        case workout = "workout"
        case recipe = "recipe"
        case milestone = "milestone"
        case progress = "progress"
        case challenge = "challenge"
    }
    
    struct PostContent: Codable {
        let imageUrl: String?
        let stats: PostStats?
        let achievement: Achievement?
    }
    
    struct PostStats: Codable {
        let distance: Double?
        let duration: Int?
        let calories: Int?
        let weight: Double?
        let reps: Int?
        let sets: Int?
    }
    
    struct Achievement: Codable {
        let type: String
        let value: String
        let icon: String
    }
}

// MARK: - Comment Model

struct SocialComment: Identifiable, Codable {
    let id: String
    let postId: String
    let userId: String
    let username: String
    let userAvatarUrl: String?
    let content: String
    let likes: Int
    let createdAt: Date
    let isLiked: Bool
}

// MARK: - Sample Data for MVP

extension SocialPost {
    static let samplePosts: [SocialPost] = [
        SocialPost(
            id: "1",
            userId: "user1",
            username: "Alex Johnson",
            userAvatarUrl: nil,
            title: "New PR: 110kg Deadlift! 🎉",
            description: "Finally hit the 110kg milestone on deadlifts! Been working towards this for 3 months. Proper form and progressive overload really works!",
            postType: .milestone,
            content: PostContent(
                imageUrl: nil,
                stats: PostStats(distance: nil, duration: nil, calories: nil, weight: 110, reps: 5, sets: 3),
                achievement: Achievement(type: "PR", value: "110kg", icon: "trophy.fill")
            ),
            tags: ["#deadlift", "#PR", "#legs", "#strength"],
            likes: 42,
            comments: 8,
            createdAt: Date().addingTimeInterval(-3600),
            isLiked: false
        ),
        SocialPost(
            id: "2",
            userId: "user2",
            username: "Sarah Martinez",
            userAvatarUrl: nil,
            title: "Morning 5K Run 🏃‍♀️",
            description: "Beautiful sunrise run today! Feeling energized and ready for the day. Consistency is key!",
            postType: .workout,
            content: PostContent(
                imageUrl: nil,
                stats: PostStats(distance: 5000, duration: 1800, calories: 320, weight: nil, reps: nil, sets: nil),
                achievement: nil
            ),
            tags: ["#running", "#cardio", "#morning", "#5k"],
            likes: 28,
            comments: 5,
            createdAt: Date().addingTimeInterval(-7200),
            isLiked: true
        ),
        SocialPost(
            id: "3",
            userId: "user3",
            username: "Mike Chen",
            userAvatarUrl: nil,
            title: "Meal Prep Sunday 🥗",
            description: "Prepped all my meals for the week! High protein chicken bowls with quinoa and roasted veggies. Ready to crush my macros this week.",
            postType: .recipe,
            content: PostContent(
                imageUrl: nil,
                stats: nil,
                achievement: nil
            ),
            tags: ["#mealprep", "#nutrition", "#healthyeating", "#protein"],
            likes: 35,
            comments: 12,
            createdAt: Date().addingTimeInterval(-14400),
            isLiked: false
        ),
        SocialPost(
            id: "4",
            userId: "user4",
            username: "Emma Wilson",
            userAvatarUrl: nil,
            title: "30 Days Streak! 🔥",
            description: "Just hit my 30-day workout streak! Feeling stronger than ever. Shoutout to the Kalo community for keeping me motivated!",
            postType: .milestone,
            content: PostContent(
                imageUrl: nil,
                stats: nil,
                achievement: Achievement(type: "Streak", value: "30 Days", icon: "flame.fill")
            ),
            tags: ["#streak", "#motivation", "#consistency", "#fitness"],
            likes: 67,
            comments: 15,
            createdAt: Date().addingTimeInterval(-21600),
            isLiked: true
        ),
        SocialPost(
            id: "5",
            userId: "user5",
            username: "Jordan Lee",
            userAvatarUrl: nil,
            title: "Basketball Training Session 🏀",
            description: "Intense vertical jump training today. Did 100 box jumps and plyometric exercises. Feeling the burn but loving the progress!",
            postType: .workout,
            content: PostContent(
                imageUrl: nil,
                stats: PostStats(distance: nil, duration: 3600, calories: 450, weight: nil, reps: 100, sets: 5),
                achievement: nil
            ),
            tags: ["#basketball", "#plyometrics", "#verticaljump", "#training"],
            likes: 31,
            comments: 6,
            createdAt: Date().addingTimeInterval(-28800),
            isLiked: false
        ),
        SocialPost(
            id: "6",
            userId: "user6",
            username: "Taylor Kim",
            userAvatarUrl: nil,
            title: "Weight Loss Progress: -10kg! 🎯",
            description: "Three months of consistent training and clean eating. Down 10kg and feeling amazing! Still have 5kg to go to reach my goal.",
            postType: .progress,
            content: PostContent(
                imageUrl: nil,
                stats: PostStats(distance: nil, duration: nil, calories: nil, weight: -10, reps: nil, sets: nil),
                achievement: Achievement(type: "Weight Loss", value: "-10kg", icon: "chart.line.downtrend.xyaxis")
            ),
            tags: ["#weightloss", "#transformation", "#progress", "#fitness"],
            likes: 89,
            comments: 23,
            createdAt: Date().addingTimeInterval(-43200),
            isLiked: true
        )
    ]
}
