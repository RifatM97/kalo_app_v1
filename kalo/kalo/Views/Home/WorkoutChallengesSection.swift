import SwiftUI

/// Workouts and challenges section showing active workouts and challenges
struct WorkoutChallengesSection: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Section Title
            VStack(alignment: .leading, spacing: 4) {
                Text("Workouts & Challenges")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                
                Text("Stay active, earn points")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
            }
            
            VStack(spacing: 12) {
                // Next Workout Card
                WorkoutCard(
                    icon: "figure.run",
                    title: "Morning Run",
                    subtitle: "Scheduled for tomorrow at 6:30 AM",
                    duration: "30 min",
                    distance: "5K"
                )
                
                // Active Challenge Card
                ChallengeCard(
                    icon: "flame.fill",
                    title: "7-Day Challenge",
                    subtitle: "Drink 8 glasses of water daily",
                    progress: 3,
                    total: 7,
                    progressColor: .orange
                )
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.white)
    }
}

/// Workout card component
struct WorkoutCard: View {
    let icon: String
    let title: String
    let subtitle: String
    let duration: String
    let distance: String
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            Image(systemName: icon)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
                .frame(width: 40, height: 40)
                .background(KaloTheme.mint)
                .cornerRadius(10)
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                
                Text(subtitle)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
            
            Spacer()
            
            // Details
            VStack(alignment: .trailing, spacing: 4) {
                HStack(spacing: 8) {
                    Label(duration, systemImage: "clock.fill")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.secondary)
                }
                
                HStack(spacing: 8) {
                    Label(distance, systemImage: "location.fill")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(12)
        .background(Color.gray.opacity(0.15))
        .cornerRadius(12)
    }
}

/// Challenge progress card
struct ChallengeCard: View {
    let icon: String
    let title: String
    let subtitle: String
    let progress: Int
    let total: Int
    let progressColor: Color
    
    var progressPercentage: Double {
        Double(progress) / Double(total)
    }
    
    var body: some View {
        VStack(spacing: 12) {
            // Header
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 40, height: 40)
                    .background(progressColor)
                    .cornerRadius(10)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(KaloTheme.text)
                    
                    Text(subtitle)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 2) {
                    Text("\(progress)/\(total)")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(progressColor)
                    
                    Text("days")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.secondary)
                }
            }
            
            // Progress Bar
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.gray.opacity(0.4))
                    
                    RoundedRectangle(cornerRadius: 4)
                        .fill(progressColor)
                        .frame(width: geo.size.width * progressPercentage)
                }
                .frame(height: 6)
            }
            .frame(height: 6)
        }
        .padding(12)
        .background(Color.gray.opacity(0.15))
        .cornerRadius(12)
    }
}

#Preview {
    WorkoutChallengesSection()
}
