# Our Chop N' Shop Grocery database

This is a simple command-line set-up of a database of grocery store prices and recipe-based ingredient suggestions. It allows users to obtain shopping lists based on the recipes they want to cook, their allergies and dietary restrictions, grocery store preferences and burget in a MongoDB database.

## Prerequisites
Python 3.11 or higher
MongoDB Atlas account (or a local MongoDB installation if you'd like)
pip (Python package manager)

## Setup
1. Clone this repository or download the source code.
   
3. Navigate to the project directory:
   cd path/to/Chopnshop-database
   
5. Create a virtual environemnt if you'd like:
   python -m venv .venv

   On Windows:
   .venv\Scripts\activate

   On macOS and Linux:
   source .venv/bin/activate

6. Install the required packages:
   pip install -r requirements.txt

7. Create a .env file in the project root directory with your MongoDB connection string:
   MONGODB_URI='your_mongodb_connection_string_here'
   Replace your_mongodb_connection_string_here with your actual MongoDB connection string from Atlas.

## Usage
To run the application:

python main.py
