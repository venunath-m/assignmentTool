# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir streamlit wikipedia duckduckgo-search python-docx fpdf2 requests pillow

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "assignment_generator_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
