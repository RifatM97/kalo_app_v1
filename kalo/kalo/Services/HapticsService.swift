import SwiftUI

#if os(iOS)
import UIKit

/**
 HapticsService - Provides safe haptic feedback without pattern library errors
 
 Uses only standard UIImpactFeedbackGenerator & UINotificationFeedbackGenerator
 to avoid missing hapticpatternlibrary.plist errors on simulators.
 Available exclusively on iOS.
 */
final class HapticsService {
    static let shared = HapticsService()
    private init() {}
    
    // MARK: - Impact Feedback (Haptic Engine)
    enum ImpactStyle {
        case light
        case medium
        case heavy
        
        var intensity: UIImpactFeedbackGenerator.FeedbackStyle {
            switch self {
            case .light:
                return .light
            case .medium:
                return .medium
            case .heavy:
                return .heavy
            }
        }
    }
    
    /// Trigger impact haptic feedback
    /// Safe for simulator and device
    func impact(_ style: ImpactStyle = .medium) {
        DispatchQueue.main.async {
            let generator = UIImpactFeedbackGenerator(style: style.intensity)
            generator.prepare()
            generator.impactOccurred()
        }
    }
    
    // MARK: - Notification Feedback
    enum NotificationStyle {
        case success
        case warning
        case error
        
        var type: UINotificationFeedbackGenerator.FeedbackType {
            switch self {
            case .success:
                return .success
            case .warning:
                return .warning
            case .error:
                return .error
            }
        }
    }
    
    /// Trigger notification haptic feedback
    func notification(_ style: NotificationStyle) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(style.type)
    }
    
    // MARK: - Selection Feedback
    /// Trigger selection feedback (light tap, minimal vibration)
    func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }
}

#else

// MARK: - macOS Stub
/// Stub implementation for non-iOS platforms (macOS, etc.)
/// Methods are no-ops on macOS.
final class HapticsService {
    static let shared = HapticsService()
    private init() {}
    
    enum ImpactStyle {
        case light, medium, heavy
    }
    
    enum NotificationStyle {
        case success, warning, error
    }
    
    func impact(_ style: ImpactStyle = .medium) {
        // No-op on macOS
    }
    
    func notification(_ style: NotificationStyle) {
        // No-op on macOS
    }
    
    func selection() {
        // No-op on macOS
    }
}

#endif

// MARK: - Convenience Extension for SwiftUI
extension View {
    /// Add haptic feedback to any view action
    /// Example: Button("Press") { }
    ///     .withHaptics()
    func withHaptics(_ hapticAction: @escaping () -> Void = {}) -> some View {
        self.onTapGesture {
            HapticsService.shared.impact()
            hapticAction()
        }
    }
}
