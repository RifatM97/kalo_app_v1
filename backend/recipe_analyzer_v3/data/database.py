"""Mock database for user profile information"""

# Mock user profile dictionary
user_profile = {
    "user_id": "user_001",
    "name": "John Doe",
    "age": 30,
    "weight_kg": 75.5,
    "height_cm": 175,
    "daily_calorie_intake": 2000,
    "diet_goal": "maintain weight",  # Options: "lose weight", "gain weight", "maintain weight"
    "dietary_restrictions": ["vegetarian"],
    "activity_level": "moderate"  # Options: "sedentary", "light", "moderate", "active", "very active"
}

# Multiple user profiles example
users_db = {
    "user_001": {
        "name": "John Doe",
        "age": 30,
        "weight_kg": 75.5,
        "height_cm": 175,
        "daily_calorie_intake": 2000,
        "diet_goal": "maintain weight",
        "dietary_restrictions": ["vegetarian"],
        "activity_level": "moderate"
    },
    "user_002": {
        "name": "Jane Smith",
        "age": 28,
        "weight_kg": 65.0,
        "height_cm": 165,
        "daily_calorie_intake": 1800,
        "diet_goal": "lose weight",
        "dietary_restrictions": [],
        "activity_level": "light"
    },
    "user_003": {
        "name": "Mike Johnson",
        "age": 35,
        "weight_kg": 85.0,
        "height_cm": 180,
        "daily_calorie_intake": 2500,
        "diet_goal": "gain weight",
        "dietary_restrictions": ["gluten-free"],
        "activity_level": "active"
    }
}
