# Our Chop N' Shop Grocery database

This is a simple command-line set-up of a database of grocery store prices and recipe-based ingredient suggestions. It allows users to obtain shopping lists based on the recipes they want to cook, their allergies and dietary restrictions, grocery store preferences and burget in a MongoDB database.

## Prerequisites
Python 3.11 or higher
MongoDB Atlas account (or a local MongoDB installation if you'd like)
pip (Python package manager)

## Schema

## Why We Chose MongoDB Over SQL

We selected MongoDB for the Chop N' Shop application database for these reasons:

1. Ease of Use: MongoDB’s flexible query language and support for various data types simplify data retrieval and manipulation. This helps streamline our development process, allowing us to focus on core features like generating recipe-based shopping lists, accommodating dietary restrictions, and managing grocery store preferences.

3. Learning Opportunity: While our team has experience with SQL, we saw this as a chance to expand our skills by learning MongoDB. We’re confident that this shift will not slow down feature implementation, but rather give us the opportunity to explore new capabilities that MongoDB offers.
  
5. Schema Flexibility: MongoDB’s document-based structure allows us to handle dynamic and varying data formats naturally. This is particularly useful for storing data such as user preferences, grocery store details, recipe ingredients, and allergen information, all of which can vary greatly in structure.
 
7. Performance: MongoDB is well-suited to handle the large volumes of data our application will generate, such as managing multiple users, recipes, and store inventories, with high read and write operations. This ensures fast performance compared to traditional SQL databases.

9. Cloud Integration: By leveraging MongoDB Atlas, a cloud-based solution, we ensure our database is secure, scalable, and accessible. This allows us to focus on building and improving the application’s functionality without the overhead of database maintenance.

## Setup
1. Clone this repository or download the source code.
   
3. Navigate to the project directory:
   `cd path/to/Chopnshop-database`
   
5. Create a virtual environemnt if you'd like:
   `python -m venv .venv`

   On Windows:
  ` .venv\Scripts\activate`

   On macOS and Linux:
  ` source .venv/bin/activate`

6. Install the required packages:
   `pip install -r requirements.txt`

7. Create a .env file in the project root directory with your MongoDB connection string:
   MONGODB_URI='your_mongodb_connection_string_here'
   Replace your_mongodb_connection_string_here with your actual MongoDB connection string from Atlas.

## Usage
To run the application:

`python main.py`

Add users, items, stores, and recipes.
