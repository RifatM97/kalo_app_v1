#!/usr/bin/env python3
"""
KALO AI PIPELINE - COMPREHENSIVE TEST SCRIPT
Tests complete recipe extraction with real pipeline modules
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, '/Users/rifathossain/Desktop/kalo/kalo-backend')

async def test_pipeline():
    """Test the complete recipe extraction pipeline"""
    
    print(f"\n{'='*80}")
    print("KALO AI RECIPE EXTRACTION PIPELINE - COMPREHENSIVE TEST")
    print(f"{'='*80}\n")
    
    # Test video URL (YouTube)
    video_url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
    
    print(f"Testing with video: {video_url}\n")
    
    try:
        from app.ai.recipe_extractor import RecipeExtractionPipeline
        print("✓ Imported RecipeExtractionPipeline")
        
        # Run the pipeline
        print("\nStarting pipeline execution...")
        result = await RecipeExtractionPipeline.extract_recipe_from_video(video_url)
        
        # Print results
        print(f"\n{'='*80}")
        print("PIPELINE RESULTS")
        print(f"{'='*80}\n")
        
        print(f"Status: {result.get('status')}")
        print(f"Error: {result.get('error')}\n")
        
        if result.get('status') == 'success':
            print("Transcript:")
            transcript = result.get('transcript', '')[:200]
            print(f"  Length: {len(result.get('transcript', ''))} characters")
            print(f"  Sample: {transcript}...\n")
            
            print("OCR Text:")
            ocr = result.get('ocr_text', '')[:200]
            print(f"  Length: {len(result.get('ocr_text', ''))} characters")
            print(f"  Sample: {ocr}...\n")
            
            print("Detected Objects:")
            ingredients = result.get('detected_ingredients', [])
            print(f"  Count: {len(ingredients)}")
            print(f"  Objects: {ingredients}\n")
            
            print("Recipe:")
            recipe = result.get('recipe', {})
            print(json.dumps(recipe, indent=2))
            
            print(f"\n✓ PIPELINE SUCCESSFUL")
            return True
        else:
            print(f"✗ Pipeline failed: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_pipeline())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(1)
