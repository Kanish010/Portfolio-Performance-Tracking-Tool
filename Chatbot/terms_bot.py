import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model_id = os.getenv("MODEL_ID")

def clarify_financial_term(user_input):
    try:
        response = client.chat.completions.create(model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant knowledgeable in financial terms."},
            {"role": "user", "content": f"The user asked: '{user_input}'. Identify and correct any typos in the financial term or concept mentioned, or confirm if it's correct."}
        ],
        max_tokens=150)
        clarification = response.choices[0].message.content.strip()
        if "correct as is" in clarification.lower() or "i believe you meant" not in clarification.lower():
            return user_input  # Return original term if it's already correct or not found any typo
        return clarification.replace("I believe you meant '", "").replace("'.", "")
    except openai.OpenAIError as e:
        print(f"Error: {e}")
        return None

def get_financial_term_definition(term):
    try:
        response = client.chat.completions.create(model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant knowledgeable in financial terms."},
            {"role": "user", "content": f"Provide a detailed and comprehensive explanation of the following financial term: {term}"}
        ],
        max_tokens=300)
        definition = response.choices[0].message.content.strip()
        return definition
    except openai.OpenAIError as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't retrieve the definition for the term."

def handle_financial_terms():
    while True:
        user_input = input("Ask me about a financial term or concept (or 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            break
        clarified_term = clarify_financial_term(user_input)
        if clarified_term:
            definition = get_financial_term_definition(clarified_term)
            print(f"\nDefinition:\n{definition}\n")
        else:
            print("Sorry, I couldn't understand the term. Please try again.")

if __name__ == "__main__":
    handle_financial_terms()