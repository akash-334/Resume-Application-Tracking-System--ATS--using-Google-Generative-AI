import requests
import os

# Get API key from environment variable
llama_api_key = os.getenv("LLAMA_API_KEY")

# Ensure API key is set
if not llama_api_key:
    raise ValueError("LLAMA_API_KEY is missing. Set it as an environment variable.")

# Llama 3 API endpoint
url = "https://api.together.xyz/v1/chat/completions"

# Payload for the request
data = {
    "model": "meta-llama/llama-3-8b",
    "messages": [
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "How can I solve 8x + 7 = -23?"}
    ],
    "temperature": 0.7,
    "max_tokens": 500
}

# Headers for authentication
headers = {
    "Authorization": f"Bearer {llama_api_key}",
    "Content-Type": "application/json"
}

# Send request
response = requests.post(url, headers=headers, json=data)

# Print response
if response.status_code == 200:
    print(response.json()["choices"][0]["message"]["content"])
else:
    print(f"Error: {response.status_code}, {response.text}")
