from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()
def main():
    print(os.getenv("GROQ_API_KEY"))
    print(os.getenv("MODEL"))

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    while True:
        user_input = input("You: ") 
        if user_input.lower() == "exit":
            break
        response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
                    {"role": "user", "content": user_input}
        ],
        temperature=0.3,
        max_tokens=30
    )
        print(f"AI: {response.choices[0].message.content}")

    print(response)


if __name__ == "__main__":
    main()
