from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow requests from Streamlit

# File to store recipes
DATA_FILE = 'recipes.json'

def load_recipes():
    """Load recipes from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_recipes(recipes):
    """Save recipes to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(recipes, f, indent=2)

# Initialize with some sample data
if not os.path.exists(DATA_FILE):
    sample_recipes = [
        {
            "id": 1,
            "name": "Pasta Carbonara",
            "ingredients": ["pasta", "eggs", "bacon", "cheese", "pepper"],
            "instructions": "Cook pasta. Mix eggs and cheese. Combine with hot pasta and bacon.",
            "prep_time": 20,
            "difficulty": "Easy",
            "category": "Main Course",
            "youtube_url": "",
            "is_favorite": True,
            "created_at": "2025-01-01"
        },
        {
            "id": 2,
            "name": "Chocolate Cookies",
            "ingredients": ["flour", "butter", "sugar", "chocolate chips", "eggs"],
            "instructions": "Mix ingredients. Bake at 350F for 12 minutes.",
            "prep_time": 30,
            "difficulty": "Easy",
            "category": "Dessert",
            "youtube_url": "https://www.youtube.com/watch?v=example",
            "is_favorite": False,
            "created_at": "2025-01-02"
        }
    ]
    save_recipes(sample_recipes)

#home page
@app.route('/')
def home():
    return jsonify({"message": "Recipe Manager API is running!"})

#get all recipes
@app.route('/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes"""
    recipes = load_recipes()
    return jsonify(recipes)

# get single recipe by ID
@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a single recipe by ID"""
    try:
        recipes = load_recipes()
        
        # Find the recipe
        for recipe in recipes:
            if recipe['id'] == recipe_id:
                return jsonify(recipe)
        
        return jsonify({"error": "Recipe not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#recipes addition
@app.route('/recipes', methods=['POST'])
def add_recipe():
    """Add a new recipe"""
    try:
        data = request.get_json()
        
        # Basic validation
        if not data.get('name'):
            return jsonify({"error": "Recipe name is required"}), 400
        
        if not data.get('ingredients'):
            return jsonify({"error": "Ingredients are required"}), 400
        
        # Load existing recipes
        recipes = load_recipes()
        
        # generate new ID
        new_id = max([r['id'] for r in recipes], default=0) + 1
        
        # create new recipe
        new_recipe = {
            "id": new_id,
            "name": data['name'],
            "ingredients": data['ingredients'],
            "instructions": data.get('instructions', ''),
            "prep_time": data.get('prep_time', 0),
            "difficulty": data.get('difficulty', 'Easy'),
            "category": data.get('category', 'Main Course'),
            "youtube_url": data.get('youtube_url', ''),
            "is_favorite": data.get('is_favorite', False),
            "created_at": datetime.now().strftime('%Y-%m-%d')
        }
        
        recipes.append(new_recipe)
        save_recipes(recipes)
        
        return jsonify(new_recipe), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# edit recipe endpoint
@app.route('/recipes/<int:recipe_id>', methods=['PUT'])
def edit_recipe(recipe_id):
    """Edit an existing recipe"""
    try:
        data = request.get_json()
        
        # basic validation
        if not data.get('name'):
            return jsonify({"error": "Recipe name is required"}), 400
        
        if not data.get('ingredients'):
            return jsonify({"error": "Ingredients are required"}), 400
        
        # load existing recipes
        recipes = load_recipes()
        
        # find and update the recipe
        recipe_found = False
        for i, recipe in enumerate(recipes):
            if recipe['id'] == recipe_id:
                # update the recipe while keeping original ID and created_at
                recipes[i] = {
                    "id": recipe_id,
                    "name": data['name'],
                    "ingredients": data['ingredients'],
                    "instructions": data.get('instructions', ''),
                    "prep_time": data.get('prep_time', 0),
                    "difficulty": data.get('difficulty', 'Easy'),
                    "category": data.get('category', 'Main Course'),
                    "youtube_url": data.get('youtube_url', ''),
                    "is_favorite": data.get('is_favorite', False),
                    "created_at": recipe.get('created_at', datetime.now().strftime('%Y-%m-%d'))  # Keep original date
                }
                recipe_found = True
                break
        
        if not recipe_found:
            return jsonify({"error": "Recipe not found"}), 404
        
        save_recipes(recipes)
        return jsonify(recipes[i])  # Return updated recipe
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#delete recipes
@app.route('/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    """Delete a recipe"""
    try:
        recipes = load_recipes()
        
        # find recipe to delete
        recipe_to_delete = None
        for i, recipe in enumerate(recipes):
            if recipe['id'] == recipe_id:
                recipe_to_delete = recipes.pop(i)
                break
        
        if not recipe_to_delete:
            return jsonify({"error": "Recipe not found"}), 404
        
        save_recipes(recipes)
        return jsonify({"message": "Recipe deleted successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#search recipe
@app.route('/recipes/search', methods=['GET'])
def search_recipes():
    """Search recipes by name or ingredient"""
    try:
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify([])
        
        recipes = load_recipes()
        filtered_recipes = []
        
        for recipe in recipes:
            # search in name
            if query in recipe['name'].lower():
                filtered_recipes.append(recipe)
                continue
            
            # search in ingredients
            for ingredient in recipe['ingredients']:
                if query in ingredient.lower():
                    filtered_recipes.append(recipe)
                    break
        
        return jsonify(filtered_recipes)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#favourite toggle
@app.route('/recipes/<int:recipe_id>/favorite', methods=['PUT'])
def toggle_favorite(recipe_id):
    """Toggle favorite status of a recipe"""
    try:
        recipes = load_recipes()
        
        # find recipe to update
        recipe_found = False
        for recipe in recipes:
            if recipe['id'] == recipe_id:
                recipe['is_favorite'] = not recipe.get('is_favorite', False)
                recipe_found = True
                break
        
        if not recipe_found:
            return jsonify({"error": "Recipe not found"}), 404
        
        save_recipes(recipes)
        return jsonify({"message": "Favorite status updated"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#server setup
if __name__ == '__main__':
    print("Starting Recipe Manager API...")
    print("Visit: http://localhost:5000")
    app.run(debug=True, port=5000)
