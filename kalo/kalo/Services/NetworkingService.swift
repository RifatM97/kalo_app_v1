import Foundation

enum NetworkError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(statusCode: Int)
    case decodingError
    case encodingError
    case unauthorized
    case notFound
    case serverError
    case connectionRefused   // NEW: Server not listening
    case timeout
    case unknown(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .httpError(let code):
            return "HTTP Error \(code)"
        case .decodingError:
            return "Failed to decode response"
        case .encodingError:
            return "Failed to encode request"
        case .unauthorized:
            return "Unauthorized - please login again"
        case .notFound:
            return "Resource not found"
        case .serverError:
            return "Server error (500+)"
        case .connectionRefused:
            return "Cannot connect to server. Is it running on \(APIConfig.baseURL.absoluteString)?"
        case .timeout:
            return "Request timed out. Server may be slow or unreachable."
        case .unknown(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
    
    var isNetworkUnavailable: Bool {
        switch self {
        case .connectionRefused, .timeout:
            return true
        default:
            if case .unknown(let err as NSError) = self {
                return err.code == NSURLErrorNotConnectedToInternet || 
                       err.code == NSURLErrorCannotConnectToHost ||
                       err.code == NSURLErrorCannotFindHost
            }
            return false
        }
    }
}

final class NetworkingService {
    static let shared = NetworkingService()
    private init() {}
    
    private let session = URLSession.shared
    private let decoder = JSONDecoder()
    private let encoder = JSONEncoder()
    
    private var token: String? {
        KeychainHelper.shared.readToken()
    }
    
    // MARK: - Health Check (NEW)
    func checkConnectivity() async throws -> Bool {
        let healthURL = APIConfig.baseURL.appendingPathComponent(APIConfig.healthEndpoint)
        var urlRequest = URLRequest(url: healthURL)
        urlRequest.timeoutInterval = APIConfig.connectionTimeout
        
        do {
            let (_, response) = try await session.data(for: urlRequest)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            return httpResponse.statusCode == 200
        } catch let error as NSError {
            if error.code == NSURLErrorCannotConnectToHost || error.code == 61 {
                throw NetworkError.connectionRefused
            } else if error.code == NSURLErrorTimedOut {
                throw NetworkError.timeout
            }
            throw NetworkError.unknown(error)
        }
    }
    
    // MARK: - Generic Request Method
    func request<T: Decodable>(
        _ endpoint: String,
        method: HTTPMethod = .get,
        body: Encodable? = nil,
        as type: T.Type
    ) async throws -> T {
        let url = APIConfig.baseAPIURL.appendingPathComponent(endpoint)
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = method.rawValue
        urlRequest.timeoutInterval = APIConfig.requestTimeout
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Add authorization token if available
        if let token = token {
            urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Encode body if provided
        if let body = body {
            urlRequest.httpBody = try encoder.encode(AnyEncodable(body))
        }
        
        do {
            let (data, response) = try await session.data(for: urlRequest)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            // Handle different status codes
            switch httpResponse.statusCode {
            case 200...299:
                break
            case 401:
                throw NetworkError.unauthorized
            case 404:
                throw NetworkError.notFound
            case 500...599:
                throw NetworkError.serverError
            default:
                throw NetworkError.httpError(statusCode: httpResponse.statusCode)
            }
            
            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                throw NetworkError.decodingError
            }
        } catch let error as NSError {
            // Map OS-level errors to NetworkError
            if error.code == NSURLErrorCannotConnectToHost ||
               error.code == 61 {  // Connection refused
                throw NetworkError.connectionRefused
            } else if error.code == NSURLErrorTimedOut {
                throw NetworkError.timeout
            } else if error.code == NSURLErrorNotConnectedToInternet {
                throw NetworkError.connectionRefused
            }
            throw NetworkError.unknown(error)
        } catch let networkError as NetworkError {
            throw networkError
        } catch {
            throw NetworkError.unknown(error)
        }
    }
    
    // MARK: - Convenience Methods
    func get<T: Decodable>(_ endpoint: String, as type: T.Type) async throws -> T {
        try await request(endpoint, method: .get, as: type)
    }
    
    func post<T: Decodable>(_ endpoint: String, body: Encodable?, as type: T.Type) async throws -> T {
        try await request(endpoint, method: .post, body: body, as: type)
    }
    
    func put<T: Decodable>(_ endpoint: String, body: Encodable?, as type: T.Type) async throws -> T {
        try await request(endpoint, method: .put, body: body, as: type)
    }
    
    func delete<T: Decodable>(_ endpoint: String, as type: T.Type) async throws -> T {
        try await request(endpoint, method: .delete, as: type)
    }
    
    func delete(_ endpoint: String) async throws {
        let url = APIConfig.baseAPIURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = HTTPMethod.delete.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = APIConfig.requestTimeout
        
        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (_, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        if httpResponse.statusCode >= 400 {
            throw NetworkError.httpError(statusCode: httpResponse.statusCode)
        }
    }
    
    // MARK: - File Upload (Image/Video)
    func uploadFile<T: Decodable>(
        _ endpoint: String,
        fileData: Data,
        fileName: String,
        mimeType: String,
        as type: T.Type
    ) async throws -> T {
        let url = APIConfig.baseAPIURL.appendingPathComponent(endpoint)
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 60 // Longer timeout for uploads
        
        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Create multipart form data
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Add file data
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            switch httpResponse.statusCode {
            case 200...299:
                break
            case 401:
                throw NetworkError.unauthorized
            case 404:
                throw NetworkError.notFound
            case 500...599:
                throw NetworkError.serverError
            default:
                throw NetworkError.httpError(statusCode: httpResponse.statusCode)
            }
            
            return try decoder.decode(T.self, from: data)
        } catch let error as NetworkError {
            throw error
        } catch {
            throw NetworkError.unknown(error)
        }
    }
}

// MARK: - HTTP Methods
enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
    case patch = "PATCH"
}

// MARK: - Helper to encode unknown Encodable types
struct AnyEncodable: Encodable {
    private let encodeFunc: (Encoder) throws -> Void
    
    init<T: Encodable>(_ wrapped: T) {
        encodeFunc = wrapped.encode
    }
    
    func encode(to encoder: Encoder) throws {
        try encodeFunc(encoder)
    }
}
