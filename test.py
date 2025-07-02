from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="llama3.2")

template = """
You are a helpful cooking assistant. Based on the following recipe information retrieved from a database, answer the user's question or provide helpful cooking suggestions.

Context:
{context}

Question:
{question}

Answer in a friendly, concise, and helpful manner. If the information is not directly available, provide your best cooking suggestion using general knowledge, but mention that it’s not directly found in the recipes.

"""

prompt = ChatPromptTemplate.from_template(template=template)

chain = prompt | model

while True:
    print("\n\n--------------------------------------")
    question = input("Ask the AI agent anything (q to quit): ")
    print("\n\n")
    if question == "q":
        break

    context = retriever.invoke(question)
    result = chain.invoke({"context": context, "question": question})
    print(result)
