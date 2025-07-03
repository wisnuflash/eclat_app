FROM python:3.13

WORKDIR /app
# Install system dependencies
COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

# Set the default command to run when the container starts
EXPOSE 5000
CMD ["python3", "-m", "streamlit", "run", "app.py"]
# CMD ["python -m streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]