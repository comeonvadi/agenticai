import getpass
import os
from dotenv import load_dotenv
load_dotenv()






try:
    baseten_api_key = os.getenv("BASETEN_API_KEY")
    os.environ["BASETEN_API_KEY"] = baseten_api_key
except Exception as e:
    #os.environ["BASETEN_API_KEY"] = getpass.getpass("Enter your Baseten API key: ")# Import API Keys
    print(f"Error loading environment variables: {e}")
    print("Please ensure you have a .env file with the correct BASETEN_API_KEY.")    
    exit(1)
print("BASETEN_API_KEY loaded successfully.")
#print(baseten_api_key)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V4.1-Flash",
    api_key=baseten_api_key,
    base_url="https://inference.baseten.co/v1",
)
response = llm.invoke("Hello, world!")
print(response.content)