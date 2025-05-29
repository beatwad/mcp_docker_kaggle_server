# Use an official Python runtime as a parent image
FROM python:3.12.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create .kaggle directory for kaggle.json.
# Path.home() for root user is /root. auth.py will create ~/.kaggle/kaggle.json.
# This ensures the directory exists and has appropriate permissions if needed by Kaggle CLI.
RUN mkdir -p /root/.kaggle && \
    chmod 700 /root/.kaggle

# Copy the application code into the container
COPY tools ./tools
COPY server.py .
COPY kaggle.json /root/.kaggle/kaggle.json

# Expose the port the app runs on (default for SSE is 3000)
EXPOSE 3000

# Define the command to run the application
# Runs server.py with SSE transport, listening on all interfaces inside the container.
# KAGGLE_USERNAME and KAGGLE_KEY should be passed as environment variables.
CMD ["python", "server.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "3000"]