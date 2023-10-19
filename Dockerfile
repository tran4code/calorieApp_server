# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port app will run on
EXPOSE 5001

# Copy needed contents to run the Flask app
COPY . .

# Install wget and dockerize
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# dockerize is a utility to wait for MongoDB service to be available before inserting data
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Copy startup script
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]