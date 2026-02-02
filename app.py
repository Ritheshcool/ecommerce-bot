import streamlit as st
import psycopg2
import faiss
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer
import os

from dotenv import load_dotenv

load_dotenv() # This loads the variables from the .env file

api_key = os.getenv("GROQ_API_KEY")

db_config = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

st.set_page_config(page_title="ShopAssistant AI", layout="centered")
st.title("🛍️ ShopAssistant (FAISS + Postgres)")

# --- LOAD DATA ---
@st.cache_resource
def initialize_search_engine():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT id, name, description FROM products")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if not rows: return None, None, [], []

        # Embeddings & FAISS
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        text_data = [f"{r[1]}: {r[2]}" for r in rows] 
        product_ids = [r[0] for r in rows]            
        
        embeddings = embedder.encode(text_data)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension) 
        index.add(np.array(embeddings))
        
        return embedder, index, product_ids, text_data
    except Exception as e:
        st.error(f"❌ DB Error: {e}")
        return None, None, [], []

embedder, faiss_index, product_ids, all_texts = initialize_search_engine()
client = Groq(api_key=GROQ_API_KEY)

# --- SEARCH FUNCTION (UPDATED) ---
def search_products(query):
    if faiss_index is None: return None
    
    # 1. Find ID via FAISS
    query_vector = embedder.encode([query])
    distances, indices = faiss_index.search(np.array(query_vector), k=1)
    if indices[0][0] == -1: return None 
    real_product_id = product_ids[indices[0][0]]
    
    # 2. Get Details via Postgres
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    # UPDATED: Added 'description' to the SELECT statement
    cur.execute("SELECT name, price, stock, description FROM products WHERE id = %s", (real_product_id,))
    result = cur.fetchone()
    conn.close()
    return result

# --- CHAT UI ---
if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Handle User Input
if prompt := st.chat_input("I'm looking for..."):
    # 1. Add User Message to History
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- SMARTER SEARCH LOGIC (Contextual Search) ---
    # If we have a previous bot response, we combine it with the new question.
    # This helps the search engine know we are still talking about the "Laptop".
    search_query = prompt
    if len(st.session_state.messages) > 1:
        # Get the last message from the bot (history matches user, bot, user, bot...)
        last_bot_message = st.session_state.messages[-2]["content"]
        
        # Combine them: "Old Context + New Question"
        # Example: "The laptop has 16GB RAM... What is the size?"
        search_query = last_bot_message + " " + prompt
    
    # Run the search with the ENHANCED query
    product_data = search_products(search_query) 
    # ------------------------------------------------
    
    if product_data:
        name, price, stock, description = product_data
        
        if stock > 0:
            stock_msg = f"In Stock ({stock} available)"
        else:
            stock_msg = "❌ Currently Out of Stock"

        rag_info = f"""
        Search Result from Database:
        Product: {name}
        Price: ${price}
        Status: {stock_msg}
        Detailed Specs/Features: {description}
        """
    else:
        rag_info = "Search Result: No direct product match found in database for this specific sentence."

    # 3. Construct the "Brain"
    system_prompt = f"""
    You are a helpful sales assistant for 'TechStore'.
    
    LATEST DATA FROM DATABASE:
    {rag_info}
    
    STRICT INSTRUCTIONS:
    1. Answer based ONLY on the 'LATEST DATA' and the previous chat history.
    2. If the 'LATEST DATA' seems irrelevant (e.g., user asks about Laptop size but data is about a Chair), IGNORE the 'LATEST DATA' and try to answer from the Previous Chat History if possible.
    3. If the user asks for features (e.g., "tell me more", "RAM", "battery"), READ the 'Detailed Specs/Features' field.
    4. Be polite but honest.
    """

    api_messages = [{"role": "system", "content": system_prompt}] 
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages, 
            stream=True
        )
        
        def stream_data():
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        response = st.write_stream(stream_data)
    
    st.session_state.messages.append({"role": "assistant", "content": response})