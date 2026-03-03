# 🌍 Geo-Agent MCP: High-Performance Geography Assistant

This project implements an AI Agent that leverages the **Model Context Protocol (MCP)** to fetch real-time country data. It is optimized for **Open WebUI** on macOS (M-series) using **Ollama** and a "Warm" Dockerized MCP server to eliminate startup latency and maximize response speed.

---

## 🏗️ Project Structure

```text
.
├── agent
│   ├── agent.py            # Core LangChain Agent logic & tool binding
│   ├── main.py             # OpenAI-compatible FastAPI gateway for Open WebUI
│   └── requirements.txt    # LangChain, Ollama, and FastAPI dependencies
├── mcpserver
│   ├── Dockerfile          # Builds the persistent "Warm" SSE server
│   ├── mcp_server.py       # FastMCP server definition (Tools)
│   ├── restcountries_service.py  # Internal logic for API interaction
│   ├── requirements.txt    # fastmcp, uvicorn, and httpx
│   ├── test_with_fastmcp_client.py   # Local stdio testing utility
│   └── test_with_langchain_client.py # Local integration testing utility
├── install-ui.sh           # Shell script to deploy/update Open WebUI
├── README.md               # Project documentation
└── requirements.txt        # Full environment freeze for reproducibility
```

## ⚡ Performance Optimization

- Warm SSE Transport: Unlike standard MCP setups that spawn a new Docker process per request, this project uses a persistent container communicating via Server-Sent Events (SSE). This cuts tool-call latency by ~80%.

- Parallel Tool Calling: The agent is configured to handle multiple country lookups simultaneously (e.g., "Tell me about France, Spain, and Italy").

- Background Task Interceptor: main.py detects Open WebUI's background tasks (like title and tag generation) and routes them to a lighter 7b model without tool overhead, saving the 14b model for complex queries.

## 🚀 Installation & Setup
1. Prerequisites

    - Ollama: Installed and running on your Mac.

    - Models:
    ```Bash
    ollama pull qwen2.5:14b  # Primary Agent Brain
    ollama pull qwen2.5:7b   # Fast Background Tasks
    ```
    - Docker: Installed and running.

2. Launch the MCP Server (The "Warm" Server)

Build and run the tool server in the background. Note that we map port 8001 on the host to avoid conflicts with the agent gateway.
```Bash
cd mcpserver
docker build -t restcountries-mcp .
docker run -d -p 8001:8000 --name mcp-warm-server restcountries-mcp
```

3. Initialize the Agent Gateway

Create a virtual environment and install the specialized LangChain dependencies.
```Bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Deploy Open WebUI

Run the installer script:
```Bash
chmod +x install-ui.sh
./install-ui.sh
```

## 🏃 Execution

Start the Agent Gateway:
```Bash
python agent/main.py
```

The gateway will initialize the MCP connection and start listening on http://localhost:8000.

Connect Open WebUI:

- Open Settings > Connections > OpenAI API.
- API URL: http://host.docker.internal:8000/v1
- API Key: none
- Select the model qwen2.5-mcp-agent in the chat interface.

## 🧪 Testing Tools
Local Unit Test (No Docker)

To test tool logic locally via stdio:

1. Ensure mcp.run() is called without arguments in mcp_server.py.

2. Run:
```Bash
python mcpserver/test_with_fastmcp_client.py
```

**Connection Verification**

Ensure the Dockerized server is accessible:
```Bash
curl http://localhost:8001/sse
```

Expected: A stream starting with event: endpoint.

## 🛠️ Troubleshooting

- TaskGroup Errors: This usually indicates the Agent cannot reach the Docker container. Check if docker ps shows mcp-warm-server running on port 8001.
- Empty Responses: Ensure your system prompt doesn't conflict with tool-calling logic. Qwen 2.5 performs best when told explicitly to "Think in English."
- Open WebUI Connection: If the UI cannot find the agent, ensure the Docker bridge is enabled or use your local IP address instead of localhost.