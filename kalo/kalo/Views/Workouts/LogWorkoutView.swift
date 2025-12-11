import SwiftUI

struct LogWorkoutView: View {
    @State var workoutVM: WorkoutViewModel
    @Environment(\.dismiss) var dismiss
    
    @State private var exerciseName = ""
    @State private var sets = "3"
    @State private var reps = "8"
    @State private var weight = ""
    @State private var duration = ""
    @State private var notes = ""
    @State private var showPRAnimation = false
    
    var isPotentialPR: Bool {
        guard !exerciseName.isEmpty else { return false }
        let weightVal = Double(weight) ?? 0
        let repsVal = Int(reps) ?? 0
        let weightToPass: Double? = weightVal > 0 ? weightVal : nil
        return workoutVM.isNewPR(exerciseName: exerciseName, weight: weightToPass, reps: repsVal)
    }
    
    var isFormValid: Bool {
        return !exerciseName.isEmpty && !sets.isEmpty && !reps.isEmpty
    }
    
    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Log Workout")
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(KaloTheme.text)
            
            Text("Track your exercise")
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.white)
    }
    
    private var prBadge: some View {
        VStack(spacing: 8) {
            HStack(spacing: 8) {
                Image(systemName: "star.fill")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.mint)
                
                Text("Potential Personal Record!")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.mint)
                
                Spacer()
            }
            
            if let prData = workoutVM.personalRecords[exerciseName.lowercased()] {
                Text("Current PR: \(Int(prData.maxWeight)) lbs × \(prData.maxReps) reps")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(12)
        .background(KaloTheme.mint.opacity(0.1))
        .cornerRadius(10)
        .transition(.scale.combined(with: .opacity))
    }
    
    private var exerciseDetailsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Exercise Details")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Exercise Name *")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                TextField("e.g., Bench Press", text: $exerciseName)
                    .padding(12)
                    .background(Color.white)
                    .cornerRadius(10)
            }
            
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Sets *")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(KaloTheme.text)
                    TextField("3", text: $sets)
                        .keyboardType(.numberPad)
                        .padding(12)
                        .background(Color.white)
                        .cornerRadius(10)
                }
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("Reps *")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(KaloTheme.text)
                    TextField("8", text: $reps)
                        .keyboardType(.numberPad)
                        .padding(12)
                        .background(Color.white)
                        .cornerRadius(10)
                }
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Weight (lbs)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                TextField("Optional", text: $weight)
                    .keyboardType(.decimalPad)
                    .padding(12)
                    .background(Color.white)
                    .cornerRadius(10)
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
    }
    
    private var optionalDetailsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Optional Details")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Duration (minutes)")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                TextField("e.g., 45", text: $duration)
                    .keyboardType(.numberPad)
                    .padding(12)
                    .background(Color.white)
                    .cornerRadius(10)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Notes")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(KaloTheme.text)
                TextField("Optional", text: $notes, axis: .vertical)
                    .lineLimit(3...6)
                    .padding(12)
                    .background(Color.white)
                    .cornerRadius(10)
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
    }
    
    private var statsPreviewSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Workout Stats")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.secondary)
            
            HStack(spacing: 12) {
                WorkoutStatBox(title: "Volume", value: calculateVolume(), unit: "lbs")
                WorkoutStatBox(title: "Est. 1RM", value: calculateEstOneRM(), unit: "lbs")
            }
        }
        .padding(16)
    }
    
    private var saveButtonSection: some View {
        VStack(spacing: 8) {
            let buttonBackground = isPotentialPR ? Color(red: 1.0, green: 0.8, blue: 0.0) : KaloTheme.mint
            
            Button(action: saveWorkout) {
                HStack {
                    let iconName = isPotentialPR ? "star.fill" : "checkmark.circle.fill"
                    let buttonText = isPotentialPR ? "Save PR Workout" : "Save Workout"
                    
                    Image(systemName: iconName)
                    Text(buttonText)
                }
                .frame(maxWidth: .infinity)
                .padding(14)
                .background(buttonBackground)
                .foregroundColor(.white)
                .font(.system(size: 16, weight: .semibold))
                .cornerRadius(12)
            }
            .disabled(!isFormValid)
            .opacity(isFormValid ? 1.0 : 0.6)
            
            if let error = workoutVM.error, !error.isEmpty {
                Text(error)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.red)
            }
        }
        .padding(16)
        .background(Color.white)
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.gray.opacity(0.15)
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    headerSection
                    
                    ScrollView {
                        VStack(spacing: 16) {
                            if isPotentialPR {
                                prBadge
                            }
                            exerciseDetailsSection
                            optionalDetailsSection
                            statsPreviewSection
                            saveButtonSection
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
                    Button("Cancel") {
                        dismiss()
                    }
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.mint)
                }
            }
        }
    }
    
    private func calculateVolume() -> String {
        let setsInt = Int(sets) ?? 0
        let repsInt = Int(reps) ?? 0
        let weightDouble = Double(weight) ?? 0
        let volume = Double(setsInt * repsInt) * weightDouble
        return String(format: "%.0f", volume)
    }
    
    private func calculateEstOneRM() -> String {
        guard let weightDouble = Double(weight), weightDouble > 0 else { return "—" }
        let repsInt = Int(reps) ?? 0
        guard repsInt > 0 else { return "—" }
        let oneRM = weightDouble * (1.0 + Double(repsInt) / 30.0)
        return String(format: "%.0f", oneRM)
    }
    
    private func saveWorkout() {
        workoutVM.addWorkout(
            exerciseName: exerciseName,
            sets: Int(sets) ?? 0,
            reps: Int(reps) ?? 0,
            weight: Double(weight),
            duration: Int(duration),
            notes: notes.isEmpty ? nil : notes
        )
        if isPotentialPR {
            showPRAnimation = true
        }
        dismiss()
    }
}

struct WorkoutStatBox: View {
    let title: String
    let value: String
    let unit: String
    
    var body: some View {
        VStack(spacing: 6) {
            Text(title)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
            
            HStack(alignment: .lastTextBaseline, spacing: 2) {
                Text(value)
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(KaloTheme.mint)
                Text(unit)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(12)
        .background(Color.white)
        .cornerRadius(10)
    }
}

#Preview {
    LogWorkoutView(workoutVM: WorkoutViewModel())
}
