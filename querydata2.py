from embeddings import embeddita
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document  

# Initialize conversation memory
memory = ConversationBufferMemory(return_messages=True)  

# Define prompt template
PROMPT = """
You are an expert assistant. Answer the given question clearly, concisely, and directly using only the provided context. 
Be sure to respond accordingly if you are being greeted. Keep the answers crisp. Do NOT summarize the context. 
Instead, provide **direct, actionable insights**. Use **bullet points or numbered steps** where relevant.
Keep the response **short, to the point, and helpful**.

**Context:** 
{context}

---

**Question:** {question}
"""

# Define greeting responses
GREETINGS = {
    "hi": "Hello! 😊 How can I help you today?",
    "hello": "Hey there! 👋 What would you like to ask?",
    "hey": "Hey! How can I assist you?",
    "hi kotori": "Hi! Kotori here! 🐦 What’s on your mind?",
    "hey kotori": "Hello! How can I help?",
    "good morning": "Good morning! ☀️ What can I do for you?",
    "good evening": "Good evening! 🌙 How can I assist?",
}


def query_rag(query_text: str):
    """
    Handles user queries:
    - If it's a greeting, returns a predefined response.
    - Otherwise, retrieves relevant information using a RAG approach.
    """

    # ✅ Check if the query is a greeting
    query_lower = query_text.strip().lower()
    if query_lower in GREETINGS:
        return GREETINGS[query_lower]

    # ✅ Initialize the embedding function & database
    embed = embeddita()
    db = Chroma(persist_directory='chroma', embedding_function=embed)

    # ✅ Retrieve relevant documents
    results = db.similarity_search_with_score(query_text, k=5)
    retrieved_texts = [doc.page_content for doc, _ in results]

    # ✅ Retrieve past conversation history
    past_results = db.similarity_search_with_score(f"CONVERSATION_HISTORY: {query_text}", k=5)
    past_texts = [doc.page_content for doc, _ in past_results]

    # ✅ Combine retrieved texts into context
    context_text = "\n\n---\n\n".join(retrieved_texts + past_texts)

    # ✅ Handle cases where no relevant information is found
    if not context_text.strip():
        return "I'm not sure about that. Could you rephrase your question?"

    # ✅ Construct the prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # ✅ Generate a response using Ollama LLM
    model = OllamaLLM(model="gemma2:2b", temperature=0.3, top_p=0.9)
    response_text = model.invoke(prompt)

    # ✅ Store the conversation history in the database
    conversation_doc = Document(
        page_content=f"User: {query_text}\nAssistant: {response_text}",
        metadata={"source": "conversation_history", "id": f"query_{hash(query_text)}"}
    )
    db.add_documents([conversation_doc], ids=[conversation_doc.metadata["id"]])

    # ✅ Extract sources from retrieved documents
    sources = [doc.metadata.get("id", None) for doc, _ in results]
    formatted_response = f"""
    
**Response:**
{response_text.strip()}

**Sources:**
{", ".join(str(src) for src in sources if src)}

"""
    print(formatted_response)

    return response_text

# Example query
response = query_rag("How to cope with Empty Nest Syndrome?")