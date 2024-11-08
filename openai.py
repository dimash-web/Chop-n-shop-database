import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_grocery_list(user_preferences):
    # Formulate the prompt based on user preferences
    prompt = f"""
    User budget: {user_preferences['Budget']}
    Dietary restrictions: {user_preferences['Dietary_restrictions']}
    Allergies: {user_preferences['Allergies']}
    Item preferences: {user_preferences['Food_request']}
    Preferred stores: {user_preferences['Preferred_stores']}
    
    Based on the available items in the database, create a shopping list within the user's budget.
    If items cannot fit the budget, provide alternative options. Include two lists if no store is preferred.
    """
    
    # Query OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5
    )

    return response.choices[0].text.strip()
