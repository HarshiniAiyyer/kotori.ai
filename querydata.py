from embeddings import embeddita
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM

PROMPT = """
Answer the question based only on the following context:

{context}     

---

Answer the question based on the above context: {question}
"""

#context -> all the chunks from our database that best matches the query
#question -> the actual question we wanna ask



def query_rag(query_text: str):
    embed = embeddita()
    db = Chroma(persist_directory='chroma', embedding_function=embed)

    #searching the db for the top 3 most relevant chunks as per our question
    #we can use this with the question text to generate the prompt

    results = db.similarity_search_with_score(query_text, k = 3)


    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = OllamaLLM(model="llama3.2:1b")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

# Example query
response = query_rag("who wrote the memoir Love Life? ")


