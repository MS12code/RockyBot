import os
import shutil
import time
from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
import streamlit as st

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="News Research Tool : RockyBot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Copy the generated image if present in the brain folder to local app directory
IMAGE_SOURCE_PATH = r"C:\Users\LENOVO\.gemini\antigravity-ide\brain\4593fe0d-9232-44cf-8925-1103f57fd40a\rockybot_sidebar_1782270124389.png"
IMAGE_DEST_PATH = "rockybot_sidebar.png"

if os.path.exists(IMAGE_SOURCE_PATH) and not os.path.exists(IMAGE_DEST_PATH):
    try:
        shutil.copy(IMAGE_SOURCE_PATH, IMAGE_DEST_PATH)
    except Exception:
        pass

# Inject Premium Dark Theme CSS
st.markdown("""
    <style>
        /* Force Dark Theme Styles */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0b0f19 !important;
            color: #f1f5f9 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid #1e293b;
        }
        
        /* Typography overrides */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
        }
        
        /* Titles */
        .title-glow {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        /* Inputs styling */
        div[data-baseweb="input"] {
            background-color: #1e293b !important;
            border-radius: 8px !important;
            border: 1px solid #334155 !important;
        }
        
        div[data-baseweb="input"] input {
            color: #f1f5f9 !important;
        }
        
        /* Style text inputs */
        .stTextInput input {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
        }
        
        /* Button styling matching the mockup */
        div.stButton > button {
            background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%) !important;
            color: #ffffff !important;
            border: none !important;
            padding: 0.6rem 1.8rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25) !important;
        }
        div.stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 16px rgba(6, 182, 212, 0.35) !important;
        }
        
        /* Answer Section Container */
        .answer-container {
            background-color: #111827 !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            border-left: 4px solid #a855f7 !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
        }
        
        /* Info banner customizations */
        .stAlert {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        
        /* Clickable source links */
        .source-link {
            color: #38bdf8 !important;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }
        .source-link:hover {
            color: #7dd3fc !important;
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Configuration & Paths -----------------

FAISS_STORE_PATH = "faiss_store"
URL_FILE_PATH = os.path.join(FAISS_STORE_PATH, "processed_urls.txt")

# Ensure local storage directory exists
os.makedirs(FAISS_STORE_PATH, exist_ok=True)

# ----------------- Sidebar Layout -----------------

st.sidebar.markdown("## News Article URLs")

# Show logo/robot image in sidebar if it exists
if os.path.exists(IMAGE_DEST_PATH):
    st.sidebar.image(IMAGE_DEST_PATH, width='stretch')

# Load previously processed URLs if they exist
stored_urls = []
if os.path.exists(URL_FILE_PATH):
    try:
        with open(URL_FILE_PATH, "r", encoding="utf-8") as f:
            stored_urls = [line.strip() for line in f.read().splitlines() if line.strip()]
    except Exception:
        pass

# Populate URL inputs with previous values if available
val_url1 = stored_urls[0] if len(stored_urls) > 0 else ""
val_url2 = stored_urls[1] if len(stored_urls) > 1 else ""
val_url3 = stored_urls[2] if len(stored_urls) > 2 else ""

url1 = st.sidebar.text_input("URL 1", value=val_url1, placeholder="Enter first news URL")
url2 = st.sidebar.text_input("URL 2", value=val_url2, placeholder="Enter second news URL (Optional)")
url3 = st.sidebar.text_input("URL 3", value=val_url3, placeholder="Enter third news URL (Optional)")

process_button = st.sidebar.button("Process URLs")

# Display a helper warning if GROQ_API_KEY is not defined
if not os.getenv("GROQ_API_KEY"):
    st.sidebar.warning("🔑 GROQ_API_KEY is missing in your .env file.")

# URL Processing Trigger
if process_button:
    input_urls = [u.strip() for u in [url1, url2, url3] if u.strip()]
    
    if not input_urls:
        st.sidebar.error("Please enter at least one URL.")
    else:
        # Show a loading spinner during the whole extraction and embedding pipeline
        with st.spinner("Processing articles (downloading, chunking, and indexing)..."):
            try:
                # 1. Load articles using WebBaseLoader with a custom User-Agent
                from langchain_community.document_loaders import WebBaseLoader
                loader = WebBaseLoader(
                    web_paths=input_urls,
                    header_template={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }
                )
                docs = loader.load()
                
                if not docs or len(docs) == 0:
                    raise ValueError("No text could be extracted from the provided URLs.")
                
                # 2. Text Chunking
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = text_splitter.split_documents(docs)
                
                if not chunks:
                    raise ValueError("The extracted text is empty or too short to split.")
                
                # 3. Create HuggingFace Embeddings
                from langchain_huggingface import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                
                # 4. Save to FAISS Vector Database locally
                from langchain_community.vectorstores import FAISS
                vectorstore = FAISS.from_documents(chunks, embeddings)
                vectorstore.save_local(FAISS_STORE_PATH)
                
                # Save processed URLs to verify later
                with open(URL_FILE_PATH, "w", encoding="utf-8") as f:
                    for url in input_urls:
                        f.write(url + "\n")
                
                st.sidebar.success("Successfully processed articles!")
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

# ----------------- Main Interface -----------------

st.markdown('<h1 style="margin-bottom: 0.5rem;"><span class="title-glow">News Research Tool : RockyBot</span> 📈</h1>', unsafe_allow_html=True)

# Verify if index files exist on local disk
index_file = os.path.join(FAISS_STORE_PATH, "index.faiss")
index_exists = os.path.exists(index_file)

if index_exists and stored_urls:
    st.info(f"Loaded Context from:  \n" + "  \n".join([f"- `{url}`" for url in stored_urls]))
    
    # Input question from user
    st.markdown("### Ask a Question:")
    question = st.text_input("Question:", placeholder="Ask something about the processed articles...", label_visibility="collapsed")
    
    if question.strip():
        if not os.getenv("GROQ_API_KEY"):
            st.error("Please add your `GROQ_API_KEY` in the `.env` file to answer your question.")
        else:
            with st.spinner("Searching context and generating answer..."):
                try:
                    # 1. Load local FAISS Store
                    from langchain_huggingface import HuggingFaceEmbeddings
                    from langchain_community.vectorstores import FAISS
                    
                    embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2"
                    )
                    vectorstore = FAISS.load_local(FAISS_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
                    
                    # 2. Setup LLM (Groq Chat Model)
                    from langchain_groq import ChatGroq
                    llm = ChatGroq(
                        model_name="llama-3.1-8b-instant",
                        temperature=0
                    )
                    
                    # 3. Setup QA Chain using LCEL
                    from langchain_core.prompts import PromptTemplate
                    from langchain_core.runnables import RunnableParallel, RunnablePassthrough
                    from langchain_core.output_parsers import StrOutputParser
                    
                    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
                    
                    # RAG Prompt constraint template
                    prompt_template = """Use the following pieces of context to answer the question at the end. 
If the article does not contain enough information or if you do not know the answer, respond exactly with:
"The article does not contain enough information to answer this question."
Do not make up or extrapolate answers beyond the provided context.

Context:
{context}

Question: {question}

Helpful Answer:"""
                    
                    QA_CHAIN_PROMPT = PromptTemplate(
                        template=prompt_template,
                        input_variables=["context", "question"]
                    )
                    
                    def format_docs(docs):
                        return "\n\n".join(doc.page_content for doc in docs)
                        
                    rag_chain_from_docs = (
                        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
                        | QA_CHAIN_PROMPT
                        | llm
                        | StrOutputParser()
                    )
                    
                    rag_chain_with_source = RunnableParallel(
                        {"context": retriever, "question": RunnablePassthrough()}
                    ).assign(answer=rag_chain_from_docs)
                    
                    # 4. Invoke the QA Chain
                    response = rag_chain_with_source.invoke(question)
                    answer = response["answer"]
                    source_docs = response["context"]
                    
                    # Display Answer Box
                    st.markdown("### Answer")
                    st.markdown(f'<div class="answer-container">{answer}</div>', unsafe_allow_html=True)
                    
                    # Collect and display source documents
                    if source_docs:
                        unique_sources = set()
                        for doc in source_docs:
                            src_url = doc.metadata.get("source")
                            if src_url:
                                unique_sources.add(src_url)
                        
                        if unique_sources:
                            st.markdown("### Sources:")
                            for src in unique_sources:
                                st.markdown(f'- <a href="{src}" target="_blank" class="source-link">{src}</a>', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Failed to fetch answer. Error: {str(e)}")
else:
    st.info("💡 To start, enter one or more news article URLs in the sidebar and click **Process URLs** to build your local knowledge base.")
