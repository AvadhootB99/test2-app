# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 5000 (the port our Flask app runs on)
EXPOSE 5000

# Run the Flask application
# Gunicorn is a production-ready WSGI server. For this simple example, we'll use Flask's built-in server.
# For production, you'd typically use Gunicorn like: CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
CMD ["python", "app.py"]
