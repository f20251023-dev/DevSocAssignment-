import os
import json
import asyncio
import aiohttp
import time



API_KEY = "" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"

INPUT_FILE = "text.txt"
OUTPUT_FILE = "llm_responses.json"
MAX_RETRIES = 5
INITIAL_BACKOFF = 1  

async def fetch_llm_response(session, prompt, retries=MAX_RETRIES, backoff=INITIAL_BACKOFF):
   
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    
    async with session.post(API_URL, json=payload, headers={'Content-Type': 'application/json'}) as response:
        if response.status == 200:
            result = await response.json()
            
            text = result['candidates'][0]['content']['parts'][0]['text']
            return {"prompt": prompt, "response": text.strip()}
            
            
        elif response.status in (429, 500, 503): 
            if retries > 0:
                await asyncio.sleep(backoff)
                return await fetch_llm_response(session, prompt, retries - 1, backoff * 2)
                
            


def read_prompts_from_file(filename):
   
    
    with open(filename, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    return prompts
    

def save_responses_to_json(filename, results):
    

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\nsaved {len(results)} responses to '{filename}'")
    
async def main():
    
    start_time = time.time()
    
    
    
    prompts = read_prompts_from_file(INPUT_FILE)
    
    if not prompts:
        print("No prompts to process.")
        return

    print(f"Found {len(prompts)} prompts.")

    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_llm_response(session, prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)

    
    save_responses_to_json(OUTPUT_FILE, results)
    
    end_time = time.time()

if __name__ == "__main__":
 
    if API_KEY == "":
        env_key = os.environ.get("YOUR_API_KEY")
        if env_key:
            API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={env_key}"

            
    asyncio.run(main())
