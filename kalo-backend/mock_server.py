"""
KALO Mock Backend API - For iOS Testing
Runs on http://localhost:8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import Optional, List
import uuid
from datetime import datetime

app = FastAPI(
    title="KALO API (Mock)",
    description="Mock backend for iOS testing",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== DATA MODELS =====
class AIChatRequest(BaseModel):
    message: str

class AIChatResponse(BaseModel):
    reply: str

class NutritionBarcodeRequest(BaseModel):
    barcode: str

class RecipeExtractionRequest(BaseModel):
    url: str

class RecipeExtractionResponse(BaseModel):
    id: str
    taskId: str
    status: str
    title: Optional[str] = None
    ingredients: Optional[List[dict]] = None
    steps: Optional[List[dict]] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

# ===== IN-MEMORY STORAGE =====
extraction_tasks = {}
SAMPLE_PRODUCTS = {
    "049000050127": {"productName": "Coca Cola", "calories": 140, "protein": 0, "carbs": 39, "fat": 0},
    "074182052436": {"productName": "Apple Juice", "calories": 110, "protein": 0, "carbs": 26, "fat": 0},
    "012000004155": {"productName": "Banana", "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
}

# ===== HEALTH CHECK =====
@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ===== AI CHAT =====
@app.post("/api/v1/ai/chat", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest):
    """
    Mock AI chat endpoint
    """
    message = request.message.lower()
    
    # Simple mock responses based on keywords
    responses = {
        "calorie": "The average daily calorie intake is 2000-2500 calories. Your specific needs depend on age, sex, activity level, and goals.",
        "protein": "Protein needs are typically 0.8-1g per kg of body weight. For athletes, it's 1.2-2g per kg.",
        "recipe": "Try our recipe extraction feature - paste a TikTok/Instagram/YouTube URL and get nutritional info automatically!",
        "workout": "Great question! Aim for 150 minutes of moderate cardio or 75 minutes of vigorous cardio per week.",
        "water": "Drink at least 8 glasses (64oz) of water daily, more if you exercise.",
        "hello": "Hi! I'm your Kalo nutrition assistant. Ask me about nutrition, recipes, workouts, or grocery planning.",
        "help": "I can help with: nutrition facts, calorie tracking, recipe extraction, workout tips, and meal planning.",
    }
    
    # Find best matching response
    reply = "That's a great question! I'd love to help, but for detailed nutrition info please consult with a nutritionist."
    for keyword, response in responses.items():
        if keyword in message:
            reply = response
            break
    
    return AIChatResponse(reply=reply)

# ===== BARCODE SCANNER =====
@app.post("/api/v1/nutrition/barcode")
async def scan_barcode(request: NutritionBarcodeRequest):
    """
    Mock barcode nutrition lookup
    """
    barcode = request.barcode.strip()
    
    # Check if product exists in mock data
    if barcode in SAMPLE_PRODUCTS:
        product = SAMPLE_PRODUCTS[barcode]
        return {
            "barcode": barcode,
            "productName": product["productName"],
            "calories": product["calories"],
            "protein": product["protein"],
            "carbs": product["carbs"],
            "fat": product["fat"],
            "servingSize": "per 100g",
            "source": "mock"
        }
    
    # Return mock data for any barcode
    return {
        "barcode": barcode,
        "productName": f"Product {barcode}",
        "calories": 100 + len(barcode) % 100,
        "protein": 2 + len(barcode) % 10,
        "carbs": 15 + len(barcode) % 20,
        "fat": 1 + len(barcode) % 5,
        "servingSize": "per 100g",
        "source": "mock"
    }

# ===== RECIPE EXTRACTION =====
@app.post("/api/v1/ai/extract-recipe", response_model=RecipeExtractionResponse)
async def extract_recipe(request: RecipeExtractionRequest):
    """
    Start recipe extraction task (returns immediately with task ID)
    """
    task_id = str(uuid.uuid4())[:8]
    
    # Store task
    extraction_tasks[task_id] = {
        "status": "processing",
        "url": request.url,
        "created_at": datetime.now().isoformat()
    }
    
    return RecipeExtractionResponse(
        id=task_id,
        taskId=task_id,
        status="processing",
        title=None
    )

@app.get("/api/v1/ai/extract-recipe/{task_id}/status", response_model=RecipeExtractionResponse)
async def get_extraction_status(task_id: str):
    """
    Get recipe extraction status
    """
    if task_id not in extraction_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = extraction_tasks[task_id]
    
    # Simulate completion after 2 checks
    if task.get("check_count", 0) >= 1:
        # Return completed recipe
        return RecipeExtractionResponse(
            id=task_id,
            taskId=task_id,
            status="completed",
            title="Delicious Pasta Primavera",
            ingredients=[
                {"name": "Pasta", "quantity": 400, "unit": "g"},
                {"name": "Olive Oil", "quantity": 2, "unit": "tbsp"},
                {"name": "Garlic", "quantity": 3, "unit": "cloves"},
                {"name": "Broccoli", "quantity": 1, "unit": "cup"},
                {"name": "Cherry Tomatoes", "quantity": 200, "unit": "g"},
            ],
            steps=[
                {"number": 1, "instruction": "Boil pasta until al dente"},
                {"number": 2, "instruction": "Heat olive oil and sauté garlic"},
                {"number": 3, "instruction": "Add vegetables and cook 5-7 minutes"},
                {"number": 4, "instruction": "Toss pasta with vegetables"},
                {"number": 5, "instruction": "Season and serve"},
            ],
            calories=450,
            protein=16,
            carbs=68,
            fat=12
        )
    else:
        # Still processing
        task["check_count"] = task.get("check_count", 0) + 1
        return RecipeExtractionResponse(
            id=task_id,
            taskId=task_id,
            status="processing",
            title=None
        )

# ===== ROOT =====
@app.get("/")
async def root():
    return {
        "service": "KALO Backend Mock API",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "ai_chat": "POST /api/v1/ai/chat",
            "barcode": "POST /api/v1/nutrition/barcode",
            "extract_recipe": "POST /api/v1/ai/extract-recipe",
            "recipe_status": "GET /api/v1/ai/extract-recipe/{task_id}/status"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
