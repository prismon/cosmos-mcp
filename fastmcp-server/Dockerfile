FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY server_dynamic_v2.py ./
COPY start_server.py ./

# Install dependencies
RUN uv sync --frozen

# Expose the port
EXPOSE 3443

# Run the server with proper environment setup
CMD ["uv", "run", "python", "start_server.py"]