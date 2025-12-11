import SwiftUI

struct AIChatView: View {
    @State private var viewModel = AIChatViewModel()
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: 8) {
                HStack {
                    Image(systemName: "sparkles")
                        .font(.title3)
                        .foregroundColor(KaloTheme.mint)
                    
                    Text("Kalo AI Assistant")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.black)
                    
                    Spacer()
                    
                    Button(action: { viewModel.clearMessages() }) {
                        Image(systemName: "arrow.clockwise")
                            .font(.system(size: 14))
                            .foregroundColor(KaloTheme.mint)
                            .padding(8)
                    }
                }
                .padding(16)
            }
            .background(Color.white)
            .border(width: 1, edges: [.bottom], color: KaloTheme.divider)
            
            // Messages
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(viewModel.messages) { message in
                            ChatBubble(message: message)
                                .id(message.id)
                        }
                        
                        if viewModel.showTypingIndicator {
                            TypingIndicator()
                                .id("typing")
                        }
                    }
                    .padding(16)
                    .onChange(of: viewModel.messages.count) { _, _ in
                        withAnimation {
                            proxy.scrollTo(viewModel.messages.last?.id, anchor: .bottom)
                        }
                    }
                }
            }
            .background(Color.gray.opacity(0.15))
            
            // Input Area
            VStack(spacing: 0) {
                Divider()
                    .padding(0)
                
                HStack(spacing: 12) {
                    TextField("Message...", text: $viewModel.currentInput)
                        .textFieldStyle(.roundedBorder)
                        .focused($isInputFocused)
                        .frame(minHeight: 36)
                    
                    Button(action: {
                        Task {
                            await viewModel.sendMessage(viewModel.currentInput)
                        }
                    }) {
                        Image(systemName: "paperplane.fill")
                            .font(.system(size: 16))
                            .foregroundColor(.white)
                            .frame(width: 36, height: 36)
                            .background(KaloTheme.mint)
                            .cornerRadius(8)
                    }
                    .disabled(viewModel.currentInput.trimmingCharacters(in: .whitespaces).isEmpty || viewModel.isLoading)
                }
                .padding(12)
                .background(Color.white)
            }
        }
        .background(Color.white)
    }
}

// MARK: - Chat Bubble
struct ChatBubble: View {
    let message: AIMessage
    
    var body: some View {
        HStack {
            if message.isUserMessage {
                Spacer()
            }
            
            Text(message.content)
                .font(.system(size: 14))
                .foregroundColor(message.isUserMessage ? .white : .black)
                .padding(12)
                .background(message.isUserMessage ? KaloTheme.mint : Color.white)
                .cornerRadius(12)
                .lineLimit(nil)
            
            if !message.isUserMessage {
                Spacer()
            }
        }
    }
}

// MARK: - Typing Indicator
struct TypingIndicator: View {
    @State private var animationIndex = 0
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<3, id: \.self) { index in
                Circle()
                    .fill(KaloTheme.mint)
                    .frame(width: 8, height: 8)
                    .scaleEffect(animationIndex == index ? 1.2 : 0.8)
                    .opacity(animationIndex == index ? 1.0 : 0.5)
            }
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(12)
        .onAppear {
            let timer = Timer.scheduledTimer(withTimeInterval: 0.4, repeats: true) { _ in
                withAnimation(.easeInOut(duration: 0.3)) {
                    animationIndex = (animationIndex + 1) % 3
                }
            }
            RunLoop.current.add(timer, forMode: .common)
        }
    }
}

// MARK: - Border Modifier
struct BorderModifier: ViewModifier {
    let width: CGFloat
    let edges: Edge.Set
    let color: Color
    
    func body(content: Content) -> some View {
        content
            .overlay(alignment: .bottom) {
                if edges.contains(.bottom) {
                    color.frame(height: width)
                }
            }
            .overlay(alignment: .top) {
                if edges.contains(.top) {
                    color.frame(height: width)
                }
            }
            .overlay(alignment: .leading) {
                if edges.contains(.leading) {
                    color.frame(width: width)
                }
            }
            .overlay(alignment: .trailing) {
                if edges.contains(.trailing) {
                    color.frame(width: width)
                }
            }
    }
}

extension View {
    func border(width: CGFloat, edges: Edge.Set, color: Color) -> some View {
        modifier(BorderModifier(width: width, edges: edges, color: color))
    }
}

#Preview {
    AIChatView()
}
