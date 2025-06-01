import streamlit as st
import requests
import pandas as pd
import json
import re

# API base URL
API_URL = "http://localhost:5000"

st.set_page_config(
    page_title="Recipe Manager",
    page_icon="🍳",
    layout="wide"
)

def extract_youtube_id(url):
    """Extract YouTube video ID from URL"""
    if not url:
        return None
    
    # handle different yt formats
    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtu\.be/([^?]+)',
        r'youtube\.com/embed/([^?]+)',
        r'youtube\.com/v/([^?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def embed_youtube_video(youtube_url, width=560, height=315):
    """Create YouTube embed HTML"""
    video_id = extract_youtube_id(youtube_url)
    if not video_id:
        return None
    
    embed_html = f"""
    <div style="display: flex; justify-content: center; margin: 10px 0;">
        <iframe 
            width="{width}" 
            height="{height}" 
            src="https://www.youtube.com/embed/{video_id}" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
        </iframe>
    </div>
    """
    return embed_html

def get_all_recipes():
    """Fetch all recipes from API"""
    try:
        response = requests.get(f"{API_URL}/recipes")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        st.error("Could not connect to API. Make sure Flask app is running!")
        return []

def get_recipe(recipe_id):
    """Fetch single recipe from API"""
    try:
        response = requests.get(f"{API_URL}/recipes/{recipe_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def add_recipe(recipe_data):
    """Add new recipe via API"""
    try:
        response = requests.post(f"{API_URL}/recipes", json=recipe_data)
        return response.status_code == 201
    except:
        return False

def edit_recipe(recipe_id, recipe_data):
    """Edit existing recipe via API"""
    try:
        response = requests.put(f"{API_URL}/recipes/{recipe_id}", json=recipe_data)
        return response.status_code == 200
    except:
        return False

def delete_recipe(recipe_id):
    """Delete recipe via API"""
    try:
        response = requests.delete(f"{API_URL}/recipes/{recipe_id}")
        return response.status_code == 200
    except:
        return False

def search_recipes(query):
    """Search recipes via API"""
    try:
        response = requests.get(f"{API_URL}/recipes/search", params={"q": query})
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def toggle_favorite(recipe_id):
    """Toggle favorite status via API"""
    try:
        response = requests.put(f"{API_URL}/recipes/{recipe_id}/favorite")
        return response.status_code == 200
    except:
        return False

def show_recipe_form(recipe=None, form_key="add"):
    """Show recipe form for adding or editing"""
    form_title = "✏️ Edit Recipe" if recipe else "➕ Add New Recipe"
    button_text = "Update Recipe" if recipe else "Add Recipe"
    
    st.header(form_title)
    
    with st.form(f"{form_key}_recipe_form"):
        name = st.text_input("Recipe Name*", value=recipe['name'] if recipe else "")
        
        # ingredients input
        ingredients_text = st.text_area(
            "Ingredients (one per line)*",
            value='\n'.join(recipe['ingredients']) if recipe else "",
            placeholder="pasta\neggs\nbacon\ncheese"
        )
        
        instructions = st.text_area("Instructions", value=recipe.get('instructions', '') if recipe else "")
        
        col1, col2 = st.columns(2)
        with col1:
            prep_time = st.number_input("Prep Time (min)", min_value=0, value=recipe.get('prep_time', 30) if recipe else 30)
        with col2:
            difficulty_options = ["Easy", "Medium", "Hard"]
            current_difficulty = recipe.get('difficulty', 'Easy') if recipe else 'Easy'
            difficulty_index = difficulty_options.index(current_difficulty) if current_difficulty in difficulty_options else 0
            difficulty = st.selectbox("Difficulty", difficulty_options, index=difficulty_index)
        
        category_options = ["Main Course", "Dessert", "Appetizer", "Breakfast", "Snack", "Beverage"]
        current_category = recipe.get('category', 'Main Course') if recipe else 'Main Course'
        category_index = category_options.index(current_category) if current_category in category_options else 0
        category = st.selectbox("Category", category_options, index=category_index)
        
        youtube_url = st.text_input("YouTube URL (optional)", 
                                  value=recipe.get('youtube_url', '') if recipe else "",
                                  placeholder="https://www.youtube.com/watch?v=...")
        
        # yt video preview
        if youtube_url:
            video_id = extract_youtube_id(youtube_url)
            if video_id:
                st.success("✅ Valid YouTube URL detected!")
                #thumbnail preview
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                st.image(thumbnail_url, width=200, caption="Video Preview")
            else:
                st.warning("⚠️ Invalid YouTube URL format")
        
        is_favorite = st.checkbox("⭐ Mark as Favorite", value=recipe.get('is_favorite', False) if recipe else False)
        
        submitted = st.form_submit_button(button_text)
        
        if submitted:
            if name and ingredients_text:
                ingredients = [ing.strip() for ing in ingredients_text.split('\n') if ing.strip()]
                
                recipe_data = {
                    "name": name,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "prep_time": prep_time,
                    "difficulty": difficulty,
                    "category": category,
                    "youtube_url": youtube_url,
                    "is_favorite": is_favorite
                }
                
                if recipe:  # editing existing recipe
                    if edit_recipe(recipe['id'], recipe_data):
                        st.success("Recipe updated successfully!")
                        return True  
                    else:
                        st.error("Failed to update recipe!")
                else:  # adding new recipe
                    if add_recipe(recipe_data):
                        st.success("Recipe added successfully!")
                        return True  
                    else:
                        st.error("Failed to add recipe!")
            else:
                st.error("Please fill in required fields!")
        
        return False  

# initialize session state for edit mode
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edit_recipe_id' not in st.session_state:
    st.session_state.edit_recipe_id = None

# Main app
st.title("🍳 Personal Recipe Manager")
st.markdown("*Organize your favorite recipes!*")

# sidebar for adding/editing recipes
with st.sidebar:
    if st.session_state.edit_mode:
        # get recipe data for editing
        recipe_to_edit = get_recipe(st.session_state.edit_recipe_id)
        if recipe_to_edit:
            success = show_recipe_form(recipe_to_edit, "edit")
            if success:
                st.session_state.edit_mode = False
                st.session_state.edit_recipe_id = None
                st.rerun()
        else:
            st.error("Recipe not found!")
            st.session_state.edit_mode = False
            st.session_state.edit_recipe_id = None
        
        # cancel edit button
        if st.button("❌ Cancel Edit"):
            st.session_state.edit_mode = False
            st.session_state.edit_recipe_id = None
            st.rerun()
    else:
        # Regular add recipe form
        success = show_recipe_form()
        if success:
            st.rerun()

# Main content area
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("🔍 Search")
    search_query = st.text_input("Search recipes...", placeholder="pasta, chicken, etc.")

# get recipes
if search_query:
    recipes = search_recipes(search_query)
    st.subheader(f"Search Results for '{search_query}'")
else:
    recipes = get_all_recipes()
    st.subheader("All Recipes")

if not recipes:
    if search_query:
        st.info("No recipes found matching your search.")
    else:
        st.info("No recipes yet. Add your first recipe using the sidebar!")
else:
    # show recipes
    for recipe in recipes:
        fav_icon = "⭐" if recipe.get('is_favorite', False) else "☆"
        recipe_title = f"{fav_icon} {recipe['name']} ({recipe['difficulty']}) - {recipe['prep_time']} min - {recipe.get('category', 'Main Course')}"
        
        with st.expander(recipe_title):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write("**Ingredients:**")
                for ingredient in recipe['ingredients']:
                    st.write(f"• {ingredient}")
                
                if recipe['instructions']:
                    st.write("**Instructions:**")
                    st.write(recipe['instructions'])
                
                # yt video
                if recipe.get('youtube_url'):
                    st.write("**Video Tutorial:**")
                    
                    # viewing options
                    tab1, tab2 = st.tabs(["🎥 Watch Video", "🔗 Open in YouTube"])
                    
                    with tab1:
                        #video player
                        embed_html = embed_youtube_video(recipe['youtube_url'], width=500, height=280)
                        if embed_html:
                            st.components.v1.html(embed_html, height=300)
                        else:
                            st.error("Invalid YouTube URL format")
                    
                    with tab2:
                        st.write(f"[🎥 Open in YouTube]({recipe['youtube_url']})")
                        #thumbnail
                        video_id = extract_youtube_id(recipe['youtube_url'])
                        if video_id:
                            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                            st.image(thumbnail_url, width=300)
                
                st.write(f"**Created:** {recipe['created_at']}")
            
            with col2:
                # edit
                if st.button(f"✏️ Edit", key=f"edit_{recipe['id']}"):
                    st.session_state.edit_mode = True
                    st.session_state.edit_recipe_id = recipe['id']
                    st.rerun()
                
                #favourite
                fav_text = "💔 Unfavorite" if recipe.get('is_favorite', False) else "❤️ Favorite"
                if st.button(fav_text, key=f"fav_{recipe['id']}"):
                    if toggle_favorite(recipe['id']):
                        st.success("Updated!")
                        st.rerun()
                    else:
                        st.error("Failed to update!")
                
                if st.button(f"🗑️ Delete", key=f"delete_{recipe['id']}"):
                    if delete_recipe(recipe['id']):
                        st.success("Recipe deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete recipe!")

#stats
if recipes:
    st.subheader("📊 Recipe Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Recipes", len(recipes))
    
    with col2:
        avg_prep = sum(r['prep_time'] for r in recipes) / len(recipes)
        st.metric("Avg Prep Time", f"{avg_prep:.0f} min")
    
    with col3:
        category_counts = {}
        for recipe in recipes:
            cat = recipe.get('category', 'Main Course')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        most_common_cat = max(category_counts, key=category_counts.get)
        st.metric("Most Common", most_common_cat)
    
    with col4:
        favorite_count = sum(1 for r in recipes if r.get('is_favorite', False))
        st.metric("⭐ Favorites", favorite_count)

#export csv
if recipes:
    st.subheader("💾 Export Data")
    if st.button("Download Recipes as CSV"):
        # Flatten recipes for CSV
        csv_data = []
        for recipe in recipes:
            csv_data.append({
                'Name': recipe['name'],
                'Category': recipe.get('category', 'Main Course'),
                'Ingredients': ', '.join(recipe['ingredients']),
                'Instructions': recipe['instructions'],
                'Prep Time (min)': recipe['prep_time'],
                'Difficulty': recipe['difficulty'],
                'YouTube URL': recipe.get('youtube_url', ''),
                'Favorite': 'Yes' if recipe.get('is_favorite', False) else 'No',
                'Created': recipe['created_at']
            })
        
        df = pd.DataFrame(csv_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="my_recipes.csv",
            mime="text/csv"
        )

st.markdown("---")
