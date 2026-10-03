import os
from urllib import response
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")






# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )
#embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)


# Clear any existing collection before creating a new one, so re-running this cell is always safe
# Chroma(embedding_function=embeddings, persist_directory="./chroma_db").delete_collection()

# vectorstore = Chroma.from_documents(
#     documents=chunks,
#     embedding=embeddings,
#         persist_directory="./chroma_db"
# )


vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)




if vectorstore._collection.count() == 0:

    loader = PyPDFDirectoryLoader("docs", glob="moon.pdf",recursive=True)
    docs = loader.load()
    print(f"Loaded {len(docs)} pages")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks")

    print(f"Vector Database Created Successfully with {vectorstore._collection.count()} chunks")


    vectorstore.add_documents(chunks)   # FIX 2: chunks were never saved to the index
    print(f"Vector Database Created Successfully with {vectorstore._collection.count()} chunks")

retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# while True:
    
    


#     retrieved_chunks = retriever.invoke(question)
#     for i, chunk in enumerate(retrieved_chunks):
#         print(f"--- Chunk {i+1} (source: {chunk.metadata.get('source')}) ---")
#         print(chunk.page_content)
#         print()
#     context = "\n\n".join(
#         f"[{c.metadata['source']}]\n{c.page_content}" for c in retrieved_chunks
#     )

SYSTEM_PROMPT = """You are a precise document-analysis assistant.

- Answer only using the provided context — no outside knowledge, no guessing.
- The context may contain multiple documents, each labeled with its source. Never mix facts across documents.
- If a name or term could match multiple different entities, don't pick one silently — list each match separately with its source.
- If the answer isn't in the context, reply exactly: "I couldn't find the answer in the provided document(s)."
- Mention which document your answer came from when possible
- If the context is a table or list of items with amounts, present ALL of them, one per line, as "Item: amount".
- Otherwise answer in short plain sentences.
- Do not use bold text. .
."""

def answer_question(question):
    retrieved_chunks = retriever.invoke(question)
    for i, chunk in enumerate(retrieved_chunks):
        print(f"--- Chunk {i+1} (source: {chunk.metadata.get('source')}) ---")
        print(chunk.page_content)
        print()
    context = "\n\n".join(
        f"[{c.metadata['source']}]\n{c.page_content}" for c in retrieved_chunks
    )

    prompt = f"""{SYSTEM_PROMPT}

        Context:
        {context}

        Question:
        {question}
        """

    response = llm.invoke(prompt)

    return response.content