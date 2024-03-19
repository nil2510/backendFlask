FROM python:3.12.2
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask","run","--debug","--host","0.0.0.0"]