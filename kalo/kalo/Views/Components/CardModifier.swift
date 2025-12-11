import SwiftUI

struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(Color.white)
            .cornerRadius(16)
            .shadow(color: Color.black.opacity(0.08), radius: 12, x: 0, y: 8)
            .padding(8)
    }
}

extension View {
    func kaloCard() -> some View { modifier(CardModifier()) }
}
