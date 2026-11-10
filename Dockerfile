FROM node:22-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
RUN python3 -m py_compile hello_tool.py regulation_search.py school_crawl_search.py && python3 -c "import school_crawl_search; print('MCP import OK')"
RUN node --check render-audit.js && node --check llm-client-openai.js && node --check server.js && node --check taiwan-time.js && node --check agent-v9.js && node --check trace-recorder.js
RUN test -s /app/index.html && test -s /app/school-ui-config.json && test -s /app/school-ui.js && test -s /app/server.js && test -s /app/hello_tool.py && test -s /app/regulation_search.py && test -s /app/additional_regulations.json
ENV NODE_ENV=production PYTHON_BIN=python3 OPENAI_MODEL=gpt-4.1-mini MAX_AGENT_STEPS=4
CMD ["node", "server.js"]
