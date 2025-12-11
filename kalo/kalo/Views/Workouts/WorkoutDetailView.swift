import SwiftUI

/// Detailed workout view with sets table, statistics, and progression
struct WorkoutDetailView: View {
    @State var workoutVM: WorkoutViewModel
    let workout: Workout
    @Environment(\.dismiss) var dismiss
    
    var prData: ExercisePR? {
        workoutVM.personalRecords[workout.exerciseName.lowercased()]
    }
    
    var isPersonalRecord: Bool {
        prData?.maxWeight == workout.weight && prData?.maxReps == workout.reps
    }
    
    var volumeForExercise: Double {
        workoutVM.totalVolume(for: workout.exerciseName)
    }
    
    var estimatedOneRM: Double? {
        workoutVM.estimatedOneRM(for: workout.exerciseName)
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.gray.opacity(0.15)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Header
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 12) {
                            Text(workout.exerciseName)
                                .font(.system(size: 28, weight: .bold))
                                .foregroundColor(KaloTheme.text)
                            
                            if isPersonalRecord {
                                Image(systemName: "star.fill")
                                    .font(.system(size: 18))
                                    .foregroundColor(Color(red: 1.0, green: 0.8, blue: 0.0))
                            }
                        }
                        
                        HStack(spacing: 6) {
                            Image(systemName: "calendar")
                                .foregroundColor(.secondary)
                                .font(.system(size: 12))
                            Text(workout.date.formatted(date: .abbreviated, time: .shortened))
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.secondary)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(16)
                    .background(Color.white)
                    
                    // Scrollable Content
                    ScrollView {
                        VStack(spacing: 16) {
                            // PR Badge (if applicable)
                            if isPersonalRecord {
                                VStack(spacing: 8) {
                                    HStack(spacing: 8) {
                                        Image(systemName: "star.fill")
                                            .font(.system(size: 14, weight: .semibold))
                                            .foregroundColor(Color(red: 1.0, green: 0.8, blue: 0.0))
                                        
                                        Text("Personal Record")
                                            .font(.system(size: 14, weight: .semibold))
                                            .foregroundColor(Color(red: 1.0, green: 0.8, blue: 0.0))
                                        
                                        Spacer()
                                    }
                                }
                                .frame(maxWidth: .infinity)
                                .padding(12)
                                .background(Color(red: 1.0, green: 0.8, blue: 0.0).opacity(0.1))
                                .cornerRadius(10)
                            }
                            
                            // Key Metrics
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Key Metrics")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(.secondary)
                                
                                HStack(spacing: 12) {
                                    MetricCard(
                                        icon: "bolt.fill",
                                        title: "Sets × Reps",
                                        value: "\(workout.sets) × \(workout.reps)",
                                        color: KaloTheme.mint
                                    )
                                    
                                    if let weight = workout.weight {
                                        MetricCard(
                                            icon: "scalemass.fill",
                                            title: "Weight",
                                            value: "\(Int(weight)) lbs",
                                            color: KaloTheme.mint
                                        )
                                    }
                                }
                                
                                HStack(spacing: 12) {
                                    MetricCard(
                                        icon: "sum",
                                        title: "Volume",
                                        value: "\(Int(volumeForExercise))",
                                        unit: "lbs",
                                        color: KaloTheme.mint
                                    )
                                    
                                    if let oneRM = estimatedOneRM {
                                        MetricCard(
                                            icon: "crown.fill",
                                            title: "Est. 1RM",
                                            value: "\(Int(oneRM))",
                                            unit: "lbs",
                                            color: Color(red: 1.0, green: 0.8, blue: 0.0)
                                        )
                                    }
                                }
                            }
                            .padding(16)
                            .background(Color.white)
                            .cornerRadius(12)
                            
                            // Exercise History
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Exercise History")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(.secondary)
                                
                                let exerciseHistory = workoutVM.workouts
                                    .filter { $0.exerciseName.lowercased() == workout.exerciseName.lowercased() }
                                    .sorted { $0.date > $1.date }
                                    .prefix(5)
                                
                                if exerciseHistory.isEmpty {
                                    Text("No history")
                                        .font(.system(size: 13, weight: .medium))
                                        .foregroundColor(.secondary)
                                } else {
                                    VStack(spacing: 8) {
                                        ForEach(exerciseHistory.indices, id: \.self) { index in
                                            let item = exerciseHistory[index]
                                            HStack(spacing: 12) {
                                                Text("#\(exerciseHistory.count - index)")
                                                    .font(.system(size: 13, weight: .semibold))
                                                    .foregroundColor(.secondary)
                                                    .frame(width: 30)
                                                
                                                VStack(alignment: .leading, spacing: 2) {
                                                    Text(item.date.formatted(date: .abbreviated, time: .omitted))
                                                        .font(.system(size: 13, weight: .semibold))
                                                        .foregroundColor(KaloTheme.text)
                                                    
                                                    Text("\(item.sets)×\(item.reps) @ \(item.weight.map { "\(Int($0)) lbs" } ?? "BW")")
                                                        .font(.system(size: 12, weight: .medium))
                                                        .foregroundColor(.secondary)
                                                }
                                                
                                                Spacer()
                                                
                                                if item.id == workout.id {
                                                    Text("This")
                                                        .font(.system(size: 11, weight: .semibold))
                                                        .foregroundColor(KaloTheme.mint)
                                                        .padding(.horizontal, 8)
                                                        .padding(.vertical, 4)
                                                        .background(KaloTheme.mint.opacity(0.1))
                                                        .cornerRadius(4)
                                                }
                                            }
                                            .padding(10)
                                            .background(Color.gray.opacity(0.15))
                                            .cornerRadius(8)
                                        }
                                    }
                                }
                            }
                            .padding(16)
                            .background(Color.white)
                            .cornerRadius(12)
                            
                            // Notes Section
                            if let notes = workout.notes, !notes.isEmpty {
                                VStack(alignment: .leading, spacing: 12) {
                                    Text("Notes")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundColor(.secondary)
                                    
                                    Text(notes)
                                        .font(.system(size: 14))
                                        .foregroundColor(KaloTheme.text)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                        .padding(12)
                                        .background(Color.gray.opacity(0.15))
                                        .cornerRadius(8)
                                }
                                .padding(16)
                                .background(Color.white)
                                .cornerRadius(12)
                            }
                            
                            // Actions
                            VStack(spacing: 8) {
                                Button(action: { 
                                    Task { @MainActor in
                                        await workoutVM.deleteWorkout(workout)
                                        dismiss()
                                    }
                                }) {
                                    HStack {
                                        Image(systemName: "trash.fill")
                                        Text("Delete Workout")
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(12)
                                    .foregroundColor(.red)
                                    .background(Color.white)
                                    .cornerRadius(10)
                                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.red, lineWidth: 1))
                                }
                                
                                Button(action: { dismiss() }) {
                                    HStack {
                                        Image(systemName: "xmark")
                                        Text("Close")
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(12)
                                    .foregroundColor(KaloTheme.mint)
                                    .background(KaloTheme.mint.opacity(0.1))
                                    .cornerRadius(10)
                                }
                            }
                        }
                        .padding(16)
                    }
                }
            }
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Done") { dismiss() }
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(KaloTheme.mint)
                }
            }
        }
    }
}

/// Reusable metric card component
struct MetricCard: View {
    let icon: String
    let title: String
    let value: String
    let unit: String?
    let color: Color
    
    init(icon: String, title: String, value: String, unit: String? = nil, color: Color) {
        self.icon = icon
        self.title = title
        self.value = value
        self.unit = unit
        self.color = color
    }
    
    var body: some View {
        VStack(spacing: 8) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(color)
                Text(title)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.secondary)
            }
            
            HStack(alignment: .lastTextBaseline, spacing: 2) {
                Text(value)
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(KaloTheme.text)
                if let unit = unit {
                    Text(unit)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.secondary)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .center)
        .padding(12)
        .background(Color.gray.opacity(0.15))
        .cornerRadius(10)
    }
}

#Preview {
    WorkoutDetailView(
        workoutVM: WorkoutViewModel(),
        workout: Workout(
            id: "test",
            date: Date(),
            exerciseName: "Bench Press",
            sets: 4,
            reps: 8,
            weight: 185,
            duration: 45,
            notes: "Great session",
            userId: nil
        )
    )
}
