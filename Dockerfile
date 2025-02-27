# Use official Python image
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first (for better caching)
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies
RUN poetry install --no-root

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 3001

# Environment Variables
ARG DB_CONNECTION_STRING
ARG API_KEY
ARG APP_ENVIRONMENT

# Run the application
CMD ["poetry", "run", "fastapi", "run", "app/main.py", "--port", "3001"]
