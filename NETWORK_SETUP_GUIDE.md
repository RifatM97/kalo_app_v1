# KALO Network Configuration & Troubleshooting Guide

## 🔧 PHASE 1 FIXES IMPLEMENTED

### ✅ iOS Networking
- **Enhanced Config.swift** with environment support (development, devRemote, staging, production)
- **Improved NetworkingService** with health check endpoint, better error handling
- **Added HapticsService** - safe haptic feedback without pattern library errors
- **Connection timeout** and **request timeout** configuration added

### ✅ Backend API
- **Health check endpoint** (`/health`) for quick connectivity test
- **Verbose health check** (`/health/verbose`) for detailed diagnostics
- All 10 API routers registered and ready

---

## 📱 SETUP INSTRUCTIONS

### **For iOS Simulator (Localhost)**

Your iOS simulator running on the Mac can directly access `localhost:8000`:

```swift
// Config.swift (already set in code)
private static let activeEnvironment: Environment = .development
// This uses: http://localhost:8000
```

**To test:**
```bash
# 1. Start backend
cd /Users/rifathossain/Desktop/kalo/kalo-backend
python main.py

# 2. Verify backend is running
curl http://localhost:8000/health
# Expected response:
# {"status": "healthy", "service": "kalo-api", "version": "1.0.0", ...}

# 3. In Xcode, build & run on simulator
# Should work immediately!
```

---

### **For Physical iPhone/iPad (Not Simulator)**

Physical devices **cannot** use `localhost` since it refers to the device itself, not your Mac.

**Option A: Use Your Mac's Local IP**

1. Find your Mac's local IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Example output: 192.168.1.100
```

2. Update Config.swift:
```swift
enum APIConfig {
    private static let activeEnvironment: Environment = .devRemote
    
    private static func baseURLForEnvironment(_ env: Environment) -> URL {
        switch env {
        case .devRemote:
            return URL(string: "http://192.168.1.100:8000")!  // ← YOUR IP HERE
        //...
        }
    }
}
```

3. Start backend (make sure it's accessible from network):
```bash
python main.py
# Should print: "Uvicorn running on http://0.0.0.0:8000"
```

4. On iPhone, connect to same WiFi network
5. Build & run on device

---

## 🧪 TESTING CONNECTIVITY

### **Option 1: Using NetworkingService Health Check**

Create a simple test view:

```swift
@main
struct KaloApp: App {
    @State private var healthStatus: String = "Checking..."
    
    var body: some Scene {
        WindowGroup {
            VStack(spacing: 20) {
                Text("Health Check")
                    .font(.title)
                
                Text(healthStatus)
                    .foregroundColor(.secondary)
                
                Button("Test Connection") {
                    Task {
                        do {
                            let isHealthy = try await NetworkingService.shared.checkConnectivity()
                            healthStatus = isHealthy ? "✅ Connected!" : "❌ Not connected"
                        } catch let error as NetworkError {
                            healthStatus = "❌ \(error.errorDescription ?? "Unknown error")"
                        }
                    }
                }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .padding()
        }
    }
}
```

### **Option 2: Using curl (Terminal)**

```bash
# Quick check
curl http://localhost:8000/health

# Detailed check
curl http://localhost:8000/health/verbose

# With verbose output
curl -v http://localhost:8000/health
```

### **Option 3: Using Postman**

1. Create new request
2. Method: **GET**
3. URL: `http://localhost:8000/health`
4. Send
5. Should return 200 OK with JSON response

---

## 🐛 TROUBLESHOOTING

### **Error: "Cannot connect to the server"**

**Cause**: Backend not running on port 8000

**Fix**:
```bash
# 1. Check if port 8000 is in use
lsof -i :8000

# 2. If nothing shows, backend isn't running
# Start it:
cd /Users/rifathossain/Desktop/kalo/kalo-backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Verify:
curl http://localhost:8000/health
```

---

### **Error: "Connection refused (errno 61)"**

**Cause**: iOS trying to connect but backend isn't listening

**Fix**:
```bash
# On Mac terminal:
python main.py

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# If not, check for Python errors
```

---

### **Error: "Could not connect to the server" (Physical Device)**

**Cause**: Device can't reach your Mac's IP

**Fix**:
1. Verify both devices on same WiFi: `Settings → WiFi`
2. Ping Mac from iPhone:
   - Open Terminal on Mac: `ifconfig | grep inet`
   - On iPhone: Safari → `http://YOUR_IP:8000/health`
   - Should show JSON response
3. If still fails:
   - Check firewall: `System Preferences → Security & Privacy → Firewall`
   - Try: `System Preferences → Network → Advanced → Options → Allow UPnP`

---

### **Error: Haptics Pattern Library Missing**

**Cause**: Simulator trying to use CHHapticPattern (real device feature)

**Fix**: ✅ ALREADY IMPLEMENTED
- Use `HapticsService.shared.impact()` instead of direct haptic patterns
- HapticsService uses UIImpactFeedbackGenerator (safe on simulator & device)

```swift
// ❌ Don't do this:
// CHHapticPattern.patternForKey...  // Will fail on simulator

// ✅ Do this instead:
HapticsService.shared.impact(.medium)
HapticsService.shared.notification(.success)
HapticsService.shared.selection()
```

---

## 📊 API ENDPOINTS FOR TESTING

Once backend is running, test these in Postman/curl:

```bash
# Health checks
GET  http://localhost:8000/health
GET  http://localhost:8000/health/verbose

# Auth (example)
POST http://localhost:8000/api/auth/register
POST http://localhost:8000/api/auth/login

# Users
GET  http://localhost:8000/api/users/me

# Runs (Activity)
GET  http://localhost:8000/api/runs
GET  http://localhost:8000/api/runs/summary/stats?period=week

# Challenges (Activity)
GET  http://localhost:8000/api/challenges
GET  http://localhost:8000/api/challenges/{id}

# Workouts
GET  http://localhost:8000/api/workouts
POST http://localhost:8000/api/workouts

# Full API docs
GET  http://localhost:8000/docs  (interactive Swagger UI)
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Backend running: `python main.py`
- [ ] Health check works: `curl http://localhost:8000/health` returns 200
- [ ] iOS Config.swift has correct environment
- [ ] iOS builds without errors
- [ ] iOS simulator connects and shows health status ✅
- [ ] Haptics working without console errors

---

## 🚀 NEXT STEPS

Once network is stable:

1. **PHASE 2**: Verify all endpoint signatures match iOS expectations
2. **PHASE 3**: Implement Strong-style workouts
3. **PHASE 4**: Running + maps + sharing
4. **PHASE 5**: Social feed
5. **PHASE 6**: Design consistency pass

---

**Questions?** Check the logs:
```bash
# Backend logs in terminal where python main.py is running
# iOS logs in Xcode Console (Cmd+Shift+C)
```
