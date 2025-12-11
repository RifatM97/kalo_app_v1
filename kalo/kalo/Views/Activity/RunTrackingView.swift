import SwiftUI

struct RunTrackingView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel = RunTrackingViewModel()
    @State private var showFinishAlert = false
    @State private var manualDistance: String = "5.0"
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.gray.opacity(0.15)
                    .ignoresSafeArea()
                
                VStack(spacing: 24) {
                    // MARK: - Header
                    HStack {
                        Text(viewModel.isRunning ? "Running" : "Ready to Run")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(KaloTheme.text)
                        
                        Spacer()
                        
                        Button(action: { dismiss() }) {
                            Image(systemName: "xmark.circle.fill")
                                .font(.system(size: 24))
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 16)
                    
                    // MARK: - Timer Display
                    VStack(spacing: 16) {
                        // Large timer
                        Text(formatTime(viewModel.elapsedSeconds))
                            .font(.system(size: 64, weight: .bold, design: .monospaced))
                            .foregroundColor(KaloTheme.mint)
                        
                        // Stats grid
                        HStack(spacing: 16) {
                            StatBox(
                                label: "Distance",
                                value: ActivityViewModel.formatDistance(viewModel.distance_m),
                                color: KaloTheme.mint
                            )
                            
                            StatBox(
                                label: "Pace",
                                value: viewModel.currentPace.map { ActivityViewModel.formatPace($0) } ?? "--",
                                color: KaloTheme.mint
                            )
                            
                            StatBox(
                                label: "Calories",
                                value: String(viewModel.caloriesBurned),
                                color: KaloTheme.mint
                            )
                        }
                    }
                    .padding(20)
                    .background(Color.white)
                    .cornerRadius(20)
                    .padding(.horizontal, 16)
                    
                    // MARK: - Distance Input (Manual)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Manual Distance (meters)")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)
                        
                        HStack {
                            TextField("Enter distance", text: $manualDistance)
                                .font(.system(size: 16, weight: .semibold))
                                .keyboardType(.decimalPad)
                                .padding(12)
                                .background(Color.white)
                                .cornerRadius(10)
                            
                            Button(action: {
                                if let distance = Float(manualDistance) {
                                    viewModel.updateDistance(distance)
                                }
                            }) {
                                Image(systemName: "checkmark.circle.fill")
                                    .font(.system(size: 20))
                                    .foregroundColor(KaloTheme.mint)
                                    .padding(.horizontal, 12)
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                    
                    Spacer()
                    
                    // MARK: - Control Buttons
                    VStack(spacing: 12) {
                        if !viewModel.isRunning {
                            Button(action: {
                                Task {
                                    await viewModel.startRun()
                                }
                            }) {
                                HStack {
                                    Image(systemName: "play.circle.fill")
                                        .font(.system(size: 20))
                                    
                                    Text("Start Run")
                                        .font(.system(size: 16, weight: .semibold))
                                }
                                .frame(maxWidth: .infinity)
                                .padding(16)
                                .background(KaloTheme.mint)
                                .foregroundColor(.white)
                                .cornerRadius(14)
                            }
                        } else {
                            HStack(spacing: 12) {
                                Button(action: { showFinishAlert = true }) {
                                    HStack {
                                        Image(systemName: "stop.circle.fill")
                                            .font(.system(size: 20))
                                        
                                        Text("Finish")
                                            .font(.system(size: 16, weight: .semibold))
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background(Color(red: 1, green: 0.3, blue: 0.3))
                                    .foregroundColor(.white)
                                    .cornerRadius(14)
                                }
                                
                                Button(action: { viewModel.cancelRun() }) {
                                    Image(systemName: "xmark.circle.fill")
                                        .font(.system(size: 20))
                                        .foregroundColor(.secondary)
                                        .padding(16)
                                        .background(Color.white)
                                        .cornerRadius(14)
                                }
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 20)
                }
            }
            .alert("Finish Run?", isPresented: $showFinishAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Finish") {
                    Task {
                        await viewModel.finishRun()
                        if viewModel.finishedRun != nil {
                            dismiss()
                        }
                    }
                }
            } message: {
                Text("Save this run? You've covered \(ActivityViewModel.formatDistance(viewModel.distance_m)) in \(formatTime(viewModel.elapsedSeconds)).")
            }
            .alert("Error", isPresented: .constant(viewModel.error != nil)) {
                Button("OK") { viewModel.error = nil }
            } message: {
                if let error = viewModel.error {
                    Text(error)
                }
            }
        }
    }
    
    private func formatTime(_ seconds: Int) -> String {
        let hours = seconds / 3600
        let minutes = (seconds % 3600) / 60
        let secs = seconds % 60
        return String(format: "%02d:%02d:%02d", hours, minutes, secs)
    }
}

struct StatBox: View {
    let label: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text(label)
                .font(.system(size: 11, weight: .medium))
                .foregroundColor(.secondary)
            
            Text(value)
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
    }
}

#Preview {
    RunTrackingView()
}
