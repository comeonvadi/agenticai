
#main.py will not be used (only app.py will be used),
#  when we deploy the app in hugging space spaces
#uv pakage manager will not be used. hence *.toml file will not be used
#need to use requirements.txt
#add .env as secrets in hugging space spaces
#after spaces created in hugging space portal
#you have to download the git clone using commandcommand prompt execution
#  : example: git clone https://huggingspace.co/spaces/comeonvadi/mychatassistant
#You will have read me file and .gitattribut file. not to make any changes in the file
#place the app.py and requirements.txt alone in the folder
# only 4 files needed from this project to be pushed to hugging face to run the app in hugging face
#1 .gitattributes the file downloaded from the abpve git clone command
#2 app.py
#3. requirements.txt
#4 Readme.md (Optional) -> what u downloaded from git clone above
# in command prompt
# git add .
# git commit -m "inital commit"
#git push
#it may ask access token of hugging face. you can use the same
#In spaces, the code is getting build 
# will use docket to deploy and application will startup


import os
import gradio as gr
from dotenv import load_dotenv
from groq import Groq
import spaces 

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") 
#Keys and model name should be stored in secrets inside 
# the spaces in huggingspace repository settings Variables/Secrets section
if not api_key:
    raise RuntimeError("Set the GROQ_API_KEY environment variable before starting the app.")

client = Groq(api_key=api_key)

@spaces.GPU #the code will be used in Free GPU Space
def chatsrepoponse(message, history):
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[{"role": "user", "content": message}],
        temperature=0.8,
    )
    content = response.choices[0].message.content
    return content or ""


with gr.Blocks(theme="soft") as demo:
    gr.ChatInterface(
        title="Simple Chat Assistant",
        description="A simple chat interface that sends messages to a local server and displays the responses.",
        examples=["Tell me a joke.", "Give me a motivational quote.", "How are you?"],
        fn=chatsrepoponse,
    )


if __name__ == "__main__":
    demo.launch(share=True)
    
                     