FROM python:3.11-slim

# Set workspace directory
WORKDIR /code

# Copy requirements if any exist (comments only, but good practice)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy all files into the container
COPY . .

# Hugging Face Spaces run on port 7860 by default
ENV PORT=7860
EXPOSE 7860

# Run the python backend server
CMD ["python", "backend/main.py"]
