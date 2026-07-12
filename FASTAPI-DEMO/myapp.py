import json
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from groq import Groq
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


@app.post("/generate")
def generate(request: PromptRequest):
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[{"role": "user", "content": request.message}],
    )
    return PromptResponse(
        message=response.choices[0].message.content,
        model=os.getenv("MODEL"),
        status="Success"
        )




if __name__ == "__main__":
    import uvicorn

    uvicorn.run("myapp:app", host="localhost", port=8000, reload=True)

