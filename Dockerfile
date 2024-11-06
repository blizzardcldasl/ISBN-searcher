# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /config

# Install Git
RUN apt-get update && apt-get install -y git && apt-get clean

# Clone the repository into /config
RUN git clone https://github.com/blizzardcldasl/ISBN-searcher.git /config

# Install dependencies
RUN pip install --no-cache-dir -r /config/requirements.txt

# Expose port 13989 for the Flask app
EXPOSE 13989

# Run the Flask app
CMD ["python", "app.py"]