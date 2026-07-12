
from xmlrpc import client

from groq import AsyncGroq
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()


api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

client = AsyncGroq(api_key=api_key)
async def ask(prompt):
        response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.7
        )
        return response.choices[0].message.content

async def main():
    client = AsyncGroq(api_key=api_key)
    prompts =["Tell me a joke","What is the capital of India?","2+2"]
    
    results = await asyncio.gather(*(ask(p) for p in prompts))
    for r in results:
        print(r)

asyncio.run(main())



