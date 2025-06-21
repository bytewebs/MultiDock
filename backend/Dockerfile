FROM python:3.11-slim
WORKDIR /app

COPY . .
RUN pip install -r requirements.txt
EXPOSE 5050
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5050", "backend:app"]
