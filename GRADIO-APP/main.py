

import gradio as gr
import groq as Groq
import os
from dotenv import load_dotenv
import requests

load_dotenv()
client =Groq(api_key=os.getenv("GROQ_API_KEY"))

def chatsrepoponse(message,history):
    try:
        result = requests.post("http://localhost:8000/generate", 
                               json={"message": message})
        result.raise_for_status()
        return result.json().get("message", "No 'response' received.")
    except requests.exceptions.RequestException as e:
        return f"Error Connecting Server: {e}"


with gr.Blocks(theme="soft") as demo:
    gr.ChatInterface(title="Simple Chat Assistant",
                     description="A simple chat interface that sends messages to a local server and displays the responses.",
                     examples=["Tell me a joke.", "Give me a motivational quote.", "How are you?"],
                     fn=chatsrepoponse)

if __name__ == "__main__":
    demo.launch(share=True)
    
                     