import openai

# Set your OpenAI API key
openai.api_key = 'your api'

def support_chatbot(user_query):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=user_query,
        max_tokens=150
    )
    return response.choices[0].text.strip()
