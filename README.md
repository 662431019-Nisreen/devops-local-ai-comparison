# Local AI Model Comparison with Docker, Ollama, and CrewAI

A DevOps course project that deploys a local language-model service in Docker, runs two lightweight models independently, and evaluates their responses through Python programs and the Continue extension in Visual Studio Code.

**The current implementation uses one selected model per request. Qwen and Llama do not review, rewrite, or receive each other's answers.**

## Verified current evidence

The current repository state was validated with a live smoke test.

```bash
source .venv/bin/activate
docker compose up -d
python scripts/check_stack.py
```

Observed live results:

```text
qwen qwen2.5-coder:1.5b 32.46
llama llama3.2:1b 33.3
```

This confirms that the Docker stack started successfully and the agent service responded for both models. The recorded evidence file is:

- `evidence/container-agent-test.json`

The evidence captures the live `/health` check and two independent single-model requests, each with `engine: crewai`, `agent_count: 1`, and `task_count: 1`.

## Containerized assessment deployment

The project includes a containerized CrewAI entry point in addition to the original host Python programs. This is the route for demonstrating external access to the **Docker agent** rather than only to Ollama.

```bash
docker compose build agent
docker compose up -d
# Browser: http://127.0.0.1:8080
python scripts/check_stack.py
```

The original standalone `ollama` container may need migration before Compose can create its service. Preserve the named `ollama` volume. The migration and container test status are documented separately; do not assume a new deployment passed because configuration files exist.

- [Architecture](docs/ARCHITECTURE.md)
- [Rubric checklist and interpretation limits](docs/RUBRIC.md)
- [Demonstration and offline procedure](docs/DEMO.md)
- [Continue configuration for the containerized agents](config/continue-agent.example.yaml)

For the Docker agent route, each request still selects **one model only**, with one CrewAI agent and task. The web interface and `/chat` API do not use the host chat program's calculator or clock shortcuts. The active Continue configuration targets the Docker Agent route at `http://127.0.0.1:8080/v1`; direct-to-Ollama usage remains a separate diagnostic option for comparison.

An optional `compose.offline.yaml` makes the runtime network internal after images and models are installed. A complete host-disconnected demonstration still requires the student's recorded test.

## 1. Project Objectives

- Run a local AI inference service using Docker and Ollama.
- Select models that can be tested on an Apple M1 laptop with 8 GB of memory.
- Compare two models using the same prompts and consistent test conditions.
- Implement task-specific Python programs for chat, translation, PDF questions, planning, code review, and HTML generation.
- Connect local models to VS Code through Continue.
- Prepare a disconnected demonstration after dependencies and models have been downloaded.
- Document unsuccessful outputs and implementation limitations as well as successful results.

## 2. Development Environment

| Component | Project environment |
|---|---|
| Computer | MacBook Air, Apple M1, 2020 |
| Memory | 8 GB unified memory |
| Operating system | macOS |
| Editor | Visual Studio Code |
| Container platform | Docker Desktop |
| Local inference service | Ollama, running in a Docker container |
| Python environment | Python 3.12 in a project-specific `.venv` |
| Agent framework | CrewAI with LiteLLM support |
| PDF text extraction | pypdf |
| Editor extension | Continue |

The models were chosen as small candidates for this machine, rather than as a claim that they are the best models available. The project has run on this hardware, but response quality and speed vary by task. Free disk space is an important operational constraint.

## 3. Models

| CLI selection | Ollama model tag | Approximate downloaded size |
|---|---|---:|
| `--model qwen` | `qwen2.5-coder:1.5b` | 986 MB |
| `--model llama` | `llama3.2:1b` | 1.3 GB |

Downloaded size is not the same as runtime memory usage. Docker, macOS, Python, model loading, and context processing also consume resources.

The standard Ollama container used in this project runs inference on the CPU on this Mac. This project does not claim Apple Metal GPU acceleration inside that container.

## 4. System Architecture

### Python task programs

```text
User input in the VS Code terminal
                 |
                 v
Task-specific Python program
                 |
                 v
CrewAI: one agent + one task + one selected model
                 |
                 v
Ollama HTTP service at 127.0.0.1:11434
                 |
                 v
Qwen OR Llama, independently
                 |
                 v
Terminal response / saved output
```

In the original host workflow, Ollama runs inside Docker and Python/CrewAI run on macOS. In the current assessment deployment, the agent service also runs CrewAI and Python inside Docker, connected to the Ollama service. Both routes are available.

### Continue integration

```text
Continue Chat in VS Code
          |
          v
Docker Agent endpoint at http://127.0.0.1:8080/v1
          |
          v
CrewAI agent in Docker
          |
          v
Ollama service
          |
          v
Qwen OR Llama
```

The active Continue configuration targets the containerized Docker Agent route. It does not use the direct host-to-Ollama flow as the default route. The direct-to-Ollama interface remains available as a diagnostic option for comparison.

Chat and translation also provide an explicit `--engine direct` option for diagnostic comparisons with Ollama, bypassing CrewAI. Their default engine is `crewai`.

## 5. Project Structure

```text
devops-final/
├── compose.yaml            # Ollama service, local port, and persistent model volume
├── compose.offline.yaml    # Optional offline network override for disconnected demo
├── Dockerfile              # Docker image for the local agent service
├── app.py                  # Generate HTML using one selected model
├── agent_server.py         # HTTP web and API layer for Docker agent requests
├── chat_input.py           # Interactive chat and labeled local utilities
├── crewai_helper.py        # Shared single-model CrewAI execution and PDF helper
├── translate_text.py       # Translation with CrewAI or direct Ollama
├── read_pdf.py             # Questions and summaries from selected PDF pages
├── requirements.txt        # Pinned core CrewAI dependency
├── requirements-docker.txt # Docker image dependency file
├── README.md               # Project overview and usage notes
├── scripts/
│   └── check_stack.py     # Live API and agent validation script
├── config/
│   └── continue-agent.example.yaml  # Continue config for Docker Agent route
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO.md
│   ├── RUBRIC.md
│   └── FINAL_CHECKLIST.md
├── evidence/
│   └── container-agent-test.json  # Verified system evidence from live tests
├── archive/                # Historical backups and older experimental outputs
├── .gitignore              # Ignore generated files and local artifacts
├── .venv/                  # Local Python environment; not source code
└── .crewai-storage/       # Runtime storage used by CrewAI (generated)
```

The repository has been cleaned to keep the active implementation visible while moving historical experiments to `archive/`. Some output directories are created only after the corresponding program is run. Preserve existing results before repeating tests that write the same output filenames.

## 6. Installation

Internet access is needed for initial installation and model downloads. Docker Desktop, VS Code, Continue, and `uv` must already be installed for the commands below.

### 6.1 Create the Python environment

From the project folder:

```bash
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install pypdf
```

The current `requirements.txt` pins the core dependency to `crewai[litellm]==1.15.28`; pypdf must be installed separately using the command above. Python 3.12 is used for compatibility with this project environment.

For the existing installation, activate `.venv` instead of recreating it.

### 6.2 Start Ollama with Docker Compose

Open Docker Desktop and wait for its engine to become ready. The included `compose.yaml` defines only Ollama; Python and CrewAI continue to run in `.venv` on macOS.

The service binds port 11434 to loopback, persists models in the named volume `ollama`, and limits Ollama to one loaded model and one parallel inference request. Selecting either model does not cause it to receive the other model's response.

On a fresh setup, run from the project folder:

```bash
docker compose config --quiet
docker compose up -d
docker compose ps
```

The image uses the `latest` tag; it is not pinned to an immutable digest. Model downloads and the initial image download require internet access.

#### Existing setup created with docker run

This project originally created a standalone container named `ollama`. It cannot coexist with the Compose service using the same container name and port. To switch the existing installation to Compose, first finish any active inference request, then run this one-time migration:

```bash
docker stop ollama
docker rm ollama
docker compose up -d
```

These commands replace the container, not the named volume. The inspected existing setup stores its models in volume `ollama`, and the Compose file explicitly uses that same name. Do not remove the volume or run `docker compose down -v` if you need to retain the downloaded models.

Migration is optional until you are ready to switch. If you have not migrated, continue starting the original container with `docker start ollama` instead of running Compose against it.

#### Models and verification

On a fresh installation, download the models once:

```bash
docker compose exec ollama ollama pull qwen2.5-coder:1.5b
docker compose exec ollama ollama pull llama3.2:1b
```

For the existing installation, verify the models before downloading again:

```bash
docker exec ollama ollama list
```

After migration, routine Compose commands are:

```bash
docker compose up -d
docker compose ps
docker compose logs --tail 50 ollama
docker compose stop
```

`docker compose stop` stops the service while preserving its container and model volume.

## 7. Running the Programs

Activate the environment and start Ollama before running an AI task:

```bash
cd ~/Documents/devops-final
source .venv/bin/activate
docker start ollama
```

Use the actual project path if it is stored elsewhere. Commands below are examples to run individually, not a batch to launch simultaneously. If `--model` is omitted, the terminal programs prompt for a model selection.

### 7.1 General chat

```bash
python chat_input.py --model qwen
```

Enter a question at `You:` and press Enter. Type `/bye` to exit. To test the other model in a separate session:

```bash
python chat_input.py --model llama
```

The current chat program keeps the latest six messages in the running session. Use `/clear` or restart the program before an independent comparison.

**Local utility distinction:** arithmetic expressions and current-time questions can be handled by the program's calculator and Bangkok clock. These outputs are labeled in the terminal. They are not model-generated answers and must not count as evidence of a model's arithmetic or real-time awareness.

To diagnose model behavior without CrewAI:

```bash
python chat_input.py --model qwen --engine direct
```

### 7.2 Translation

```bash
python translate_text.py --model qwen
```

Enter source text and submit it with `/end`:

```text
Hello, how are you?
/end
```

Use `/bye` to exit. English input defaults to Thai output; input containing Thai characters defaults to English. Set the target explicitly when needed:

```bash
python translate_text.py --model llama --to th
python translate_text.py --model qwen --engine direct --to en
```

Successful requests append the source, result, selected model, engine, target language, and elapsed time to `translation-results/translations.jsonl`. Translation accuracy is not guaranteed.

### 7.3 PDF questions and summaries

```bash
python read_pdf.py ~/Downloads/Project-Dev-ops.pdf --model qwen
```

Specify the page range and question:

```bash
python read_pdf.py ~/Downloads/Project-Dev-ops.pdf \
  --model llama --start 4 --pages 3 \
  --question "Summarize the requirements stated in these pages."
```

The program extracts selectable text from one to three pages per request. Extracted source text is limited to 6,000 characters, with the page range and truncation status included in the output. It does not perform OCR or read text embedded only in screenshots.

Results are written into `pdf-results/qwen/` or `pdf-results/llama/`. In the generated filename, the final number represents the requested page count, not the ending page.

### 7.4 HTML generation

```bash
python app.py --model qwen
```

Enter a web-page description when prompted. Repeat with `--model llama` and exactly the same description for an independent comparison.

Outputs are written to:

```text
result/qwen/html-response.txt
result/qwen/index.html
result/llama/html-response.txt
result/llama/index.html
```

The raw response is saved first. The program requires a complete HTML document before writing `index.html`; it does not verify every function or automatically repair the generated code. A previous `index.html` can remain from an earlier run if a new response is incomplete. Check the current response and timestamps before evaluating results.

Open generated pages on macOS:

```bash
open result/qwen/index.html
open result/llama/index.html
```

### 7.5 Planning and code review

```bash
python plan_tasks.py --model qwen
python review_python.py --model llama
```

These programs accept multiple lines. Type `/end` on a separate line to submit and `/bye` to exit. Code review treats submitted code as text and does not execute it. Planning requests five numbered steps, but the model may fail to follow that instruction.

## 8. Continue Configuration

Install the Continue extension in VS Code. Merge the following model entries into the active local configuration, normally `~/.continue/config.yaml` on macOS:

```yaml
name: Independent Local Models
version: 1.0.0
schema: v1

models:
  - name: Qwen 1.5B - Independent
    provider: ollama
    model: qwen2.5-coder:1.5b
    apiBase: http://127.0.0.1:11434
    roles:
      - chat
    defaultCompletionOptions:
      contextLength: 4096
      maxTokens: 3000
      temperature: 0

  - name: Llama 1B - Independent
    provider: ollama
    model: llama3.2:1b
    apiBase: http://127.0.0.1:11434
    roles:
      - chat
    defaultCompletionOptions:
      contextLength: 4096
      maxTokens: 3000
      temperature: 0
```

Reload the VS Code window after changing the configuration. In Continue, select **Chat**, choose one model, and submit the test prompt. Open a new chat before selecting the other model so that it does not receive the first model's response as context.

## 9. Comparison Procedure

1. Select a task and write its prompt before running either model.
2. Use exactly the same prompt and the same interface for both models.
3. Match output limits, temperature, and context settings where the interface allows it.
4. Run one model at a time and keep each session independent.
5. Save the original answers, code, screenshots, and timing method.
6. Test behavior against a checklist defined before inspecting the answers.
7. Record failures as failures; do not silently replace a model's answer with a corrected answer.
8. If code is assembled, reformatted, or repaired manually, keep the original and label the modified copy.
9. Repeat with a new round label after any prompt or configuration change.

Do not mix CrewAI results, direct-Ollama results, and Continue results into one ranking without identifying the interface. They can use different prompt wrappers and generation settings. Model tags also differ in parameter count and quantization, so this is a practical comparison of the installed configurations, not an equal-size model benchmark.

### Suggested evaluation criteria

| Area | What to check |
|---|---|
| Correctness | Does the answer solve the stated problem? |
| Instruction following | Does it use the requested language, format, and file structure? |
| Completeness | Are all required features or facts present? |
| Usability | Does the generated page open, and do its controls work? |
| Translation | Are meaning, pronouns, tense, and questions preserved? |
| Speed | What was the elapsed time, and did timing include model loading? |
| Offline operation | Can a new request complete with internet connectivity disabled? |

A sample Student Task Planner checklist covers adding tasks, rejecting blank titles, completing and deleting tasks, filtering, counts, persistence after refresh, safe text rendering, and responsive styling. A calculator can provide a smaller functional test with known expected answers.

## 10. Observations and Limitations

Development tests produced both successful and unsuccessful outputs:

- Both models generated HTML that could be displayed in a browser, but generated applications did not consistently meet all functional requirements.
- Initial Student Task Planner attempts were incomplete under the earlier 800-token Continue limit. The current configuration raises this to 3,000 for both models. The earlier attempts should remain labeled with their original settings.
- Some Llama output used separate files and external fonts despite the request for one offline HTML file. Saved code also contained runtime and logic errors.
- Translation tests included correct greetings, incorrect pronouns, incomplete translations, repeated input, and leaked CrewAI formatting instructions. Prompt changes did not eliminate all failures.
- Model responses can change after prompt and program revisions. Conclusions must identify the tested version and conditions.
- Review by an AI model does not establish factual correctness; this project currently evaluates models independently.
- No controlled multi-run statistical benchmark or peak-memory measurement is claimed.

These observations are evidence of the tested configurations, not a claim that either model always succeeds or always fails at a task. No overall winner is asserted without reference to a specific task and recorded evaluation.

## 11. Offline Demonstration

The current endpoints are local. However, local configuration alone is not proof of fully disconnected operation. End-to-end offline operation must be demonstrated separately.

After downloading all dependencies and models:

1. Start Docker Desktop and the Ollama container.
2. Activate `.venv` and open the required program or Continue configuration.
3. Disable Wi-Fi and any other internet connection.
4. Submit a new prompt, rather than displaying a previously generated answer.
5. Save the new result and evidence of disconnected operation.
6. Repeat the same task with the other model and independent context.
7. Record any dependency, extension, or runtime behavior that still requires connectivity.

**Status:** this README does not claim that a complete disconnected demonstration has already passed. Include that claim only after recording the test.

## 12. Troubleshooting

| Problem | Action |
|---|---|
| Cannot connect to Docker daemon | Open Docker Desktop and wait for the engine to start. |
| Ollama is unavailable | Run `docker start ollama` and check `docker ps`. |
| Model not found | Check `docker exec ollama ollama list`; pull the exact model tag if absent. |
| Disk-space guard stops a request | Check `df -h .` and free space before retrying. |
| HTML ends in the middle of a tag or function | Record the failure, check the output limit, and repeat both models with matched settings. |
| Continue Apply cannot resolve a file | Save the returned code manually to a clearly named HTML file. |
| Translation repeats the source or prints instructions | Record the result and compare the same input with `--engine direct`; do not treat a completed request as proof of correctness. |
| An archived API reports port 8000 already in use | The current direct-Ollama Continue setup does not require that API. |

The Python programs enforce a **3 GiB free-space guard**. This is a project-specific precaution, not an official universal minimum for Ollama. Disk-space readings displayed by `df` can be rounded. Docker previously stopped unexpectedly during a period of low disk space; the exact cause was not established.

## 13. Submission Evidence

Prepare the following for presentation:

- Hardware specifications and explanation of the model choices.
- Docker container status and installed model list.
- Source programs and the Continue configuration.
- Identical prompts and original responses from both models.
- Functional test results, failures, and screenshots.
- Separate labels for original, assembled, and repaired generated code.
- Offline demonstration evidence once completed.
- A conclusion explaining which model is more suitable for the demonstrated task and why.

The implementation was developed with AI assistance. Generated code and model responses require manual inspection and testing; the project documents observed limitations rather than assuming output quality.
