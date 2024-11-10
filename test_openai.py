from openai_service import generate_grocery_list

# Define user preferences for the test
user_preferences = {
    "Budget": 50,  # User's budget for the grocery list
    "Dietary_restrictions": ["gluten-free", "dairy-free"],
    "Allergies": ["peanuts", "shellfish"],  # List of allergies
    "Food_request": ["pasta", "arabiatta"],  # Specific food requests
    "Preferred_stores": ["Trader Joe's"]  # Preferred stores
}

# Call the function to generate the grocery list
grocery_list = generate_grocery_list(user_preferences)

# Print the generated grocery list
print(grocery_list)
