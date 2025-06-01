# Recipe Manager

A simple personal recipe organizer built with Flask and Streamlit. This is my project to learn web development basics.

## What it does

- Add, edit, and delete recipes
- Search recipes by name or ingredients  
- Mark recipes as favorites
- Add YouTube video links for cooking tutorials
- View basic recipe statistics
- Export all recipes to CSV file
- Simple web interface that's easy to use

## How to run it

1. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
2. **Start the backend server:**
   ```bash
   python app.py
3. **In a new terminal window, start the web interface:**
   ```bash
   streamlit run ui.py
4.Open your web browser and go to the URL that appears (usually http://localhost:8501)

Files in this project

app.py - The Flask backend that handles all the recipe data
ui.py - The Streamlit frontend that creates the web interface
requirements.txt - List of Python packages needed
recipes.json - Where all the recipe data gets saved (created automatically)

How it works
The Flask app creates a REST API that runs on port 5000. The Streamlit app creates a web interface on port 8501 and talks to the Flask API to get and save recipe data. All recipes are stored in a JSON file.
