import openai
import os

# Set your OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

def support_chatbot(user_query):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=user_query,
        max_tokens=150
    )
    return response.choices[0].text.strip()
