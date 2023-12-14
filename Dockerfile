FROM python:3.8

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY labels.txt .

ENV PORT=8000

EXPOSE 8000

CMD ["python", "app.py"]