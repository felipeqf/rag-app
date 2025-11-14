# RAG Research Assistant

A Retrieval-Augmented Generation (RAG) application that allows users to interact with an AI assistant that answers questions based on PDF documents using Google's Gemini AI and Weaviate vector database.

## What It Is

This is a document-based question-answering system that combines:

- **Vector Search**: Weaviate for efficient semantic search
- **LLM**: Google Gemini for natural language understanding and generation
- **Modern UI**: Streamlit-based chat interface with Google authentication
- **Persistence**: SQLite for chat history and session management

## Features

- 📄 **PDF Document Ingestion**: Upload and process PDF documents into a searchable vector database
- 💬 **Conversational AI**: Chat with an AI assistant that retrieves relevant information from your documents
- 🔐 **Google Authentication**: Secure login with Google OAuth
- 📚 **Session History**: Save and resume previous conversations
- 🎨 **Modern UI**: Clean, responsive chat interface built with Streamlit
- 🔄 **Real-time Streaming**: Streaming responses for better user experience
- 🐳 **Dockerized**: Easy deployment with Docker Compose

## Tech Stack

- **Framework**: Python 3.12+
- **LLM**: Google Gemini (via LangChain)
- **Vector Database**: Weaviate
- **Embeddings**: Google Generative AI Embeddings
- **UI**: Streamlit
- **Database**: SQLite (chat history)
- **Orchestration**: LangChain

## How to Run

### Prerequisites

- Docker and Docker Compose installed
- Google API Key (for Gemini API)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/felipeqf/rag-app.git
   cd rag
   ```

2. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. **Configure Google OAuth**

   Follow the [Streamlit Google Auth Platform tutorial](https://docs.streamlit.io/develop/tutorials/authentication/google) to set up Google OAuth authentication. You'll need to create a `.streamlit/secrets.toml` file with your Google OAuth credentials.

4. **Load Documents into Vector Database**


Place your PDF files in the `src/documents/` directory.


```bash
# Install dependencies
uv sync

# Load documents
python -m src.modules.load_documents
```

5. **Start the application**

   ```bash
   docker-compose up
   ```

6. **Access the application**

   Open your browser and navigate to:

   - **Streamlit UI**: http://localhost:8501
   - **Weaviate**: http://localhost:8080

## Project Structure

```
rag/
├── src/
│   ├── config/          # Configuration and logging
│   ├── documents/       # PDF documents directory
│   ├── modules/         # Core application modules
│   │   ├── db.py           # Database operations
│   │   ├── rag.py          # RAG logic and retrieval
│   │   ├── load_documents.py  # Document ingestion
│   │   └── streamlit_ui.py    # UI implementation
│   └── prompts/         # LLM prompt templates
├── docker-compose.yaml  # Docker services configuration
├── Dockerfile           # Application container
└── pyproject.toml       # Python dependencies
```

## Usage

1. **Login**: Click "Log in with Google" to authenticate
2. **Ask Questions**: Type your questions in the chat input
3. **View History**: Access previous conversations from the sidebar
4. **New Conversation**: Start a new chat session anytime

## Configuration

Key configuration parameters in `src/config/config.py`:

- LLM model selection
- Embedding model configuration
- Chunk size for document splitting
- Vector search parameters

## Stopping the Application

```bash
docker-compose down
```

To remove volumes as well:

```bash
docker-compose down -v
```
