import sqlite3
import streamlit as st
from memoir_rag import search_across_chunks

# Helper functions for database operations
def load_memoir_from_db(conn, memoir_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT memoirs.author, memoir_chunks.content, memoir_chunks.image_path
        FROM memoirs
        JOIN memoir_chunks ON memoir_chunks.memoir_id = memoirs.id
        WHERE memoirs.id = ?
    ''', (memoir_id,))
    return cursor.fetchall()

def display_memoir_content(memoir_data):
    for author, chunk, image_path in memoir_data:
        if image_path:
            st.image(
                image_path,
                caption="Generated by Monster API",
                use_container_width=True
            )
        st.write(chunk)

def handle_user_question(conn, user_input, memoir_id, author):
    return search_across_chunks(conn, user_input, memoir_id, author)

# Main Streamlit app
def main():
    # Sidebar for API keys
    st.sidebar.title("API Key Configuration")
    groq_api_key = st.sidebar.text_input("Enter your GROQ API Key:", type="password")
    monster_api_key = st.sidebar.text_input("Enter your Monster API Key:", type="password")

    # Store keys in session state
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

    # Save entered keys
    if groq_api_key and monster_api_key:
        st.session_state.api_keys["GROQ_API_KEY"] = groq_api_key
        st.session_state.api_keys["MONSTER_API_KEY"] = monster_api_key
        st.sidebar.success("API Keys successfully configured!")

    # Ensure keys are provided before proceeding
    if not st.session_state.api_keys.get("GROQ_API_KEY") or not st.session_state.api_keys.get("MONSTER_API_KEY"):
        st.warning("Please enter both API keys in the sidebar to continue.")
        return

    # Main application title
    st.title("Alan's Memoir: Interactive Q&A")

    # Load database connection
    conn = sqlite3.connect('memoirs.db')
    memoir_id = 1  # Modify based on desired memoir ID
    memoir_data = load_memoir_from_db(conn, memoir_id)

    # Display memoir content
    display_memoir_content(memoir_data)

    # Fetch author for user questions
    author = memoir_data[0][0] if memoir_data else None

    # Input for user question
    user_input = st.text_input("Ask a question about the memoir:")
    if user_input and author:
        response = handle_user_question(conn, user_input, memoir_id, author)
        st.write(f"**Answer:** {response}")

if __name__ == "__main__":
    main()
