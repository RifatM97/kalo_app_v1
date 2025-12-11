import SwiftUI

struct KaloButton: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(.vertical, 12)
            .padding(.horizontal, 20)
            .background(Color.kaloMint)
            .foregroundColor(.white)
            .font(.system(.headline, design: .rounded).weight(.semibold))
            .cornerRadius(12)
            .shadow(color: Color.kaloMint.opacity(0.25), radius: 8, x: 0, y: 6)
    }
}

extension View {
    func kaloButtonStyle() -> some View {
        modifier(KaloButton())
    }
}
