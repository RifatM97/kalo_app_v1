import SwiftUI

/// Detailed statistics view for a specific exercise
struct ExerciseStatsView: View {
    let workoutVM: WorkoutViewModel
    let exerciseName: String
    
    var body: some View {
        VStack(spacing: 16) {
            // Header
            VStack(alignment: .leading, spacing: 8) {
                Text(exerciseName)
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(KaloTheme.text)
                
                Text("Career Statistics")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(16)
            
            // Stats Grid
            VStack(spacing: 12) {
                // Max Weight
                HStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Max Weight")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.secondary)
                        
                        HStack(spacing: 4) {
                            if let maxWeight = workoutVM.maxWeight(for: exerciseName) {
                                Text(String(format: "%.0f", maxWeight))
                                    .font(.system(size: 24, weight: .bold))
                                    .foregroundColor(KaloTheme.mint)
                                
                                Text("lbs")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(.secondary)
                            } else {
                                Text("—")
                                    .font(.system(size: 20, weight: .semibold))
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    
                    Spacer()
                    
                    // Estimated 1RM
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Estimated 1RM")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.secondary)
                        
                        HStack(spacing: 4) {
                            if let oneRM = workoutVM.estimatedOneRM(for: exerciseName) {
                                Text(String(format: "%.0f", oneRM))
                                    .font(.system(size: 24, weight: .bold))
                                    .foregroundColor(KaloTheme.mint)
                                
                                Text("lbs")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(.secondary)
                            } else {
                                Text("—")
                                    .font(.system(size: 20, weight: .semibold))
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                }
                .padding(12)
                .background(Color.white)
                .cornerRadius(12)
                
                // Total Volume
                HStack(spacing: 12) {
                    Image(systemName: "chart.bar.fill")
                        .font(.system(size: 16))
                        .foregroundColor(KaloTheme.mint)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Total Volume")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.secondary)
                        
                        Text(String(format: "%.0f", workoutVM.totalVolume(for: exerciseName)))
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(KaloTheme.text)
                    }
                    
                    Spacer()
                    
                    Text("lbs")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(.secondary)
                }
                .padding(12)
                .background(Color.white)
                .cornerRadius(12)
                
                // PR Badge
                if let pr = workoutVM.personalRecords[exerciseName.lowercased()] {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 8) {
                            Image(systemName: "star.fill")
                                .font(.system(size: 14, weight: .semibold))
                            
                            Text("Personal Record")
                                .font(.system(size: 12, weight: .semibold))
                            
                            Spacer()
                        }
                        
                        HStack(spacing: 12) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Weight")
                                    .font(.system(size: 11, weight: .semibold))
                                    .foregroundColor(.secondary)
                                
                                Text(String(format: "%.0f lbs", pr.maxWeight))
                                    .font(.system(size: 16, weight: .bold))
                            }
                            
                            Divider()
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Reps")
                                    .font(.system(size: 11, weight: .semibold))
                                    .foregroundColor(.secondary)
                                
                                Text("\(pr.maxReps)")
                                    .font(.system(size: 16, weight: .bold))
                            }
                            
                            Divider()
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Date")
                                    .font(.system(size: 11, weight: .semibold))
                                    .foregroundColor(.secondary)
                                
                                Text(pr.prDate.formatted(date: .abbreviated, time: .omitted))
                                    .font(.system(size: 14, weight: .semibold))
                            }
                            
                            Spacer()
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(12)
                    .background(KaloTheme.mint.opacity(0.1))
                    .foregroundColor(KaloTheme.mint)
                    .cornerRadius(12)
                }
            }
            .padding(16)
            
            Spacer()
        }
        .background(Color.gray.opacity(0.15))
    }
}

#Preview {
    ExerciseStatsView(workoutVM: WorkoutViewModel(), exerciseName: "Bench Press")
}
