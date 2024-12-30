# Use a Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for Flask app
ENV FLASK_APP=app.py

# Expose the port the app will run on
EXPOSE 5000

# Run the app using Gunicorn (production-ready)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
