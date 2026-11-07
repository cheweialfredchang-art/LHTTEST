FROM node:22-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
RUN test -s /app/index.html && test -s /app/school-ui-config.json && test -s /app/school-ui.js && test -s /app/server.js && test -s /app/hello_tool.py && test -s /app/regulation_search.py && test -s /app/additional_regulations.json
ENV NODE_ENV=production PYTHON_BIN=python3 OPENAI_MODEL=gpt-4.1-mini MAX_AGENT_STEPS=4
CMD ["node", "server.js"]
