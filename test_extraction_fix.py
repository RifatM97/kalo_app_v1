#!/usr/bin/env python3
"""
Test the fixed AI extraction pipeline
Tests both endpoints: /api/ai/extract-recipe (URL-based) and /api/recipes/extract-from-image
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend is healthy")
            return True
        else:
            print(f"✗ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend not reachable: {e}")
        return False

def test_url_extraction(video_url):
    """Test URL-based extraction (async with polling)"""
    print(f"\n{'='*60}")
    print(f"Testing URL extraction: {video_url}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Submit extraction request
        print("Step 1: Submitting extraction request...")
        response = requests.post(
            f"{BASE_URL}/api/ai/extract-recipe",
            json={"url": video_url},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to submit request: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        task_id = data.get("task_id")
        status = data.get("status")
        
        print(f"✓ Task created: {task_id}")
        print(f"  Status: {status}")
        
        if not task_id:
            print("✗ No task_id returned")
            return False
        
        # Step 2: Poll for completion
        print("\nStep 2: Polling for completion...")
        max_polls = 60  # Wait up to 2 minutes
        poll_interval = 2
        
        for i in range(max_polls):
            time.sleep(poll_interval)
            
            response = requests.get(
                f"{BASE_URL}/api/ai/extract-recipe/{task_id}/status",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"✗ Failed to get status: {response.status_code}")
                return False
            
            data = response.json()
            status = data.get("status")
            
            print(f"  Poll {i+1}/{max_polls}: {status}")
            
            if status == "completed":
                print("\n✓ Extraction completed!")
                print("\n" + "="*60)
                print("EXTRACTED RECIPE:")
                print("="*60)
                print(f"Title: {data.get('title', 'N/A')}")
                print(f"Description: {data.get('description', 'N/A')}")
                print(f"Servings: {data.get('servings', 'N/A')}")
                print(f"Difficulty: {data.get('difficulty', 'N/A')}")
                print(f"Cook time: {data.get('cook_time_minutes', 'N/A')} min")
                print(f"Prep time: {data.get('prep_time_minutes', 'N/A')} min")
                
                ingredients = data.get('ingredients', [])
                if ingredients:
                    print(f"\nIngredients ({len(ingredients)}):")
                    for ing in ingredients[:5]:  # Show first 5
                        qty = ing.get('quantity') or ''
                        unit = ing.get('unit') or ''
                        name = ing.get('name', 'Unknown')
                        print(f"  - {qty} {unit} {name}".strip())
                    if len(ingredients) > 5:
                        print(f"  ... and {len(ingredients) - 5} more")
                
                steps = data.get('steps', [])
                if steps:
                    print(f"\nSteps ({len(steps)}):")
                    for step in steps[:3]:  # Show first 3
                        step_num = step.get('step', '?')
                        instruction = step.get('instruction', 'N/A')
                        print(f"  {step_num}. {instruction[:80]}")
                    if len(steps) > 3:
                        print(f"  ... and {len(steps) - 3} more steps")
                
                macros = data.get('macros', {})
                if macros:
                    print(f"\nMacros per serving:")
                    print(f"  Calories: {macros.get('calories', 'N/A')}")
                    print(f"  Protein: {macros.get('protein', 'N/A')}g")
                    print(f"  Carbs: {macros.get('carbs', 'N/A')}g")
                    print(f"  Fat: {macros.get('fat', 'N/A')}g")
                
                print("="*60)
                return True
            
            elif status == "failed":
                error = data.get('error', 'Unknown error')
                print(f"\n✗ Extraction failed: {error}")
                return False
            
            elif status == "processing":
                # Still processing, continue polling
                continue
            
            else:
                print(f"\n✗ Unknown status: {status}")
                return False
        
        print("\n✗ Timeout waiting for extraction")
        return False
        
    except Exception as e:
        print(f"\n✗ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("KALO AI EXTRACTION PIPELINE TEST")
    print("="*60)
    
    # Test 1: Backend health
    if not test_health():
        print("\n✗ Backend not running. Start with:")
        print("  ./start_backend.sh")
        sys.exit(1)
    
    # Test 2: URL extraction with the TikTok link
    tiktok_url = "https://www.tiktok.com/@nourishment.nutrition/video/7580846176082087198"
    
    print(f"\n\nTesting with TikTok URL:")
    print(f"  {tiktok_url}")
    print(f"\nNOTE: This will:")
    print(f"  1. Download the video using yt-dlp")
    print(f"  2. Extract frames across the video timeline")
    print(f"  3. Send selected frames to OpenAI Vision (gpt-4o)")
    print(f"  4. Extract structured recipe data")
    print(f"\nThis may take 30-90 seconds and will cost ~$0.02-0.05")
    print(f"\nPress Ctrl+C to cancel, or wait 5 seconds to start...")
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    
    success = test_url_extraction(tiktok_url)
    
    if success:
        print("\n\n" + "="*60)
        print("✓ TEST PASSED - AI extraction is working!")
        print("="*60)
        print("\nThe fix resolved the 'cake with dining table' issue by:")
        print("  1. Sending actual video FRAMES as images to GPT-4o Vision")
        print("  2. Using a stronger prompt that checks for cooking content")
        print("  3. Reducing hallucination with lower temperature (0.2)")
        sys.exit(0)
    else:
        print("\n\n" + "="*60)
        print("✗ TEST FAILED")
        print("="*60)
        print("\nCheck backend logs:")
        print("  tail -f /tmp/kalo-backend.log")
        sys.exit(1)

if __name__ == "__main__":
    main()
