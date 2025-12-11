import SwiftUI

/// Reusable Personal Record badge for showing PR status
struct PRBadgeView: View {
    let isPR: Bool
    let text: String
    
    var body: some View {
        if isPR {
            HStack(spacing: 4) {
                Image(systemName: "star.fill")
                    .font(.system(size: 10, weight: .semibold))
                
                Text(text)
                    .font(.system(size: 11, weight: .semibold))
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(KaloTheme.mint)
            .foregroundColor(.white)
            .cornerRadius(6)
        }
    }
}

/// Component showing workout intensity with PR indicator
struct WorkoutCardWithPR: View {
    let workout: Workout
    let isPersonalRecord: Bool
    let onDelete: () -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon with PR highlight
            VStack {
                Image(systemName: "dumbbell")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(isPersonalRecord ? KaloTheme.mint : KaloTheme.mint.opacity(0.6))
                    .cornerRadius(12)
            }
            
            // Content
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(workout.exerciseName)
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(KaloTheme.text)
                        
                        if isPersonalRecord {
                            Text("Personal Record 🏆")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(KaloTheme.mint)
                        }
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text(workout.date.formatted(date: .omitted, time: .shortened))
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                        
                        if isPersonalRecord {
                            PRBadgeView(isPR: true, text: "NEW PR")
                        }
                    }
                }
                
                HStack(spacing: 12) {
                    if workout.sets > 0 {
                        Label(String(format: "%d×%d", workout.sets, workout.reps), systemImage: "repeat")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                    }
                    
                    if let weight = workout.weight {
                        Label(String(format: "%.0f lbs", weight), systemImage: "scalemass.fill")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                    }
                    
                    if let duration = workout.duration {
                        Label(String(format: "%d min", duration), systemImage: "timer")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                }
            }
            
            // Delete Button
            Button(action: onDelete) {
                Image(systemName: "xmark.circle")
                    .font(.system(size: 18))
                    .foregroundColor(.secondary)
                    .opacity(0.6)
            }
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: KaloTheme.shadowColor, radius: KaloTheme.shadowRadius, x: 0, y: 1)
    }
}

#Preview {
    VStack(spacing: 12) {
        WorkoutCardWithPR(
            workout: Workout.mockWorkouts[0],
            isPersonalRecord: false,
            onDelete: { }
        )
        
        WorkoutCardWithPR(
            workout: Workout.mockWorkouts[1],
            isPersonalRecord: true,
            onDelete: { }
        )
    }
    .padding(16)
    .background(Color(.gray))
}
