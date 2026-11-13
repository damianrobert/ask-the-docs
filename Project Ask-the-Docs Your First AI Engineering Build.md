# Project Ask-the-Docs: Your First AI Engineering Build

Nov 13, 2026 · @Rădulescu Roberto-Damian

## Overview

You will build **Ask-the-Docs**: a deployed web service that answers questions about the Docker and Linux documentation, and cites the exact pages it used. Under the hood it is a RAG (Retrieval-Augmented Generation) system, which is the most common thing AI engineers ship in industry today.

**The analogy.** A plain LLM is a student taking a closed-book exam: smart, but it guesses when it doesn't remember, and it confidently makes things up. RAG turns it into an open-book exam. Before answering, a librarian (the retriever) runs to the shelves, pulls the 5 most relevant index cards, and hands them over. The student then writes an answer *from those cards* and says which card each fact came from.

**Why this is a good first project:**

- It's small enough to finish in about 6–8 weeks of part-time work, but it touches every stage of a real AI product: data, models, API, evaluation, containers, CI/CD and a live deployment.
- It uses what you already know. Python for the app, Docker for packaging, Linux and networking for the server, ports, firewall and HTTPS.
- It's the shape of real work. A typical ticket at an AI team reads: *"Build an internal assistant that answers questions over our docs, prove it's accurate, and ship it."* That is exactly this.
- The finished product is portfolio-ready: a public URL, a GitHub repo with green CI, and an evaluation report with numbers.

**What "done" looks like.** Someone opens `https://ask.yourdomain.com`, types *"How do I make a Docker volume persist between container restarts?"*, and gets a correct answer in under 10 seconds with links to the source pages. If they ask something outside the docs, it says "I don't know" instead of inventing an answer.

## Skills you'll build

Each row is a skill that shows up in AI engineer job descriptions, and where in this project you practise it.

| Skill | What it means in practice | Where you practise it |
| --- | --- | --- |
| Working with LLM APIs | Prompts, system messages, temperature, tokens, streaming, cost | Milestone 1 |
| Embeddings | Turning text into vectors so "similar meaning" becomes "close in space" | Milestone 2 |
| Chunking and ingestion | Cleaning and splitting documents so retrieval works well | Milestone 2 |
| Vector databases | Storing vectors and running similarity search (Qdrant) | Milestone 2–3 |
| RAG pipeline design | Retrieve, build the prompt, generate, cite | Milestone 3 |
| Prompt engineering | Grounding the model, forcing citations, refusing when unsure | Milestone 3 |
| API engineering | FastAPI, Pydantic schemas, error handling, timeouts | Milestone 4 |
| Evaluation (evals) | Measuring quality with a test set instead of "it looks fine" | Milestone 5 |
| Containerisation | Dockerfiles, multi-service Compose, healthchecks | Milestone 6 |
| CI/CD | Lint, test and build automatically on every push | Milestone 7 |
| Deployment and ops | VPS, reverse proxy, HTTPS, firewall, logs, secrets | Milestone 8 |

**Analogy for embeddings**, since everything rests on them: an embedding is GPS coordinates for meaning. "How do I stop a container?" and "command to halt a running container" share few words, but their coordinates land on the same street. Search then becomes "find the nearest neighbours", not "find matching words".

## Architecture

The system has two flows that share one vector database: ingestion fills it once, and answering reads from it on every question.

&#91;embedded content: Ask-the-Docs architecture · ingestion and answering flows\]

Only Caddy is reachable from the internet; Qdrant and the LLM stay on Docker's internal network.

**Analogy, end to end:** ingestion is a librarian cutting every manual into index cards and filing each card in a catalogue sorted by *meaning*, not alphabet. Answering is a visitor at the front desk (Caddy) asking a question. The librarian (retriever) pulls the 5 closest cards, staples them to the question (prompt builder), and hands the bundle to the expert (LLM), who must answer only from those cards and say which ones it used.

## Tech stack

Every choice favours tools that are free, run on a laptop, and are common in real teams. Swap any of them later; the architecture stays the same.

| Layer | Choice | Why this one |
| --- | --- | --- |
| Language | Python 3.12 | The default language of AI engineering |
| Package manager | `uv` | Fast, modern, one lockfile; replaces pip + venv |
| Corpus | Docker docs (Markdown, from the public `docker/docs` GitHub repo) | Real, messy, technical text you already understand |
| Embedding model | `BAAI/bge-small-en-v1.5` via `sentence-transformers` | Small (\~130 MB), runs on CPU, good quality |
| Vector database | Qdrant (Docker image) | Easy to run, nice web dashboard, production-grade |
| LLM | Ollama with a small local model (e.g. `llama3.2:3b` or `qwen2.5:3b`) **or** a hosted API (Anthropic, OpenAI) | Start local and free; keep it behind one interface so swapping is a config change |
| API | FastAPI + Pydantic | Typed, fast, automatic `/docs` page |
| UI | Streamlit | A usable chat page in \~50 lines of Python |
| Tests | `pytest` + `httpx` | Standard Python testing |
| Lint/format | `ruff` | One tool, very fast |
| Containers | Docker + Docker Compose | Run all services with one command |
| CI/CD | GitHub Actions + GitHub Container Registry | Free for public repos |
| Hosting | A small Linux VPS (Hetzner, DigitalOcean, or Oracle free tier) | Real server, real networking; \~4–8 GB RAM if you run Ollama there |
| Reverse proxy | Caddy | Automatic HTTPS with Let's Encrypt in 3 lines of config |

**One rule to follow from day one:** never hard-code model names, URLs or API keys. Put them in a `.env` file read by a `Settings` class (`pydantic-settings`). Think of it like a car's dashboard: you change the radio station with a knob, not by rewiring the engine.

Check current versions and model names when you start; this space moves fast.

## Repository layout

Aim for this structure by the end. Don't create it all on day one; let it grow milestone by milestone.

```
ask-the-docs/
├── src/askdocs/
│   ├── config.py          # Settings loaded from .env
│   ├── llm.py             # One interface, two backends (Ollama / API)
│   ├── ingest/
│   │   ├── loader.py      # Read + clean Markdown files
│   │   ├── chunker.py     # Split into overlapping chunks
│   │   └── indexer.py     # Embed + upsert into Qdrant
│   ├── rag/
│   │   ├── retriever.py   # Query Qdrant, return top-k chunks
│   │   ├── prompts.py     # System prompt + templates
│   │   └── pipeline.py    # retrieve -> prompt -> generate -> cite
│   └── api/
│       ├── main.py        # FastAPI app: /ask, /health
│       └── schemas.py     # Pydantic request/response models
├── ui/app.py              # Streamlit chat page
├── evals/
│   ├── golden_set.jsonl   # 30+ questions with expected sources
│   ├── run_evals.py       # Scores retrieval + answers
│   └── results/           # One JSON report per run
├── tests/                 # unit/ and integration/
├── scripts/ingest.py      # CLI: build the index
├── docker/
│   ├── api.Dockerfile
│   └── ui.Dockerfile
├── deploy/Caddyfile
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example           # Committed. The real .env is NOT.
├── pyproject.toml
└── README.md
```

Keeping ingestion, RAG logic and the API in separate folders is the point. Like a restaurant: the prep kitchen (ingest) works before opening, the line cooks (rag) cook to order, and the waiters (api) only talk to customers. Each can change without the others noticing.

## Milestones

Nine milestones, each ending in something that works. Commit at the end of each one with a clear message and tick its boxes here. Times assume \~8–10 hours a week.

### M0 — Set up the workshop (2–3 days)

- [x] Create a GitHub repo `ask-the-docs`, clone it, add a Python `.gitignore`
- [x] `uv init`, add `ruff` and `pytest`, write a one-line passing test
- [x] Create `config.py` with a `Settings` class and a `.env.example`
- [ ] Write a first README: one paragraph on what the project will do

**Done when:** `uv run pytest` and `uv run ruff check .` both pass.

### M1 — Talk to an LLM (3–4 days)

- [ ] Install Ollama, pull a small model, call it from Python
- [ ] Write `llm.py` with one function, `generate(system, user) -> str`, and two backends (Ollama and a hosted API) chosen by config
- [ ] Experiment: change temperature from 0 to 1 and ask the same question 5 times. Write down what changes
- [ ] Ask it something about Docker it can't know (a recent flag, a niche option) and record a hallucination. Keep it; you'll fix it in M3

**Done when:** `uv run python -m askdocs.llm "What is a Docker volume?"` prints an answer from either backend.

### M2 — Ingest the docs (1 week)

- [ ] Clone the Docker docs repo into `data/raw/` (git-ignored). Start with one section only, e.g. `content/manuals/engine/`
- [ ] `loader.py`: read Markdown, strip front-matter and HTML/shortcodes, keep the title and source path
- [ ] `chunker.py`: split by headings, then into \~500-token chunks with \~50 tokens of overlap
- [ ] `indexer.py`: embed chunks in batches, upsert into Qdrant with metadata (`source`, `title`, `heading`)
- [ ] Run Qdrant in Docker (`docker run -p 6333:6333 qdrant/qdrant`) and look at your points in its dashboard
- [ ] Make ingestion idempotent: running it twice must not create duplicates (use a hash of the chunk as its ID)

**Analogy:** chunking is cutting a book into index cards. Cards too big and the librarian hands over whole chapters; too small and each card loses its context. Overlap is writing the last line of one card at the top of the next.

**Done when:** `uv run python scripts/ingest.py` builds the index, and a test query returns sensible chunks.

### M3 — Retrieve and answer (1 week)

- [ ] `retriever.py`: embed the question, return the top-k chunks (start with k = 5) with scores
- [ ] `prompts.py`: a system prompt that says *answer only from the context; cite sources as \[1\], \[2\]; if the answer isn't there, say you don't know*
- [ ] `pipeline.py`: retrieve → build prompt → generate → return `{answer, sources}`
- [ ] Add a score threshold: if no chunk is relevant enough, refuse without calling the LLM
- [ ] Re-ask the M1 hallucination question. Did it improve?

**Done when:** a CLI command answers 5 hand-picked questions correctly with citations, and refuses "What's the capital of France?"

### M4 — Wrap it in an API and a UI (4–5 days)

- [ ] `POST /ask` with Pydantic models: `question` in; `answer`, `sources`, `latency_ms` out
- [ ] `GET /health` that checks Qdrant and the LLM are reachable
- [ ] Validation (empty or 2,000+ character questions get a 422) and timeouts on LLM calls
- [ ] Structured JSON logging: question, number of chunks, latency, errors
- [ ] Streamlit page that calls the API and shows answers with clickable sources

**Done when:** `uvicorn` is running, `/docs` shows your endpoints, and the Streamlit page works end to end.

### M5 — Measure quality with evals (1 week)

This is the milestone that separates an AI engineer from someone who wrote a demo. Details are in the next section.

- [ ] Write a golden set of 30+ questions, each with the source file(s) that contain the answer. Include 5 questions the docs *can't* answer
- [ ] `run_evals.py`: compute retrieval hit rate, answer quality and refusal accuracy; save a JSON report
- [ ] Run one experiment: change chunk size **or** k **or** the embedding model, and compare reports
- [ ] Write down the winning settings and why in `evals/README.md`

**Done when:** you can say "retrieval hit@5 is X% and answer correctness is Y%" with a report to back it.

### M6 — Containerise (3–4 days)

- [ ] `api.Dockerfile`: slim Python base, non-root user, `uv sync --frozen`, healthcheck
- [ ] `ui.Dockerfile` for Streamlit
- [ ] `docker-compose.yml` with `qdrant`, `ollama` (or none, if using an API), `api`, `ui`; named volumes for Qdrant and Ollama models; services talk by service name on an internal network
- [ ] Only the UI and API ports are published; Qdrant stays internal

**Done when:** on a clean machine, `docker compose up -d` then the ingest command gives a working app.

### M7 — Automate with CI/CD (2–3 days)

- [ ] GitHub Actions on every push: `ruff`, unit tests, build images
- [ ] On `main`: push images to GitHub Container Registry tagged with the commit SHA
- [ ] A small "eval smoke test" job: 5 golden questions must pass, or the build fails
- [ ] Add the CI badge to the README

**Done when:** a pull request shows green checks, and breaking a test turns them red.

### M8 — Deploy (1 week)

- [ ] Rent a VPS, create a non-root sudo user, SSH keys only, `ufw` allowing 22, 80, 443
- [ ] Point a domain or subdomain (A record) at the server
- [ ] Install Docker, copy `docker-compose.yml` and `.env`, pull images from GHCR
- [ ] Put Caddy in front for HTTPS; add basic rate limiting or a simple access password
- [ ] Run ingestion on the server; check logs with `docker compose logs -f`
- [ ] Optional: a GitHub Actions deploy job that SSHes in and runs `docker compose pull && docker compose up -d`

**Done when:** a friend on their phone can use `https://ask.yourdomain.com`.

### M9 — Polish and present (2–3 days)

- [ ] README: what it is, architecture diagram, how to run locally, eval results, live link
- [ ] A 30-second GIF or video demo
- [ ] A short "Lessons learned" section: what surprised you, what you'd do next

## Testing and evaluation

AI systems need two kinds of checking. **Tests** ask "does the code work?" and give a yes/no. **Evals** ask "are the answers good?" and give a score. You need both.

**Analogy:** tests are the car's safety inspection: brakes work, lights turn on, pass or fail. Evals are the driving exam: an examiner rides along on 30 routes and gives a score. A car can pass inspection and still drive badly.

### Tests (pytest)

| Type | What to test | Example |
| --- | --- | --- |
| Unit | Pure functions, no network | Chunker never exceeds max size; overlap is correct; front-matter is stripped |
| Unit with fakes | Pipeline logic with a fake LLM and fake retriever | With zero relevant chunks, the pipeline refuses and never calls the LLM |
| API | FastAPI `TestClient` | Empty question returns 422; `/health` returns 200; response matches the schema |
| Integration | Real Qdrant in Docker (marked `@pytest.mark.integration`) | Ingest 3 small files, then a query returns the right one |

Keep unit tests fast (under 10 seconds total) so you run them constantly. Integration tests can run in CI with Qdrant as a service container.

### Evals

Your golden set is a JSONL file, one case per line:

```json
{"id": "vol-01", "question": "How do I persist data after a container is removed?", "expected_sources": ["storage/volumes.md"], "must_mention": ["volume"], "answerable": true}
```

Measure three numbers per run:

1. **Retrieval hit@k**: in what share of questions does an expected source appear in the top k chunks? If this is low, no prompt will save you. Fix chunking or embeddings first.
2. **Answer correctness**: does the answer contain the key facts and cite a correct source? Start with simple checks (`must_mention` keywords, citation present). Then add an *LLM-as-judge*: a second model call that grades the answer 1–5 against the retrieved context. Spot-check 10 of its grades by hand; judges make mistakes too.
3. **Refusal accuracy**: on the unanswerable questions, did it say "I don't know"?

Also log **p50/p95 latency** and, if using a paid API, **cost per question**.

Starting targets for a first version: hit@5 ≥ 80%, correctness ≥ 70%, refusal ≥ 80%, p95 latency < 10 s. Your first numbers will likely be lower. That's normal and it's the point: now you can improve them with evidence.

The golden rule of evals: **change one thing at a time, re-run, compare reports.** Commit every report so you have a history.

## Deployment

The deployed setup is four containers on one VPS, with only Caddy facing the internet. This is where your Linux, networking and Docker knowledge pays off.

**Analogy:** Caddy is the building's front desk. Visitors only ever talk to the front desk on ports 80 and 443. It checks them in (HTTPS) and walks them to the right office (`/` goes to the UI, `/api` goes to the API). Qdrant and Ollama are back offices with no door to the street.

### Pipeline from your laptop to the internet

1. You push to `main`.
2. GitHub Actions lints, tests, runs the eval smoke test, builds images and pushes them to GHCR tagged with the commit SHA.
3. A deploy job (or you, at first, by hand) SSHes to the VPS and runs `docker compose pull && docker compose up -d`.
4. Caddy keeps serving; the API container restarts on the new image; `/health` confirms it's up.

### A minimal Caddyfile

```
ask.yourdomain.com {
    handle_path /api/* {
        reverse_proxy api:8000
    }
    reverse_proxy ui:8501
}
```

### Server checklist

- [ ] SSH: key-only login, root login disabled
- [ ] Firewall: `ufw` allows 22, 80, 443 only
- [ ] Docker publishes no ports except Caddy's (Docker can bypass `ufw` for published ports, so don't publish Qdrant's 6333)
- [ ] `.env` lives only on the server, `chmod 600`, never in git
- [ ] `restart: unless-stopped` on every service
- [ ] Volumes for Qdrant data, Ollama models and Caddy certificates, so a restart loses nothing
- [ ] Log rotation for Docker (`max-size` in the logging options)
- [ ] A free uptime monitor (e.g. UptimeRobot) pinging `/api/health`

### Sizing

With a hosted LLM API, a 2 GB VPS is enough. Running a 3B model in Ollama on CPU needs about 4–8 GB of RAM and answers will take several seconds. Pick the API route if the server is small; it's a config change thanks to `llm.py`.

## Definition of done

The project is finished when every box below is ticked. This is the list a senior engineer would check in your final review.

**Built**

- [ ] Ingestion is one command and idempotent
- [ ] `/ask` returns an answer, sources and latency; `/health` checks dependencies
- [ ] The UI shows answers with clickable source links
- [ ] Out-of-scope questions get a polite "I don't know"
- [ ] No secrets in git; all settings come from `.env`

**Tested**

- [ ] Unit tests for chunker, retriever logic, pipeline and API pass
- [ ] At least one integration test against real Qdrant
- [ ] Golden set of 30+ questions, including 5+ unanswerable ones
- [ ] Committed eval report with hit@5, correctness, refusal accuracy and p95 latency
- [ ] At least one documented experiment that improved a metric

**Deployed**

- [ ] CI runs lint, tests, eval smoke test and image build on every push
- [ ] Images published to GHCR
- [ ] Live on HTTPS at your own domain
- [ ] Only ports 22, 80, 443 open on the server
- [ ] Uptime monitor configured

**Presented**

- [ ] README with architecture diagram, setup steps, eval results and live link
- [ ] Demo GIF or short video
- [ ] "Lessons learned" section

## Pitfalls, stretch goals and glossary

### Common pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Ingesting everything on day one | Slow runs, can't tell what's wrong | Start with one docs folder; grow later |
| Tuning prompts before checking retrieval | Answers stay wrong whatever you write | Look at the retrieved chunks first; measure hit@k |
| Different embedding models at index and query time | Search returns nonsense | Store the model name in config; re-index when it changes |
| No overlap or giant chunks | Answers miss details or mix topics | Try 300–800 tokens with \~10% overlap; let evals decide |
| Judging quality by "looks good to me" | Regressions go unnoticed | Golden set + reports, every change |
| Publishing Qdrant's port in Compose | Database open to the internet | Keep it on the internal network only |
| Committing `.env` | Leaked API key | `.gitignore` it from M0; rotate any key that leaks |

### Stretch goals (after v1 ships)

- **Streaming** answers token by token (Server-Sent Events) so the UI feels instant
- **Hybrid search**: combine keyword (BM25) and vector search; helps with exact flags like `--mount`
- **Re-ranking**: retrieve 20 chunks, re-score with a cross-encoder, keep the best 5
- **Conversation memory**: follow-up questions like "and how do I delete it?"
- **Feedback buttons** (👍/👎) stored in SQLite, turned into new golden-set cases
- **Observability**: Prometheus metrics + a Grafana dashboard, or a tracing tool like Langfuse
- **Your own corpus**: point it at your notes or a project's wiki

### Glossary

| Term | Plain meaning |
| --- | --- |
| LLM | A model that predicts the next token of text; the "student" |
| Token | A piece of a word; models count and charge by tokens |
| Context window | How much text the model can read at once; its desk size |
| Embedding | A list of numbers representing meaning; GPS coordinates for text |
| Vector database | A store that finds the nearest embeddings fast; the library catalogue |
| Chunk | One piece of a document stored and retrieved as a unit; an index card |
| RAG | Retrieve relevant chunks, then generate an answer from them; the open-book exam |
| Top-k | How many chunks you retrieve per question |
| Hallucination | A confident answer that isn't supported by any source |
| Grounding | Forcing answers to come from the provided context |
| Golden set | Your fixed list of test questions with known answers |
| LLM-as-judge | Using a model to grade another model's answers |
| Temperature | Randomness knob: 0 is consistent, 1 is creative |
