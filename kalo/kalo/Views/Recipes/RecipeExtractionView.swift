import SwiftUI
import PhotosUI

struct RecipeExtractionView: View {
    @State private var viewModel = RecipeExtractionViewModel()
    @FocusState private var isInputFocused: Bool
    @State private var selectedImage: UIImage?
    @State private var selectedPhotoItem: PhotosPickerItem?
    @State private var showCamera = false
    @State private var selectedVideo: URL?
    
    var body: some View {
        ZStack {
            Color.gray.opacity(0.15).ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "video.badge.plus")
                            .font(.title3)
                            .foregroundColor(KaloTheme.mint)
                        
                        Text("Extract Recipe")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.black)
                        
                        Spacer()
                    }
                    .padding(16)
                }
                .background(Color.white)
                .border(width: 1, edges: [.bottom], color: KaloTheme.divider)
                
                ScrollView {
                    VStack(spacing: 16) {
                        // Image/Video Picker Section
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Upload Image or Video")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.black)
                            
                            HStack(spacing: 12) {
                                // Photo Picker
                                PhotosPicker(selection: $selectedPhotoItem, matching: .images) {
                                    VStack(spacing: 8) {
                                        Image(systemName: "photo.on.rectangle")
                                            .font(.system(size: 24))
                                            .foregroundColor(KaloTheme.mint)
                                        Text("Choose Image")
                                            .font(.system(size: 12, weight: .medium))
                                            .foregroundColor(.black)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background(Color.white)
                                    .cornerRadius(8)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(KaloTheme.mint, lineWidth: 1)
                                    )
                                }
                                .disabled(viewModel.isExtracting)
                                
                                // Camera Button
                                Button(action: { showCamera = true }) {
                                    VStack(spacing: 8) {
                                        Image(systemName: "camera")
                                            .font(.system(size: 24))
                                            .foregroundColor(KaloTheme.mint)
                                        Text("Take Photo")
                                            .font(.system(size: 12, weight: .medium))
                                            .foregroundColor(.black)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background(Color.white)
                                    .cornerRadius(8)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(KaloTheme.mint, lineWidth: 1)
                                    )
                                }
                                .disabled(viewModel.isExtracting)
                            }
                            
                            // Selected Image Preview
                            if let image = selectedImage {
                                VStack(spacing: 8) {
                                    Image(uiImage: image)
                                        .resizable()
                                        .scaledToFit()
                                        .frame(height: 200)
                                        .cornerRadius(8)
                                    
                                    HStack {
                                        Button(action: {
                                            selectedImage = nil
                                            selectedPhotoItem = nil
                                        }) {
                                            Text("Remove")
                                                .font(.system(size: 12, weight: .medium))
                                                .foregroundColor(.red)
                                        }
                                        
                                        Spacer()
                                        
                                        Button(action: {
                                            Task {
                                                await viewModel.extractFromImage(image)
                                            }
                                        }) {
                                            HStack {
                                                if viewModel.isExtracting {
                                                    ProgressView()
                                                        .progressViewStyle(.circular)
                                                        .tint(KaloTheme.mint)
                                                } else {
                                                    Image(systemName: "wand.and.stars")
                                                        .foregroundColor(KaloTheme.mint)
                                                }
                                                Text("Extract Recipe")
                                                    .font(.system(size: 12, weight: .semibold))
                                                    .foregroundColor(KaloTheme.mint)
                                            }
                                            .padding(.horizontal, 16)
                                            .padding(.vertical, 8)
                                            .background(KaloTheme.mint.opacity(0.1))
                                            .cornerRadius(8)
                                        }
                                        .disabled(viewModel.isExtracting)
                                    }
                                }
                                .padding(.top, 8)
                            }
                        }
                        .padding(16)
                        .background(Color.white)
                        .cornerRadius(12)
                        
                        // Divider
                        HStack {
                            VStack { Divider() }
                            Text("OR")
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(.gray)
                                .padding(.horizontal, 8)
                            VStack { Divider() }
                        }
                        .padding(.vertical, 8)
                        
                        // Input Section
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Video URL")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.black)
                            
                            HStack {
                                TextField("Paste TikTok, Instagram, or YouTube URL", text: $viewModel.videoURL)
                                    .textFieldStyle(.roundedBorder)
                                    .focused($isInputFocused)
                                    .disabled(viewModel.isExtracting)
                                
                                if !viewModel.videoURL.isEmpty {
                                    Button(action: { viewModel.videoURL = "" }) {
                                        Image(systemName: "xmark.circle.fill")
                                            .foregroundColor(.gray)
                                    }
                                }
                            }
                            
                            if let error = viewModel.error {
                                Text(error)
                                    .font(.system(size: 12))
                                    .foregroundColor(.red)
                            }
                        }
                        .padding(16)
                        .background(Color.white)
                        .cornerRadius(12)
                        
                        // Extract Button
                        Button(action: {
                            Task {
                                await viewModel.extractRecipe(from: viewModel.videoURL)
                            }
                        }) {
                            HStack {
                                if viewModel.isExtracting {
                                    ProgressView()
                                        .progressViewStyle(.circular)
                                        .tint(.white)
                                } else {
                                    Image(systemName: "wand.and.stars")
                                }
                                
                                Text(viewModel.isExtracting ? "Extracting..." : "Extract Recipe")
                                    .font(.system(size: 14, weight: .semibold))
                            }
                            .frame(maxWidth: .infinity)
                            .padding(12)
                            .background(KaloTheme.mint)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }
                        .disabled(viewModel.videoURL.isEmpty || viewModel.isExtracting)
                        .padding(.top, 8)
                        
                        // Progress
                        if !viewModel.extractionProgress.isEmpty {
                            Text(viewModel.extractionProgress)
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                                .padding(16)
                        }
                        
                        // Extracted Recipe
                        if let recipe = viewModel.extractedRecipe {
                            RecipeExtractedCard(recipe: recipe)
                                .padding(.top, 8)
                        }
                    }
                    .padding(16)
                    .padding(.vertical, 16)
                }
            }
        }
        .navigationTitle("")
        #if os(iOS)
        .navigationBarTitleDisplayMode(.inline)
        #endif
        .onChange(of: selectedPhotoItem) { _, newItem in
            Task {
                if let data = try? await newItem?.loadTransferable(type: Data.self),
                   let image = UIImage(data: data) {
                    selectedImage = image
                }
            }
        }
        .sheet(isPresented: $showCamera) {
            ImagePicker(image: $selectedImage, sourceType: .camera)
        }
    }
}

// MARK: - Image Picker for Camera
struct ImagePicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    let sourceType: UIImagePickerController.SourceType
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = sourceType
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker
        
        init(_ parent: ImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.image = image
            }
            parent.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

// MARK: - Extracted Recipe Card
struct RecipeExtractedCard: View {
    let recipe: RecipeExtractionResponse
    @State private var isSaved = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Title & Save Button
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(recipe.title ?? "Recipe")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.black)
                    
                    if let difficulty = recipe.difficulty {
                        Text("Difficulty: \(difficulty)")
                            .font(.system(size: 12))
                            .foregroundColor(.gray)
                    }
                }
                
                Spacer()
                
                Button(action: { isSaved.toggle() }) {
                    Image(systemName: isSaved ? "bookmark.fill" : "bookmark")
                        .font(.system(size: 16))
                        .foregroundColor(isSaved ? KaloTheme.mint : .gray)
                }
            }
            
            Divider()
            
            // Metadata
            HStack(spacing: 16) {
                if let cookTime = recipe.cookTimeMinutes {
                    VStack(alignment: .center, spacing: 4) {
                        Image(systemName: "clock")
                            .font(.system(size: 14))
                            .foregroundColor(.gray)
                        Text("\(cookTime)m")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.black)
                    }
                }
                
                if let servings = recipe.servings {
                    VStack(alignment: .center, spacing: 4) {
                        Image(systemName: "person.2")
                            .font(.system(size: 14))
                            .foregroundColor(.gray)
                        Text("\(servings)")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(.black)
                    }
                }
            }
            
            // Macros
            if let macros = recipe.macros {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Nutrition (per serving)")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(.gray)
                    
                    HStack(spacing: 12) {
                        MacroWidget(label: "Cal", value: Int(macros.calories ?? 0), color: KaloTheme.mint)
                        MacroWidget(label: "P", value: Int(macros.protein ?? 0), color: .orange)
                        MacroWidget(label: "C", value: Int(macros.carbs ?? 0), color: .blue)
                        MacroWidget(label: "F", value: Int(macros.fat ?? 0), color: .red)
                    }
                }
                .padding(.vertical, 8)
            }
            
            // Ingredients
            VStack(alignment: .leading, spacing: 8) {
                Text("Ingredients")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.gray)
                
                ForEach(recipe.ingredients ?? [], id: \.id) { ingredient in
                    HStack(spacing: 8) {
                        Circle()
                            .fill(KaloTheme.mint)
                            .frame(width: 4, height: 4)
                        
                        Text(ingredient.name)
                            .font(.system(size: 12))
                            .foregroundColor(.black)
                        
                        if let quantity = ingredient.quantity, let unit = ingredient.unit {
                            Text("(\(String(format: "%.1f", quantity)) \(unit))")
                                .font(.system(size: 11))
                                .foregroundColor(.gray)
                        }
                    }
                }
            }
            
            // Steps
            VStack(alignment: .leading, spacing: 8) {
                Text("Steps")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.gray)
                
                ForEach(recipe.steps ?? [], id: \.id) { step in
                    HStack(alignment: .top, spacing: 8) {
                        Text("\(step.step)")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(KaloTheme.mint)
                            .frame(width: 20)
                        
                        Text(step.instruction)
                            .font(.system(size: 12))
                            .foregroundColor(.black)
                            .lineLimit(nil)
                    }
                }
            }
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(12)
    }
}

// MARK: - Macro Widget
struct MacroWidget: View {
    let label: String
    let value: Int
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text("\(value)")
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(color)
            
            Text(label)
                .font(.system(size: 10))
                .foregroundColor(.gray)
        }
        .frame(width: 50)
        .padding(6)
        .background(color.opacity(0.1))
        .cornerRadius(6)
    }
}

#Preview {
    RecipeExtractionView()
}
