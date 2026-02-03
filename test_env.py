import os
from dotenv import load_dotenv

load_dotenv()
print("Loaded Key:", os.getenv("OPENAI_API_KEY"))