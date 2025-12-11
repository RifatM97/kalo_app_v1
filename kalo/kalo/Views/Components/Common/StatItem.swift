import SwiftUI

/// Reusable stat item component for displaying metrics
/// Used across Activity views and Run detail screens
struct StatItem: View {
    let label: String
    let value: String
    let icon: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 10, weight: .semibold))
                    .foregroundColor(KaloTheme.mint)
                
                Text(label)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.secondary)
            }
            
            Text(value)
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(KaloTheme.text)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
    }
}

#Preview {
    HStack(spacing: 12) {
        StatItem(
            label: "Duration",
            value: "45:30",
            icon: "clock.fill"
        )
        
        StatItem(
            label: "Avg Pace",
            value: "5:23/km",
            icon: "bolt.fill"
        )
        
        StatItem(
            label: "Calories",
            value: "420",
            icon: "flame.fill"
        )
    }
    .padding()
}
