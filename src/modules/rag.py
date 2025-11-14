from pathlib import Path
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config.config import Config
from src.config.logs import logger
import weaviate
from src.modules.db import Database
import os
from langchain_weaviate import WeaviateVectorStore

class Rag:
    def __init__(self):
        self.config = Config()
        os.environ["GOOGLE_API_KEY"] = self.config.GOOGLE_API_KEY
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.config.EMBEDDINGS_MODEL_NAME)
        self.model = GoogleGenerativeAI(model=self.config.LLM_MODEL_NAME)
        self.db = Database()


    def get_response(self, question: str, session_id: str) -> str:
        """Get a response from the RAG model.
        Args:
            question: The question to answer.
            session_id: The session ID to get the conversation history from.
        Returns:
            The response from the RAG model.
        """
        # Get conversation history from database
        try:
            messages = self.db.get_session(session_id)
            chat_history = ""
            if messages:
                chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            chat_history = ""
        
        # Template with chat history
        try:
            template_path = Path(__file__).parent / "../prompts" / "rag.jinja2"
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            # Contextualize the question
            prompt = PromptTemplate(
                input_variables=["chat_history", "context", "question"],
                template=template_content
            )
        except Exception as e:
            logger.error(f"Error creating prompt: {e}")

        # Use context manager to properly close the connection
        with weaviate.connect_to_local() as client:
            vectorstore = WeaviateVectorStore(
                client=client,
                index_name="Documents",
                text_key="text",
                embedding=self.embeddings,
            )
            # Create a retriever
            try:
                retriever = vectorstore.as_retriever(
                        search_type="similarity",
                        search_kwargs={"k": 5}
                    )
            except Exception as e:
                logger.error(f"Error creating retriever: {e}")
            # Create a retrieval chain
            retrieval_chain = (
                {
                    "context": retriever, 
                    "question": RunnablePassthrough(),
                    "chat_history": lambda _: chat_history
                }
                | prompt
                | self.model
                | StrOutputParser()
            )
            # Invoke the retrieval chain
            try:
                response = retrieval_chain.stream(question)
                for chunk in response:
                    yield chunk
            except Exception as e:
                logger.error(f"Error invoking retrieval chain: {e}")
                yield f"Error invoking retrieval chain: {e}"

if __name__ == "__main__":
    rag = Rag()
    response = rag.get_response("Your question here")
    logger.info(response)
