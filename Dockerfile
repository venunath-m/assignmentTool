# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code, fonts, assets, and .env
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Set environment variables (optional fallback)
# ENV OPENAI_API_KEY="your_openai_key_here"

# Run Streamlit app
CMD ["streamlit", "run", "assignment_generator_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
