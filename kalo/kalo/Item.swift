//
//  Item.swift
//  kalo
//
//  Created by Arafat Hossain Shake Mohammed on 05/12/2025.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
