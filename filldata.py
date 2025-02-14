from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from embeddings import embeddita
from langchain.vectorstores import Chroma


############################ LOADING THE PDFS INTO THE FUNCTION ####################################
def load_documents():
    docloader = PyPDFDirectoryLoader(r"data")
    return docloader.load()

############################ SPLITTING DOCUMENTS TO AVOID RECURSION ############################
def split_documents(documents: list[Document]): 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 800,
        chunk_overlap = 200,
        length_function = len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

################### ADDING TO THE DATABASE. WE SPLIT THE CHUNKS PROPERLY ###########################

def addchroma(chunks: list[Document]):
    db = Chroma(
        persist_directory='chroma', embedding_function=embeddita()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []  # Initialize new_chunks here
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks) > 0:
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")


########################### ADDING AND UPDATING NEW CHUNKS.######################################
#every chunk has a page number and what file source its from. 
#we assign an id to every chunk to check if the database has the existing chunk, if not we add it.

#some chunks might share the same id, due to the same page number
#so we increment the index of the chunk, hence keeping the chunk id unique

def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


documents = load_documents()[0:11]
print(f"Number of documents loaded: {len(documents)}")

chunks = split_documents(documents)
print(f"Number of chunks: {len(chunks)}")
print(f"First chunk: {chunks[0]}")

# Add to Chroma
addchroma(chunks)
print("Finished adding to Chroma DB")


    