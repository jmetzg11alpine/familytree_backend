FROM python:3.11.4-slim
WORKDIR /backend
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["python", "populate_database.py" "&&" "python", "main.py"]
