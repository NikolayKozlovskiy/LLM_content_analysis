# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Install the PostgreSQL development packages and other dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Verify openpyxl installation
RUN pip show openpyxl

# Download NLTK data
RUN python -m nltk.downloader punkt

# Make port 80 available to the world outside this container
EXPOSE 80

# Command to run the entrypoint script
ENTRYPOINT ["python", "entrypoint.py"]

