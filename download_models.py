from transformers import AutoModel, AutoTokenizer, AutoProcessor
from sentence_transformers import SentenceTransformer
import os

def download_models():
    # Create model cache directory
    os.makedirs("model_cache", exist_ok=True)
    
    print("Downloading Sentence Transformer model...")
    SentenceTransformer('all-MiniLM-L6-v2')
    
    print("\nDownloading OPT-350M model...")
    AutoModel.from_pretrained('facebook/opt-350m')
    AutoTokenizer.from_pretrained('facebook/opt-350m')
    
    print("\nDownloading Wav2Vec2 model...")
    AutoModel.from_pretrained('facebook/wav2vec2-base-960h')
    AutoProcessor.from_pretrained('facebook/wav2vec2-base-960h')
    
    print("\nDownloading VITS model...")
    AutoModel.from_pretrained('facebook/mms-tts-eng')
    AutoTokenizer.from_pretrained('facebook/mms-tts-eng')
    
    print("\nAll models downloaded successfully!")

if __name__ == "__main__":
    download_models() 