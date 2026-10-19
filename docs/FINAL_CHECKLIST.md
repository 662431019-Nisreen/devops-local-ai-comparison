# Final Submission Checklist

This checklist reflects the rubric priorities for this project and keeps the scope focused on what an instructor is most likely to look for.

## 1. Core project must-have

### System works
- Docker is installed and working.
- `docker compose up -d` starts the project without manual code edits.
- Ollama is running and reachable.
- At least one local model is downloaded and usable.
- The selected model runs locally and returns a response.
- `agent_server.py` runs on `http://127.0.0.1:8080`.
- `/health` returns status.
- `/chat` returns a valid result.
- `qwen` and `llama` can be selected independently.
- One model is used per request; no shared cross-model answer flow.

### Required files
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/RUBRIC.md`
- `compose.yaml`
- `compose.offline.yaml`
- `Dockerfile`
- `agent_server.py`
- `crewai_helper.py`
- `chat_input.py`
- `translate_text.py`
- `read_pdf.py`
- `app.py`
- `requirements.txt`
- `config/continue-agent.example.yaml`
- `scripts/check_stack.py`

### Optional but useful
- `docs/DEMO.md`
- `evidence/` with test outputs

## 2. Highest-priority rubric items

### f9: Local agentic operation
- The project demonstrates AI agent execution on the local machine.
- The system works without depending solely on a browser-only mock.
- A live request reaches CrewAI and Ollama successfully.
- Evidence shows the agent path is working.

### f13: Connect from VS Code / terminal / web to Docker Agent
- Continue config points to `http://127.0.0.1:8080/v1`.
- Web UI works through `/` and `/chat`.
- Terminal commands can call the agent successfully.
- Docker route is clearly distinguished from direct Ollama route.

### f14: Model installed locally and in Docker
- Models can be pulled and used in Ollama.
- Docker runtime can access the same model set or a compatible model set.
- The project does not claim unsupported claims such as Apple Metal GPU acceleration if it was not verified.

### f10: Infrastructure as Code
- Docker is used.
- Compose files are present.
- The system can be reproduced using configuration, not only manual terminal steps.
- The project explains how to start services from configuration.

## 3. Documentation quality

### README must include
- Objective of the project
- Why local AI is relevant
- What models are used
- Names of the core files
- Setup steps
- Run commands
- Limitations and constraints
- What is current implementation vs legacy backup

### Architecture doc must include
- Simple diagram of flow
- Host terminal / browser / Continue
- Docker agent
- CrewAI
- Ollama
- Selected model
- Model volume and runtime notes

## 4. Evidence requirements

At minimum, keep one evidence file showing real output from the system.

Recommended:
- `evidence/container-agent-test.json`
- output from `curl http://127.0.0.1:8080/health`
- output from `python scripts/check_stack.py`
- output from `python chat_input.py --model qwen`
- output from `python chat_input.py --model llama`

Evidence should show:
- health response
- model selected
- request completed
- request path was actual agent route
- one model selected per request

## 5. Repository hygiene

### Keep in root
- project source files
- docs
- config
- docker files
- scripts

### Move or archive
- old backups
- legacy results
- prototype HTML files
- unused connectors
- historical experiments

### Ignore / do not commit
- `.venv/`
- `__pycache__/`
- `.crewai-storage/`
- `.DS_Store`
- generated output not needed for final evidence

## 6. Avoid common mistakes

- Do not claim both models are reviewed or rewritten by each other.
- Do not claim host internet was disconnected unless it was actually tested.
- Do not claim the offline demo passed unless there is captured evidence.
- Do not leave legacy backups mixed with the final project root.
- Do not rely only on file existence; show runtime evidence.

## 7. Recommended final sequence

1. Verify Docker is running.
2. Start Ollama and confirm models exist.
3. Run `agent_server.py` and confirm `http://127.0.0.1:8080` is alive.
4. Call `/health` and `/chat` successfully.
5. Test both `qwen` and `llama` using the same prompt.
6. Save evidence output into `evidence/`.
7. Review README and architecture for truthfulness.
8. Remove or archive old experimental files.
9. Make sure `.gitignore` excludes generated outputs.
10. Push final repo state to GitHub.

## 8. Final grading mindset

The instructor is most likely to reward:
- working system
- documented setup
- Docker infrastructure
- agent service route
- multi-model testing
- real evidence
- clear architecture explanation

The project does not need to be huge. It needs to be clear, working, and evidence-backed.
