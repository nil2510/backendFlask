FROM python:3.12.1

# Set working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

RUN python manage.py create_db

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
