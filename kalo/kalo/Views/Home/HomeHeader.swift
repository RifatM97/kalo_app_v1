import SwiftUI

/// Header section with greeting and date, styled like Apple App Store "Today" tab
struct HomeHeader: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Greeting
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Good \(timeOfDay()),")
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.secondary)
                    
                    Text(userName())
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(KaloTheme.text)
                }
                
                Spacer()
                
                // User avatar placeholder
                Circle()
                    .fill(KaloTheme.mint.opacity(0.2))
                    .frame(width: 44, height: 44)
                    .overlay(
                        Image(systemName: "person.crop.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(KaloTheme.mint)
                    )
            }
            
            // Date
            HStack(spacing: 8) {
                Image(systemName: "calendar")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.secondary)
                
                Text(Date().formatted(date: .abbreviated, time: .omitted))
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.white)
    }
    
    private func timeOfDay() -> String {
        let hour = Calendar.current.component(.hour, from: Date())
        if hour < 12 {
            return "morning"
        } else if hour < 18 {
            return "afternoon"
        } else {
            return "evening"
        }
    }
    
    private func userName() -> String {
        // TODO: Replace with actual user name from User model
        return "Rifat"
    }
}

#Preview {
    HomeHeader()
}
