"""
Configuration settings for AMARDS (DeepSeek version)
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   # ✅ change this
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # OpenRouter + DeepSeek model
    MODEL_NAME = "deepseek/deepseek-chat"   # ✅ VERY IMPORTANT
    BASE_URL = "https://openrouter.ai/api/v1"
    
    TEMPERATURE = 0.7
    MAX_TOKENS = 4000
    
    # Agent settings
    MAX_ITERATIONS = 10
    CRITIC_THRESHOLD = 0.7
    
    # Memory settings
    MAX_MEMORY_ITEMS = 50
    
@classmethod
def validate(cls):
    if not cls.OPENAI_API_KEY:   # ✅ change here
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    if not cls.TAVILY_API_KEY:
        print("Warning: TAVILY_API_KEY not set. Web search limited.")
    
    return True