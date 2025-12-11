import SwiftUI

/// Chat bottom sheet / modal with beautiful App Store-style design
struct ChatBottomSheetView: View {
    @Binding var isPresented: Bool
    @State private var aiChatVM = AIChatViewModel(coachMode: true)
    @FocusState private var isInputFocused: Bool
    @State private var offset: CGFloat = 0
    
    var body: some View {
        ZStack {
            // Dimming background with blur
            if isPresented {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()
                    .onTapGesture {
                        dismissSheet()
                    }
            }
            
            // Sheet content with modern design
            VStack(spacing: 0) {
                // Drag indicator + header
                VStack(spacing: 0) {
                    // Drag handle
                    Capsule()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: 36, height: 5)
                        .padding(.top, 12)
                        .padding(.bottom, 16)
                    
                    // Modern header with gradient accent
                    VStack(spacing: 8) {
                        HStack {
                            ZStack {
                                LinearGradient(
                                    colors: [KaloTheme.mint, KaloTheme.mint.opacity(0.7)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                                .frame(width: 44, height: 44)
                                .cornerRadius(12)
                                
                                Image(systemName: "sparkles")
                                    .font(.system(size: 20, weight: .semibold))
                                    .foregroundColor(.white)
                            }
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text("AI Coach")
                                    .font(.system(size: 22, weight: .bold))
                                    .foregroundColor(KaloTheme.text)
                                
                                Text("Your personal fitness & nutrition expert")
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
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 16)
                    .background(.ultraThinMaterial)
                }
                
                // Messages area with gradient background
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
                
                // Modern input area with elevated design
                VStack(spacing: 0) {
                    Divider()
                        .background(Color.gray.opacity(0.2))
                    
                    HStack(spacing: 12) {
                        // Text input with subtle shadow
                        HStack {
                            TextField("Ask me anything...", text: $aiChatVM.currentInput, axis: .vertical)
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
                        
                        // Send button with gradient
                        Button(action: {
                            Task {
                                await aiChatVM.sendMessage(aiChatVM.currentInput)
                            }
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
    
    private func dismissSheet() {
        isInputFocused = false
        withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) {
            isPresented = false
        }
    }
}

/// Modern chat bubble with beautiful styling
struct ModernChatBubble: View {
    let message: AIMessage
    
    var body: some View {
        HStack(alignment: .bottom, spacing: 8) {
            if message.isUserMessage {
                Spacer(minLength: 60)
            }
            
            if !message.isUserMessage {
                // AI avatar
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [KaloTheme.mint.opacity(0.2), KaloTheme.mint.opacity(0.1)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 32, height: 32)
                    
                    Image(systemName: "sparkles")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(KaloTheme.mint)
                }
            }
            
            VStack(alignment: message.isUserMessage ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .font(.system(size: 15, weight: .regular))
                    .foregroundColor(message.isUserMessage ? .white : KaloTheme.text)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(
                        Group {
                            if message.isUserMessage {
                                LinearGradient(
                                    colors: [KaloTheme.mint, KaloTheme.mint.opacity(0.85)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            } else {
                                Color(.systemBackground)
                            }
                        }
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                    .shadow(color: .black.opacity(0.05), radius: 4, y: 2)
                
                Text(message.timestamp, style: .time)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 4)
            }
            
            if !message.isUserMessage {
                Spacer(minLength: 60)
            }
        }
    }
}

/// Modern typing indicator with animation
struct ModernTypingIndicator: View {
    @State private var animationIndex = 0
    
    var body: some View {
        HStack(alignment: .bottom, spacing: 8) {
            // AI avatar
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [KaloTheme.mint.opacity(0.2), KaloTheme.mint.opacity(0.1)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 32, height: 32)
                
                Image(systemName: "sparkles")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(KaloTheme.mint)
            }
            
            HStack(spacing: 6) {
                ForEach(0..<3, id: \.self) { index in
                    Circle()
                        .fill(KaloTheme.mint.opacity(0.6))
                        .frame(width: 8, height: 8)
                        .scaleEffect(animationIndex == index ? 1.3 : 0.7)
                        .opacity(animationIndex == index ? 1.0 : 0.4)
                        .animation(
                            .easeInOut(duration: 0.6).repeatForever(autoreverses: false).delay(Double(index) * 0.2),
                            value: animationIndex
                        )
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color(.systemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
            .shadow(color: .black.opacity(0.05), radius: 4, y: 2)
            
            Spacer(minLength: 60)
        }
        .onAppear {
            animationIndex = 1
        }
    }
}

#Preview {
    ZStack {
        Color.gray.ignoresSafeArea()
        
        ChatBottomSheetView(isPresented: .constant(true))
    }
}
