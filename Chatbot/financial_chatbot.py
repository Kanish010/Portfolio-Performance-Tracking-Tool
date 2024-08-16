import os
import uuid
from openai import OpenAI
from dotenv import load_dotenv
from chat_history import save_message, load_history

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat_with_gpt(message_history):
    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=message_history)
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    message_history = load_history(session_id)
    
    if not message_history:
        message_history = [{"role": "system", "content": "You are a financial assistant specializing in financial terms, market data, and portfolio management. Provide clear, accurate, and concise financial information."}]
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break
        
        message_history.append({"role": "user", "content": user_input})
        response = chat_with_gpt(message_history)
        message_history.append({"role": "assistant", "content": response})
        
        save_message(session_id, "user", user_input)
        save_message(session_id, "assistant", response)
        
        print("Chatbot: ", response)