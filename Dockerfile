FROM tiangolo/uvicorn-gunicorn:python3.10
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
ENV PYTHONPATH=/app
# Run your app directly
# CMD ["fastapi", "run", "app/app.py", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
