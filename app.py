import streamlit as st
from querydata2 import query_rag  
import os
import sys




# Page Config
st.set_page_config(page_title="Kotori.ai", layout="wide")

# CSS Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #bdd1f8;
    }
    div[data-testid="stTextInput"] label {
        font-size: 20px !important;
        font-weight: bold;
    }
    .title-container {
        margin-top: 50px;
        text-align: left;  /* Ensure all text is left-aligned */
    }
    .response-container {
        margin-top: 30px;
    }
    [data-testid="stSidebar"] {
        background-color: #98C8E8 !important;
    }
    [data-testid="stSidebar"] * {
        color: #003366 !important;
    }
    img {
        border: 3px solid #1D3557 !important;
        border-radius: 8px;
    }
    div.stButton > button {
        background-color: #003366;
        color: white !important;
        font-weight: bold;
        border-radius: 5px;
        padding: 8px 16px;
    }
    div.stButton > button:hover {
        background-color: #98C8E8;
        color: #003366 !important;
        border: 2px solid #003366;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Page Title with Left Alignment & Different Heading Sizes
st.markdown('''
<h1 class="title-container" style="color: #003366; text-align: left;">
    <br> Feeling lonely and empty without your kids?  
    <br> You might be experiencing Empty Nest Syndrome.  
</h1>
<h2 class="title-container" style="color: #00509E; text-align: left;">
    <br> Ask Kotori.ai to learn more.  
</h2>
''', unsafe_allow_html=True)


# Sidebar: Image, About Section, and Chat History
with st.sidebar:
    st.image("assets/images/image.png", use_container_width=True)

    st.header("About")
    st.write("This chatbot retrieves and answers questions on Empty Nest Syndrome (ENS).")

    # Chat History Section
    st.subheader("History")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for i, chat in enumerate(reversed(st.session_state["chat_history"])):
        with st.expander(f" {chat['query']}", expanded=False):
            st.markdown(f"**Q:** {chat['query']}")
            st.markdown(f"**A:** {chat['response']}")

    # Clear Chat History Button
    if st.button("Clear Chat History?"):
        st.session_state["chat_history"] = []
        st.rerun()

# Ensure session state variables exist
if "query_text" not in st.session_state:
    st.session_state["query_text"] = ""

if "latest_query" not in st.session_state:
    st.session_state["latest_query"] = None

# User Input Field (Search Bar Only, No Clear Button)
query_text = st.text_input("", placeholder="Ask Kotori a question..", key="query_text")

# Process Query
if query_text and query_text != st.session_state.get("latest_query"):
    st.session_state["latest_query"] = query_text
    st.rerun()

def format_response(response):
    response = response.replace("\n", "<br>")  # Ensure new lines are handled
    response = response.replace("* ", "• ")  # Convert asterisks into bullet points
    response = response.replace("**", "<b>").replace("</b>", "</b>")  # Convert bold Markdown to HTML
    return response

# Process Stored Query After UI Refresh
if st.session_state["latest_query"]:
    with st.spinner("🔎 Generating a response..."):
        response = query_rag(st.session_state["latest_query"])  # Fetch response from query_rag()

    # Avoid duplicate queries in history
    if not st.session_state["chat_history"] or st.session_state["latest_query"] != st.session_state["chat_history"][-1]["query"]:
        st.session_state["chat_history"].append({"query": st.session_state["latest_query"], "response": response})

    # Keep only the last 10 messages
    MAX_HISTORY = 10  
    if len(st.session_state["chat_history"]) > MAX_HISTORY:
        st.session_state["chat_history"].pop(0)


     # Format response to handle bullet points and bold text properly
    formatted_response = format_response(response)

    # Display Response with Larger Font Size
    st.markdown(
        f'''
        <div class="response-container" style="background-color: #d6e4ff; padding: 15px; border-radius: 10px;">
            <p style="font-size: 22px; font-weight: bold; color: #222;">{formatted_response}</p>
        </div>
        ''',
        unsafe_allow_html=True
    )

    # Display Response
    #st.write(response)

    # Clear latest query after displaying the response
    st.session_state["latest_query"] = None
