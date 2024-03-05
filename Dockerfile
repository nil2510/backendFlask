FROM python:3.12.2
WORKDIR /app
COPY requirements.txt .
# RUN apt-get update && apt-get install -y build-essential cmake
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask","run","--host","0.0.0.0"]