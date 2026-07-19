import random
import hashlib
import requests
from typing import List

def get_mock_embedding(text: str, dimensions: int = 768) -> List[float]:
    """
    Generates a deterministic mock embedding vector of unit length
    based on the SHA-256 hash of the input text.
    """
    # Seed random generator with the hash of the text
    hasher = hashlib.sha256(text.encode('utf-8'))
    seed = int(hasher.hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    
    # Generate random Gaussian vector
    vec = [rng.gauss(0, 1) for _ in range(dimensions)]
    
    # Normalize to unit length (L2 norm)
    norm = sum(x*x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

def get_embedding(text: str, api_key: str = None) -> List[float]:
    """
    Calls the Gemini API to retrieve embeddings for the input text using text-embedding-004.
    Falls back to deterministic mock embeddings if no API key is set or if the API call fails.
    """
    if not api_key:
        return get_mock_embedding(text)
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [
                {
                    "text": text
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            return res_json["embedding"]["values"]
        else:
            print(f"[Embeddings API] Status {response.status_code}: {response.text}. Falling back to mock.")
            return get_mock_embedding(text)
    except Exception as e:
        print(f"[Embeddings API] Request error: {e}. Falling back to mock.")
        return get_mock_embedding(text)

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Computes the cosine similarity between two float vectors.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)
