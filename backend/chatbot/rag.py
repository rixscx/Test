import os
import openai
from dotenv import load_dotenv
import numpy as np

# --- 1. CONFIGURATION & INITIALIZATION ---
load_dotenv()

# Configure the OpenAI API client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")
    client = openai.OpenAI(api_key=api_key)
except Exception as e:
    print(f"Error configuring OpenAI client: {e}")
    client = None

# --- 2. KNOWLEDGE BASE & EMBEDDINGS ---
KNOWLEDGE_BASE = {
    "what is eden": "Eden is a modern culinary insights tool, designed to analyze food images and provide detailed nutritional and ingredient information.",
    "how does the analyzer work": "The analyzer uses a deep learning model to identify a dish from an image. It then breaks down the dish into its likely ingredients and estimates nutritional values like calories, proteins, fats, and carbs.",
    "what are recipes": "The recipes feature allows you to find cooking instructions for the dish identified by the analyzer. It helps you recreate the meal at home.",
    "who is pipo": "Pipo is the integrated AI assistant for Eden. I'm here to answer your questions about the platform, help you navigate its features, and provide general information.",
    "what technologies does eden use": "Eden's backend is built with Django and Django REST Framework. The frontend is a modern Vue.js application. The AI and analysis features leverage PyTorch and OpenAI's GPT models.",
    "can I save my analysis": "Yes, after an image is analyzed, you have an option to save the detailed breakdown as a JSON file for your records.",
    "is eden free": "The current version of Eden is a demonstration project and is free to use.",
    "how do I use the guestbook": "The guestbook is a place to leave comments or feedback. Simply navigate to the Guestbook page and add your entry.",
    "troubleshooting analyzer failed": "If an analysis fails, first ensure the backend server is running. If it is, the model may not have been able to identify the dish in the image. Try a clearer, more direct photo of the food.",
    "default": "I'm sorry, I don't have information on that topic right now. My knowledge is focused on the Eden platform and its features. Please ask me about the analyzer, recipes, or other aspects of Eden."
}

documents = list(KNOWLEDGE_BASE.values())
doc_embeddings = None

def compute_embeddings():
    """Computes embeddings for the knowledge base documents using the OpenAI API."""
    global doc_embeddings
    if not client:
        print("OpenAI client is not configured. Cannot compute embeddings.")
        return

    try:
        response = client.embeddings.create(input=documents, model="text-embedding-ada-002")
        doc_embeddings = np.array([item.embedding for item in response.data])
        print("Knowledge base embeddings computed successfully.")
    except Exception as e:
        print(f"Error computing embeddings with OpenAI: {e}")
        doc_embeddings = None

# Removed global compute_embeddings() call

# --- 3. CORE RAG LOGIC ---
def find_best_passage(query, embeddings, texts):
    """Finds the most relevant passage from the knowledge base using vector similarity."""
    if embeddings is None or client is None:
        print("Embeddings or OpenAI client not available.")
        return KNOWLEDGE_BASE["default"]

    try:
        query_embedding_response = client.embeddings.create(input=[query], model="text-embedding-ada-002")
        query_embedding = np.array(query_embedding_response.data[0].embedding)

        dot_products = np.dot(embeddings, query_embedding)
        norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)

        if np.all(norms == 0):
            return KNOWLEDGE_BASE["default"]

        similarities = dot_products / norms

        if np.max(similarities) < 0.75: # Adjusted threshold for better relevance
            return KNOWLEDGE_BASE["default"]

        best_doc_index = np.argmax(similarities)
        return texts[best_doc_index]

    except Exception as e:
        print(f"Error finding best passage: {e}")
        return KNOWLEDGE_BASE["default"]

def get_rag_response(user_query):
    """Generates a response using the RAG model with OpenAI's ChatCompletions."""
    if doc_embeddings is None:
        compute_embeddings()
    if doc_embeddings is None or client is None:
        return "My apologies, my knowledge systems are currently offline. Please try again later."

    context = find_best_passage(user_query, doc_embeddings, documents)

    system_prompt = """
    You are Pipo, the helpful AI assistant for a culinary analysis platform called Eden.
    Your personality is professional, slightly futuristic, and very helpful.
    A user has asked a question. Use the provided context to answer them.
    If the context doesn't have the answer, state that you don't have information on that topic, but remain helpful.
    """

    user_prompt = f"""
    Context: "{context}"

    User's Question: "{user_query}"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating content with OpenAI model: {e}")
        return "I seem to be having trouble accessing my core functions. Please try again in a moment."
