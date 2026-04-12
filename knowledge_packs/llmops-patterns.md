# LLMOps Patterns

A reference guide for engineers building, deploying, and operating LLM-powered systems in production.

---

## 1. RAG Architecture Patterns

### Naive RAG
The simplest pattern: ingest documents → chunk → embed → store in vector DB → at query time, embed query → retrieve top-k chunks → pass to LLM as context.

**When it works:** Small, well-structured document collections. Homogeneous document types. Forgiving use cases where occasional retrieval misses are acceptable.

**Where it breaks down:** Mixed document types (PDFs, tables, code). Questions that require synthesizing information across many documents. Queries that need recent or real-time information.

### Advanced RAG

Extends naive RAG with improvements at the pre-retrieval, retrieval, and post-retrieval stages:

| Stage | Technique | Problem It Solves |
|---|---|---|
| Pre-retrieval | Query rewriting / HyDE | Poorly phrased queries miss relevant chunks |
| Pre-retrieval | Query expansion | Single query misses related terminology |
| Retrieval | Hybrid search (dense + sparse) | Dense-only misses exact keyword matches |
| Retrieval | Re-ranking (cross-encoder) | Initial top-k contains irrelevant results |
| Post-retrieval | Contextual compression | Retrieved chunks contain too much irrelevant text |
| Post-retrieval | Metadata filtering | Over-retrieval from wrong document subsets |

### Modular RAG

Treats each pipeline component as independently swappable: retriever, re-ranker, generator, memory, and routing are separate modules with defined interfaces. Enables A/B testing of individual components without rebuilding the whole pipeline.

### Agentic RAG

The LLM itself controls the retrieval loop: decides whether to retrieve, what to query, and when it has enough information. Enables multi-hop reasoning but increases latency, cost, and unpredictability.

---

## 2. Chunking Strategies Comparison

| Strategy | How It Works | Best For | Watch Out For |
|---|---|---|---|
| Fixed-size | Split by character count with overlap | Simple, fast baseline | Breaks mid-sentence, mid-concept |
| Recursive | Split by separators (paragraph → sentence → word) | General prose documents | Still size-limited |
| Semantic | Split at topic/meaning boundaries using embedding similarity | Long documents with distinct sections | Slow, chunk sizes vary wildly |
| Document-structure | Use markdown headers, HTML tags, PDF outline | Structured docs (wikis, technical docs) | Requires document format awareness |
| Parent-child | Small chunks for retrieval, large chunks sent to LLM | Precision retrieval + full context generation | More complex index design |

**Rule of thumb:** Start with recursive chunking at 512-1024 tokens with 10-20% overlap. Measure retrieval precision. Only move to more complex strategies when metrics justify it.

---

## 3. Embedding Model Selection

### Key dimensions
- **Dimension size:** Higher dimensions = more expressive, more VRAM/storage cost. Common sizes: 384, 768, 1536, 3072.
- **Max sequence length:** Critical for long documents. Models with 512-token limits lose information in longer chunks.
- **Domain fit:** General models (OpenAI ada, sentence-transformers) vs domain-specific (legal, biomedical).
- **Cost:** API-based (OpenAI, Cohere) vs self-hosted (sentence-transformers, BGE, E5).

### Common embedding models (as of 2025-2026)
| Model | Provider | Dimensions | Max Tokens | Cost |
|---|---|---|---|---|
| text-embedding-3-large | OpenAI | 3072 | 8192 | API (paid) |
| text-embedding-3-small | OpenAI | 1536 | 8192 | API (cheap) |
| embed-v4 | Cohere | 1024 | 512 | API (paid) |
| BGE-M3 | BAAI | 1024 | 8192 | Free (self-host) |
| all-MiniLM-L6-v2 | sentence-transformers | 384 | 256 | Free (self-host) |

**Check MTEB Leaderboard** for current rankings: https://huggingface.co/spaces/mteb/leaderboard

---

## 4. Retrieval Evaluation Metrics

### Retrieval-level metrics
- **Precision@k:** Of the k retrieved chunks, what fraction were actually relevant? Higher = less noise in context.
- **Recall@k:** Of all relevant chunks in the corpus, what fraction were retrieved in the top k? Higher = fewer missed answers.
- **MRR (Mean Reciprocal Rank):** How high did the first relevant chunk rank? Rewards systems that surface the best answer first.
- **nDCG (Normalized Discounted Cumulative Gain):** Accounts for graded relevance — highly relevant chunks at position 1 score better than at position 5.

### RAG generation metrics (RAGAS)
| Metric | What It Measures | Range |
|---|---|---|
| Faithfulness | Does the answer stick to the retrieved context? | 0-1, higher is better |
| Answer Relevance | Does the answer address the question asked? | 0-1, higher is better |
| Context Precision | Are the retrieved chunks actually useful? | 0-1, higher is better |
| Context Recall | Did retrieval capture all information needed? | 0-1, higher is better |

**Typical production alert thresholds:** Faithfulness < 0.7 and Context Precision < 0.6 usually indicate a pipeline problem worth investigating.

---

## 5. LLM Observability Tooling Landscape

| Tool | Primary Use | Self-hostable | Cost |
|---|---|---|---|
| Langfuse | Tracing, prompt management, evals | Yes | Free tier + paid |
| Arize Phoenix | Tracing, hallucination detection | Yes | Free (OSS) |
| LangSmith | LangChain-native tracing, datasets | No | Free tier + paid |
| Helicone | Proxy-based logging, cost tracking | Yes | Free tier + paid |
| Weights & Biases Weave | Experiment tracking + LLM tracing | No | Free tier + paid |

**What to instrument at minimum:**
1. Token usage (input + output) per request
2. Latency per step (retrieval, LLM call, total)
3. Cost per request (calculated from token counts)
4. Error rate and error types
5. For RAG: chunk retrieval scores and which chunks were used

---

## 6. Model Serving Trade-offs

### vLLM vs TGI vs Ollama

| | vLLM | TGI (HuggingFace) | Ollama |
|---|---|---|---|
| Best for | High-throughput production | HuggingFace ecosystem | Local dev and testing |
| OpenAI-compatible API | Yes | Yes | Yes |
| Continuous batching | Yes | Yes | No |
| Quantization support | GPTQ, AWQ, INT4 | GPTQ, bitsandbytes | GGUF |
| Multi-GPU | Yes | Yes | No |
| Operational complexity | Medium | Medium | Low |

### Self-hosted vs managed inference

| Factor | Self-hosted (vLLM/TGI) | Managed (Bedrock/Vertex/Azure OpenAI) |
|---|---|---|
| Cost at scale | Lower per-token | Higher per-token |
| Operational burden | High (you manage GPUs, scaling, updates) | Low |
| Model choice | Any HuggingFace model | Provider's catalog only |
| Data sovereignty | Full control | Provider's data policy |
| Cold start | Predictable (always-on) | Possible (serverless) |
| Best for | >10M tokens/day, specific model requirements | Prototypes, low-medium volume, speed to market |

---

## 7. Cost Management Patterns

### Token optimization
- **Prompt compression:** LLMLingua reduces prompt tokens by 3-5x with minimal quality loss on long contexts.
- **Context window management:** Only pass the most relevant retrieved chunks; trim system prompts aggressively.
- **Output constraints:** Specify max_tokens and output format (JSON schema) to prevent runaway generation.

### Caching
- **Exact caching:** Cache identical queries (Redis). Effective for FAQ-style applications.
- **Semantic caching (GPTCache):** Cache by embedding similarity. Effective when queries are paraphrases of each other. Risks: cache poisoning, stale answers.
- **Prompt prefix caching:** AWS Bedrock and Anthropic support caching repeated system prompts across requests — major cost reduction for applications with long static system prompts.

### Model routing
Use a router (LiteLLM) to send requests to cheaper models when query complexity is low:
- Simple factual queries → small/cheap model
- Complex reasoning → large/expensive model
- Classify by query type, length, or confidence score from small model

---

## 8. Agentic System Design Patterns

### ReAct (Reason + Act)
The LLM alternates between reasoning ("I need to look up X") and acting (calling a tool). After each action, it observes the result and reasons again. Loop terminates when the LLM decides it has enough information.

**Key design controls:**
- `max_iterations` — hard stop to prevent infinite loops
- `max_tokens_per_step` — prevent single-step runaway
- Confidence threshold — if model expresses uncertainty repeatedly, escalate to human
- Tool call validation — validate structured tool arguments before execution

### Orchestrator + Sub-agent
A coordinator agent decomposes tasks and delegates to specialized sub-agents (research agent, writing agent, code agent). Enables parallelism and specialization.

**Communication patterns:** Shared message queue, direct function calls, or structured handoff prompts. Always log inter-agent messages for debugging.

### Human-in-the-loop checkpoints
Insert mandatory human review before:
- Irreversible actions (send email, write to database, deploy code)
- High-value decisions (financial transactions, customer communications)
- Low-confidence steps (model's own uncertainty score below threshold)

---

## 9. LLMOps CI/CD Patterns

### Treating prompts as code
- Store prompts in version control (git) with semantic versioning
- Code review for prompt changes — require another engineer to approve
- Changelog for prompts: what changed, why, eval results before/after

### Eval gates in CI/CD
```
On every PR that touches prompts or RAG config:
  1. Run offline eval suite against golden dataset
  2. Compare metrics to baseline (last merged version)
  3. Block merge if faithfulness drops > 5% or answer relevance drops > 3%
  4. Post metric summary as PR comment
```

### Canary prompt rollouts
Deploy new prompt version to 5% of traffic. Monitor production metrics (cost, latency, user satisfaction signals). Promote to 100% if metrics hold, rollback if degradation detected.
