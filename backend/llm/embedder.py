_embeddings = None

def get_embeddings(text: str):
    global _embeddings
    if _embeddings is None:
        from huggingface_hub import InferenceClient
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        _embeddings = InferenceClient(
            provider="hf-inference",
            api_key=os.getenv("EMBEDDER_API_KEY"),
        )
    print(">>> Generating embeddings...", text[:30], "...")
    return _embeddings.feature_extraction(
            text=text,
            model="BAAI/bge-m3",
        ).tolist()