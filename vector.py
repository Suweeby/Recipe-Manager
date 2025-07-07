import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import json

with open('recipes.json', 'r') as f:
    recipes = json.load(f)

embeddings = OllamaEmbeddings(model="mxbai-embed-large")
db_location = "./chroma_langchain_db"
add_docs = not os.path.exists(db_location)

if add_docs:
    documents = []
    ids = []

    for i, recipe in enumerate(recipes):
        ingredients_str = "\n- " + "\n- ".join(recipe["ingredients"])

        content = (
            f"Name: {recipe['name']}\n"
            f"Category: {recipe['category']}\n"
            f"Difficulty: {recipe['difficulty']}\n"
            f"Ingredients:{ingredients_str}\n"
            f"Instructions:\n{recipe['instructions']}\n"
        )
        document = Document(
            page_content=content,
            metadata={"id": recipe["id"], "name": recipe["name"], "prep_time": recipe["prep_time"], "date": recipe["created_at"]},
            id = str(i)
        )
        ids.append(str(i))
        documents.append(document)

vector_store = Chroma(
    collection_name="recipes",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_docs:
    vector_store.add_documents(documents=documents, ids=ids)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)
