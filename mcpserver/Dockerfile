FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mcp_server.py .


ENV FAST_MCP_HOST=0.0.0.0
ENV FAST_MCP_PORT=8000

CMD ["python", "mcp_server.py"]