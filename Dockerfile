FROM python:3.10-slim

WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Run main pipeline
CMD ["python", "scripts/main.py"]