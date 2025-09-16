# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy all Python files and maintain directory structure
COPY . /app/

# Install dependencies from the requirements.txt mounted at build time
RUN --mount=type=bind,source=requirements.txt,target=/requirements.txt \
    pip install --no-cache-dir --default-timeout=100 -r /requirements.txt

# Expose the port your Gradio app will run on
EXPOSE 7860

# Run the application
CMD ["python", "/app/app.py"]
