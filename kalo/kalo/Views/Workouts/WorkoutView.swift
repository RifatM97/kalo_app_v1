import SwiftUI

struct WorkoutView: View {
    @State var workoutVM: WorkoutViewModel
    @State private var showAddSheet = false
    
    var totalVolume: Int {
        Int(workoutVM.workouts.reduce(0.0) { total, workout in
            let weight = workout.weight ?? 0
            return total + (Double(workout.sets * workout.reps) * weight)
        })
    }
    
    var exerciseCount: Int {
        Set(workoutVM.workouts.map { $0.exerciseName }).count
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.gray.opacity(0.15)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // MARK: - Header
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Workouts")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(KaloTheme.text)
                        
                        HStack(spacing: 12) {
                            Image(systemName: "dumbbell")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(KaloTheme.mint)
                            
                            Text("\(workoutVM.workouts.count) workouts • Track your training")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.secondary)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(16)
                    .background(Color.white)
                    
                    if workoutVM.workouts.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "dumbbell")
                                .font(.system(size: 48))
                                .foregroundColor(.secondary)
                            Text("No Workouts Yet")
                                .font(.system(size: 18, weight: .semibold))
                                .foregroundColor(KaloTheme.text)
                            Text("Start logging your exercises")
                                .foregroundColor(.secondary)
                        }
                        .frame(maxHeight: .infinity)
                        .frame(maxWidth: .infinity)
                    } else {
                        ScrollView {
                            VStack(spacing: 16) {
                                HStack(spacing: 12) {
                                    StatSummaryCard(title: "Total Volume", value: "\(totalVolume)", unit: "lbs", icon: "sum", color: KaloTheme.mint)
                                    StatSummaryCard(title: "Exercises", value: "\(exerciseCount)", unit: "types", icon: "square.grid.2x2", color: Color(red: 1.0, green: 0.8, blue: 0.0))
                                }
                                
                                // Action Buttons
                                HStack(spacing: 12) {
                                    Button(action: { showAddSheet = true }) {
                                        HStack {
                                            Image(systemName: "plus.circle.fill")
                                            Text("Log Workout")
                                        }
                                        .frame(maxWidth: .infinity)
                                        .padding(12)
                                        .background(KaloTheme.mint)
                                        .foregroundColor(.white)
                                        .cornerRadius(12)
                                    }
                                    
                                    NavigationLink(destination: WorkoutHistoryView(workoutVM: workoutVM)) {
                                        HStack {
                                            Image(systemName: "list.bullet")
                                            Text("History")
                                        }
                                        .frame(maxWidth: .infinity)
                                        .padding(12)
                                        .background(Color.white)
                                        .foregroundColor(KaloTheme.mint)
                                        .cornerRadius(12)
                                        .overlay(RoundedRectangle(cornerRadius: 12).stroke(KaloTheme.mint, lineWidth: 1.5))
                                    }
                                }
                            }
                            .padding(16)
                        }
                    }
                }
            }
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .sheet(isPresented: $showAddSheet) {
                LogWorkoutView(workoutVM: workoutVM)
            }
        }
    }
}

struct StatSummaryCard: View {
    let title: String
    let value: String
    let unit: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(color)
                Spacer()
            }
            
            Text(value)
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(KaloTheme.text)
            
            Text(unit)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
                .textCase(.uppercase)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: KaloTheme.shadowColor, radius: KaloTheme.shadowRadius, x: 0, y: 1)
    }
}

struct PRHighlightCard: View {
    let pr: ExercisePR
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "crown.fill")
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(Color(red: 1.0, green: 0.8, blue: 0.0))
                .frame(width: 40, height: 40)
                .background(Color(red: 1.0, green: 0.8, blue: 0.0).opacity(0.1))
                .cornerRadius(10)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(pr.exerciseName)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                
                Text("\(Int(pr.maxWeight)) lbs × \(pr.maxReps) reps")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Text(pr.prDate.formatted(date: .abbreviated, time: .omitted))
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(KaloTheme.mint)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(KaloTheme.mint.opacity(0.1))
                .cornerRadius(4)
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: KaloTheme.shadowColor, radius: KaloTheme.shadowRadius, x: 0, y: 1)
    }
}

#Preview {
    WorkoutView(workoutVM: WorkoutViewModel())
}
