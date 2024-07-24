import openai

# Set your OpenAI API key
openai.api_key = 'sk-proj-q9sIpSKeTJUMQnfVBqi7T3BlbkFJ8nBzYMT1gBH92AEZah72'

def support_chatbot(user_query):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=user_query,
        max_tokens=150
    )
    return response.choices[0].text.strip()
