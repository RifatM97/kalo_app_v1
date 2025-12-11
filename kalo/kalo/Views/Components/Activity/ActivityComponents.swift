import SwiftUI

/// Summary Stat Card - displays a single metric with value and label
struct SummaryStatCard: View {
    let label: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 32, height: 32)
                    .background(color)
                    .cornerRadius(8)
                
                Text(label)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
                
                Spacer()
            }
            
            Text(value)
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(KaloTheme.text)
        }
        .padding(12)
        .background(Color.gray.opacity(0.15))
        .cornerRadius(12)
    }
}

/// Progress Ring - circular progress indicator
struct ProgressRingView: View {
    let percentage: Float
    let size: CGFloat = 120
    let lineWidth: CGFloat = 8
    let color: Color = KaloTheme.mint
    
    var body: some View {
        ZStack {
            // Background circle
            Circle()
                .stroke(Color.gray.opacity(0.2), lineWidth: lineWidth)
            
            // Progress circle
            Circle()
                .trim(from: 0, to: CGFloat(min(percentage / 100, 1.0)))
                .stroke(color, style: StrokeStyle(lineWidth: lineWidth, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut(duration: 0.5), value: percentage)
            
            // Center text
            VStack(spacing: 4) {
                Text(String(format: "%.0f%%", percentage))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(KaloTheme.text)
                
                Text("Complete")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
            }
        }
        .frame(width: size, height: size)
    }
}

/// Run Card - displays a single run in list
struct RunCard: View {
    let run: RunDetail
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 12) {
                // Icon
                VStack {
                    Image(systemName: "figure.run")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(width: 44, height: 44)
                        .background(KaloTheme.mint)
                        .cornerRadius(12)
                }
                
                // Content
                VStack(alignment: .leading, spacing: 6) {
                    Text(formatDate(run.started_at))
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(KaloTheme.text)
                    
                    HStack(spacing: 16) {
                        Label(ActivityViewModel.formatDistance(run.distance_m),
                              systemImage: "location.fill")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                        
                        Label(ActivityViewModel.formatTime(run.duration_s),
                              systemImage: "clock.fill")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                        
                        Label(ActivityViewModel.formatPace(run.avg_pace_s_per_km),
                              systemImage: "bolt.fill")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                // Calories
                if let calories = run.calories_burned {
                    VStack(alignment: .trailing, spacing: 4) {
                        Text(String(calories))
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(KaloTheme.mint)
                        
                        Text("kcal")
                            .font(.system(size: 11, weight: .medium))
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(12)
            .background(Color.gray.opacity(0.15))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func formatDate(_ isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: isoString) {
            let dateFormatter = DateFormatter()
            dateFormatter.dateStyle = .medium
            dateFormatter.timeStyle = .short
            return dateFormatter.string(from: date)
        }
        return isoString
    }
}

/// Heatmap View - calendar grid showing activity intensity
struct HeatmapView: View {
    let data: [HeatmapDay]
    let period: String
    
    let columns = [
        GridItem(.adaptive(minimum: 30), spacing: 4)
    ]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Activity Heatmap")
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(KaloTheme.text)
            
            LazyVGrid(columns: columns, spacing: 4) {
                ForEach(data, id: \.date) { day in
                    VStack(spacing: 2) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 4, style: .continuous)
                                .fill(colorForIntensity(day.intensity))
                            
                            Text(String(day.date.split(separator: "-").last ?? ""))
                                .font(.system(size: 8, weight: .semibold))
                                .foregroundColor(.white)
                                .opacity(day.intensity > 0.3 ? 1 : 0)
                        }
                        .aspectRatio(1, contentMode: .fit)
                    }
                }
            }
            
            // Legend
            HStack(spacing: 16) {
                HStack(spacing: 4) {
                    Circle().fill(Color.gray.opacity(0.2)).frame(width: 8, height: 8)
                    Text("None").font(.system(size: 10, weight: .medium)).foregroundColor(.secondary)
                }
                
                HStack(spacing: 4) {
                    Circle().fill(KaloTheme.mint.opacity(0.3)).frame(width: 8, height: 8)
                    Text("Low").font(.system(size: 10, weight: .medium)).foregroundColor(.secondary)
                }
                
                HStack(spacing: 4) {
                    Circle().fill(KaloTheme.mint).frame(width: 8, height: 8)
                    Text("High").font(.system(size: 10, weight: .medium)).foregroundColor(.secondary)
                }
                
                Spacer()
            }
        }
        .padding(16)
        .background(Color.gray.opacity(0.15))
        .cornerRadius(16)
    }
    
    private func colorForIntensity(_ intensity: Float) -> Color {
        if intensity == 0 {
            return Color.gray.opacity(0.2)
        } else if intensity < 0.5 {
            return KaloTheme.mint.opacity(Double(intensity * 2))
        } else {
            return KaloTheme.mint.opacity(Double(0.3 + intensity * 0.7))
        }
    }
}

/// Summary Card - displays week/month summary stats
struct SummarySectionCard: View {
    let summary: RunSummary
    let period: String
    
    var body: some View {
        VStack(spacing: 16) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("This \(periodLabel)")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.secondary)
                    
                    Text(ActivityViewModel.formatDistance(summary.total_distance_m))
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(KaloTheme.text)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    HStack(spacing: 4) {
                        Image(systemName: "figure.run")
                            .font(.system(size: 12, weight: .semibold))
                        Text(String(summary.number_of_runs))
                            .font(.system(size: 14, weight: .semibold))
                    }
                    .foregroundColor(KaloTheme.mint)
                    
                    Text(ActivityViewModel.formatTime(summary.total_time_s))
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.secondary)
                }
            }
            
            Divider()
            
            // Stats grid
            HStack(spacing: 12) {
                ActivityStatItem(
                    label: "Avg Pace",
                    value: ActivityViewModel.formatPace(summary.average_pace_s_per_km),
                    icon: "bolt.fill"
                )
                
                ActivityStatItem(
                    label: "Calories",
                    value: String(summary.total_calories),
                    icon: "flame.fill"
                )
            }
        }
        .padding(16)
        .background(Color.gray.opacity(0.15))
        .cornerRadius(16)
    }
    
    private var periodLabel: String {
        switch period {
        case "month": return "Month"
        case "year": return "Year"
        default: return "Week"
        }
    }
}

/// Small stat item for grid - Activity specific with label
struct ActivityStatItem: View {
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
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 16) {
        SummaryStatCard(
            label: "This Week",
            value: "12.5 km",
            icon: "figure.run",
            color: KaloTheme.mint
        )
        
        ProgressRingView(percentage: 65)
        
        Spacer()
    }
    .padding(16)
}
