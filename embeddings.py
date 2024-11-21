from langchain_ollama import OllamaEmbeddings

def embeddita():
    em = OllamaEmbeddings(model='llama3.2:1b')
    return em

