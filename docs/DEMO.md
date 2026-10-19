# Instructor demonstration checklist

## Prepare while online

1. Build the agent image: `docker compose build agent`.
2. Start both services: `docker compose up -d`.
3. Verify `docker compose ps` and `docker exec ollama ollama list`.
4. Confirm both model tags are installed. Do not pull images/models during an offline test.
5. Open `http://127.0.0.1:8080` or use `config/continue-agent.example.yaml` in Continue Chat.

A previous standalone container named `ollama` must first be replaced without deleting the `ollama` volume. The migration is documented in README; do not run `down -v`.

## Compare independent models

Use the exact same prompt twice. Use a new Continue chat for each model, or separate `/chat` requests. The web/API route has no conversation memory. Save complete responses, selected model, elapsed time, and test conditions. Do not count a refusal or a malformed answer as success just because the request returned HTTP 200.

```bash
curl http://127.0.0.1:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen","prompt":"Explain the difference between a Docker image and a container in two sentences."}'
```

Repeat with `"model":"llama"`. No answer is passed from one model to the other. No calculator/clock shortcut is used in this API route.

## Disconnected test

1. Finish active inference requests.
2. Apply the offline network override, using existing images only:

```bash
docker compose -f compose.yaml -f compose.offline.yaml up -d --no-build --pull never
```

3. Disable Wi-Fi and other host internet connections yourself.
4. Submit a NEW prompt containing a fresh identifier, e.g. `Offline demonstration NISREEN-02: write a short HTML heading with this exact identifier.`
5. Test both models independently and capture the request, response, model name, and disconnected status.
6. Restore host connectivity. Return to normal Compose networking if needed:

```bash
docker compose up -d --no-build --pull never
```

Internal Docker networking and a fully disconnected host are different tests. Record which one was actually performed. No host disconnection is claimed until the student captures that evidence.

## Presentation outline (f1-f6)

- Problem: whether small local models can support useful student tasks on an M1 8 GB laptop without a cloud LLM.
- Methods: Docker/Ollama, independent model selection, CrewAI task execution, identical prompts, recorded outcomes.
- Design: explain the architecture and persistent volumes.
- Analysis: compare correctness, instruction following, functionality, and measured time. Record failures.
- Conclusions: select a model for a specific task, with limitations; do not assert an overall winner from one trial.
- Demonstration: show Compose, the two model tags, a fresh offline agent request, and one external interface.
