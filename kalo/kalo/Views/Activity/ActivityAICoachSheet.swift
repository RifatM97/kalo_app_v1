import SwiftUI

/// AI Coach sheet specifically for Activity/Training context
struct ActivityAICoachSheet: View {
    @Binding var isPresented: Bool
    let activityContext: String
    @State private var aiChatVM: AIChatViewModel
    @FocusState private var isInputFocused: Bool
    @State private var offset: CGFloat = 0
    
    init(isPresented: Binding<Bool>, activityContext: String) {
        self._isPresented = isPresented
        self.activityContext = activityContext
        self._aiChatVM = State(initialValue: AIChatViewModel(coachMode: true))
    }
    
    var body: some View {
        ZStack {
            // Dimming background
            if isPresented {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()
                    .onTapGesture {
                        dismissSheet()
                    }
            }
            
            // Sheet content
            VStack(spacing: 0) {
                // Header
                VStack(spacing: 0) {
                    // Drag handle
                    Capsule()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: 36, height: 5)
                        .padding(.top, 12)
                        .padding(.bottom, 16)
                    
                    // Header with context indicator
                    VStack(spacing: 12) {
                        HStack {
                            ZStack {
                                LinearGradient(
                                    colors: [KaloTheme.mint, KaloTheme.mint.opacity(0.7)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                                .frame(width: 44, height: 44)
                                .cornerRadius(12)
                                
                                Image(systemName: "figure.run")
                                    .font(.system(size: 20, weight: .semibold))
                                    .foregroundColor(.white)
                            }
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Training Coach")
                                    .font(.system(size: 22, weight: .bold))
                                    .foregroundColor(KaloTheme.text)
                                
                                Text("Personalized advice based on your activity")
                                    .font(.system(size: 13, weight: .medium))
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                            
                            Button(action: { dismissSheet() }) {
                                Image(systemName: "xmark.circle.fill")
                                    .font(.system(size: 28))
                                    .foregroundColor(.gray.opacity(0.3))
                                    .symbolRenderingMode(.hierarchical)
                            }
                        }
                        
                        // Context preview card
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "chart.bar.fill")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundColor(KaloTheme.mint)
                                
                                Text("Your Activity Data Loaded")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundColor(KaloTheme.mint)
                                
                                Spacer()
                                
                                Image(systemName: "checkmark.circle.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.green)
                            }
                            
                            Text("AI Coach has access to your recent runs, stats, and personal records")
                                .font(.system(size: 11, weight: .medium))
                                .foregroundColor(.secondary)
                        }
                        .padding(12)
                        .background(Color(.systemGray6))
                        .cornerRadius(12)
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 16)
                    .background(.ultraThinMaterial)
                }
                
                // Messages area
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 16) {
                            ForEach(aiChatVM.messages) { message in
                                ModernChatBubble(message: message)
                                    .id(message.id)
                            }
                            
                            if aiChatVM.showTypingIndicator {
                                ModernTypingIndicator()
                                    .id("typing")
                            }
                        }
                        .padding(20)
                        .onChange(of: aiChatVM.messages.count) { _, _ in
                            withAnimation(.easeOut(duration: 0.3)) {
                                proxy.scrollTo(aiChatVM.messages.last?.id, anchor: .bottom)
                            }
                        }
                    }
                }
                .background(
                    LinearGradient(
                        colors: [
                            Color(.systemBackground),
                            Color(.systemGray6).opacity(0.3)
                        ],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                
                // Suggested questions
                if aiChatVM.messages.count <= 1 {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            SuggestedQuestionButton(
                                text: "How can I improve my pace?",
                                action: {
                                    sendSuggestedQuestion("How can I improve my running pace? Here's my recent data: \(activityContext)")
                                }
                            )
                            SuggestedQuestionButton(
                                text: "Training plan for 5K",
                                action: {
                                    sendSuggestedQuestion("Can you create a training plan to help me improve my 5K time? Here's my current fitness level: \(activityContext)")
                                }
                            )
                            SuggestedQuestionButton(
                                text: "Recovery advice",
                                action: {
                                    sendSuggestedQuestion("What recovery strategies should I use based on my recent training volume? \(activityContext)")
                                }
                            )
                        }
                        .padding(.horizontal, 20)
                    }
                    .padding(.vertical, 12)
                    .background(.ultraThinMaterial)
                }
                
                // Input area
                VStack(spacing: 0) {
                    Divider()
                        .background(Color.gray.opacity(0.2))
                    
                    HStack(spacing: 12) {
                        HStack {
                            TextField("Ask about your training...", text: $aiChatVM.currentInput, axis: .vertical)
                                .textFieldStyle(.plain)
                                .focused($isInputFocused)
                                .lineLimit(1...4)
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                        }
                        .background(Color(.systemGray6))
                        .cornerRadius(20)
                        .overlay(
                            RoundedRectangle(cornerRadius: 20, style: .continuous)
                                .stroke(KaloTheme.mint.opacity(isInputFocused ? 0.5 : 0), lineWidth: 2)
                        )
                        
                        Button(action: {
                            sendMessage()
                        }) {
                            ZStack {
                                LinearGradient(
                                    colors: aiChatVM.currentInput.trimmingCharacters(in: .whitespaces).isEmpty
                                        ? [Color.gray.opacity(0.3), Color.gray.opacity(0.2)]
                                        : [KaloTheme.mint, KaloTheme.mint.opacity(0.8)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                                .frame(width: 44, height: 44)
                                .cornerRadius(22)
                                
                                Image(systemName: "arrow.up")
                                    .font(.system(size: 18, weight: .bold))
                                    .foregroundColor(.white)
                            }
                        }
                        .disabled(aiChatVM.currentInput.trimmingCharacters(in: .whitespaces).isEmpty || aiChatVM.isLoading)
                    }
                    .padding(16)
                    .background(.ultraThinMaterial)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
            .shadow(color: .black.opacity(0.2), radius: 20, y: -5)
            .ignoresSafeArea(edges: .bottom)
            .offset(y: offset)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        if value.translation.height > 0 {
                            offset = value.translation.height
                        }
                    }
                    .onEnded { value in
                        if value.translation.height > 150 {
                            dismissSheet()
                        } else {
                            withAnimation(.spring()) {
                                offset = 0
                            }
                        }
                    }
            )
        }
        .animation(.spring(response: 0.5, dampingFraction: 0.8), value: isPresented)
    }
    
    private func sendMessage() {
        let messageWithContext = aiChatVM.currentInput
        Task {
            let context = ChatContext(
                goals: "Running and endurance training",
                recentWorkouts: activityContext,
                stats: nil
            )
            await aiChatVM.sendMessage(messageWithContext, context: context)
        }
    }
    
    private func sendSuggestedQuestion(_ question: String) {
        Task {
            let context = ChatContext(
                goals: "Running and endurance training",
                recentWorkouts: activityContext,
                stats: nil
            )
            await aiChatVM.sendMessage(question, context: context)
        }
    }
    
    private func dismissSheet() {
        isInputFocused = false
        withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
            isPresented = false
        }
    }
}

// MARK: - Suggested Question Button
struct SuggestedQuestionButton: View {
    let text: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(text)
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(KaloTheme.mint)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(Color(.systemBackground))
                .cornerRadius(20)
                .overlay(
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .stroke(KaloTheme.mint.opacity(0.3), lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    ActivityAICoachSheet(
        isPresented: .constant(true),
        activityContext: "Recent runs: 5km at 5:30/km, 10km at 6:00/km"
    )
}
