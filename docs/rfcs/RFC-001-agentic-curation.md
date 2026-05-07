# RFC-001: Multi-Agent Signal Curation

**Authors**: Antigravity
**Status**: Proposed
**Date**: 2026-05-07

## 1. Abstract
We propose moving from a static keyword-based signal filtering system to a multi-agent orchestration pipeline. This will use Llama 3.3 (via Groq) to rank news items by semantic relevance and the Curator Agent to synthesize final digests.

## 2. Motivation
Keyword filtering results in high false positives (noise) and misses relevant items that don't use specific jargon. An LLM-based agent can understand context and user "intent" rather than just strings.

## 3. Proposed Design
### 3.1 Pipeline
1. **Collector**: Scrapes raw signals (YouTube/Blogs).
2. **Ranker (Curator Agent)**: Takes user interest profile and signal metadata. Assigns a 0-10 score.
3. **Synthesizer (Digest Agent)**: Takes Top-N signals and generates a cohesive summary.
4. **Dispatcher (Email Agent)**: Formats and sends the result.

### 3.2 Performance Impact
- **Latency**: LLM inference adds ~2s per user. We will mitigate this with parallel async requests.
- **Cost**: Moving to Groq API ensures high throughput with minimal overhead.

## 4. Alternative Approaches
- **Embeddings/Vector Search**: High accuracy but requires a vector DB and constant indexing. We chose direct LLM ranking for the initial "hot" signal window (last 24-48h).

## 5. Security Considerations
- Ensure user PI (emails) are not passed to the LLM; only IDs and interests.
