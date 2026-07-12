import json
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from groq import Groq
from httpx import stream
from httpx import stream
from pydantic import BaseModel

load_dotenv()

app = FastAPI()


class PromptRequest(BaseModel):
    message: str


class PromptResponse(BaseModel):
    message: str
    model: str
    status: str


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.get("/")
def show():
    return {"message": "Hello World!"}

def stream_response(message: str):
    stream = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[{"role": "user", "content": message}],
        stream=True)
    
    for chunk in stream:
        content = chunk.choices[0].delta.content
        #print(f"Streaming content: {content}")
        if content:
            yield content


@app.post("/generate")
def generate(request: PromptRequest):
    return StreamingResponse(stream_response(request.message),
                                 media_type="text/event-stream")
   



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("streaming:app", host="localhost", port=8000, reload=True)

