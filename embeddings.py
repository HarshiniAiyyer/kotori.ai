from langchain_ollama import OllamaEmbeddings

def embeddita():
    em = OllamaEmbeddings(model='gemma2:2b')
    return em

