# Use base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy all files into the container's /app directory
COPY . /app/

# Install dependencies
RUN pip install -r requirements.txt

# Start the application using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
