# Use official Python image
FROM python:3.13

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
# Download the latest installer
ADD https://astral.sh/uv/0.5.25/install.sh /uv-installer.sh
# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 3001

# Environment Variables
ARG DB_CONNECTION_STRING
ARG API_KEY
ARG APP_ENVIRONMENT

# Run the application
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "3001"]
