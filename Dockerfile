FROM python:3.12-slim

WORKDIR /app

# Install UV to manage dependencies
RUN pip install uv
# Copy requirements first to leverage Docker cache
COPY pyproject.toml .
# Install dependencies
RUN uv pip install --system -e .

# Copy the rest of the application
COPY . .

# Create directories for persistent data
RUN mkdir -p /app/chroma_db && \
    chmod 777 -R /app/chroma_db

# Define volumes for persistent data
VOLUME ["/app/chroma_db", "/app/chat_history.db"]

# Set the entrypoint
ENTRYPOINT ["streamlit", "run", "main.py"]

# Expose the port
EXPOSE 8501