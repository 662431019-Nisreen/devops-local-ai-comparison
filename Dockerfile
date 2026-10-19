FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OTEL_SDK_DISABLED=true \
    CREWAI_TRACING_ENABLED=false \
    CREWAI_STORAGE_DIR=/data/crewai
WORKDIR /app
COPY requirements.txt requirements-docker.txt ./
RUN pip install --no-cache-dir -r requirements-docker.txt
COPY crewai_helper.py chat_input.py translate_text.py read_pdf.py app.py plan_tasks.py review_python.py agent_server.py ./
EXPOSE 8080
CMD ["python", "agent_server.py"]
