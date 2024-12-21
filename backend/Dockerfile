# Base image
FROM python:3.10-slim

# Working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./  
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . ./

# Add wait-for-it.sh
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expose port
EXPOSE 5000

# Command to wait for PostgreSQL before starting Flask
CMD ["/wait-for-it.sh", "db:5432", "--", "flask", "run", "--host=0.0.0.0"]
