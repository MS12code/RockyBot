# 🥊 News Research Tool : RockyBot 📈

RockyBot is a beginner-friendly GenAI-powered web application that allows users to perform news research. Users can input up to three news article URLs, extract their contents, split the text into manageable chunks, embed them, store them in a local FAISS vector database, and ask questions about the articles. The answers are generated using Retrieval-Augmented Generation (RAG) powered by LangChain, HuggingFace Embeddings, and Groq's Llama3 model.

---

Live Link : https://rockybot-9eopmokvevhakf88ayqlxp.streamlit.app/

## ✨ Features

- **Multi-URL Processing**: Enter up to three news article URLs in the sidebar to process them together.
- **Robust Scraping**: Automatically extracts text using LangChain loaders or falls back to a custom parser.
- **Sentence Embeddings**: Converts text chunks to vectors using `sentence-transformers/all-MiniLM-L6-v2` locally (no external API needed for embeddings).
- **Fast Vector Storage**: Persists the vector database locally in `faiss_store/` using FAISS.
- **RAG Answering**: Uses Groq Cloud's Llama3 model (`llama3-8b-8192`) via LangChain `RetrievalQA` to answer questions strictly based on the articles.
- **Direct Source Display**: Displays the exact source URLs of the article content used to generate the answer.
- **Beautiful Dark Theme UI**: Custom premium styling with animations and responsive layouts.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **RAG Framework**: LangChain
- **Vector Database**: FAISS (CPU)
- **Embeddings**: HuggingFace (`sentence-transformers`)
- **LLM**: Groq Chat (`llama3-8b-8192`)

---

## 🚀 Getting Started

### 1. Clone or Open the Directory
Open your terminal and navigate to the project directory:
```bash
cd RockyBot
```

### 2. Install Dependencies
Make sure you have Python 3.12+ installed. Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Setup API Key
Create a file named `.env` in the root directory (one is already generated for you) and add your Groq API Key:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Run the Application
Start the Streamlit development server:
```bash
streamlit run app.py
```

Streamlit will open the application in your default web browser (typically at `http://localhost:8501`).

---

## 📂 Project Structure

```
RockyBot/
│
├── app.py                  # Core application logic and Streamlit UI
├── requirements.txt        # List of package dependencies
├── .env                    # Environment variables (API Key)
├── README.md               # Setup and project guide
├── rockybot_sidebar.png    # App UI sidebar logo
└── faiss_store/            # Directory to store local FAISS index files
    ├── index.faiss
    ├── index.pkl
    └── processed_urls.txt
```

---

## 💡 How It Works (The Student's Guide)

1. **Document Loading**: The app reads raw HTML content from the specified URLs, parses and sanitizes the layout (removing headers, footers, scripts), and saves the plain text content.
2. **Text Chunking**: Using `RecursiveCharacterTextSplitter` with `chunk_size = 1000` and `chunk_overlap = 200`, the article text is broken into small chunks to fit the LLM's context window.
3. **Generating Embeddings**: Each text chunk is translated into a 384-dimensional vector using HuggingFace's local `all-MiniLM-L6-v2` transformer model.
4. **Vector Storage**: The vectors are loaded into a local FAISS index. When a user asks a question, the question is also embedded and the top 3 most similar chunks are retrieved.
5. **RAG QA Chain**: The retrieved chunks and the question are injected into a strict prompt template, which is sent to Groq's Llama3 model to formulate a factual answer. If the context does not contain enough info, the model outputs the default fallback response.
