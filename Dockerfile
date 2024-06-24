FROM python:3.9-slim-buster 

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "redesim2.py", "--server.port=8501"]
