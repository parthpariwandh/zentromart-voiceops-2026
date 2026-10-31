# VoiceOps 2026 Capstone Report
## ZentroMart Customer Support Agent
**From Tokens to Transformers · Consulting & Analytics Club, IIT Guwahati × Gnani.ai**  
**Author:** Parth Pariwandh · Jadavpur University  
**GitHub:** https://github.com/parthpariwandh/zentromart-voiceops-2026

### 1. What was built in each step

**Step 1 – Prompting baseline**  
System prompt sets the role of ZentroMart AI support assistant. Without documents the model can only guess. Practice questions show near-zero grounded accuracy.

**Step 2 – RAG**  
All 21 Markdown documents are chunked on `## [SECTION-ID]` headings. Embeddings via all-MiniLM-L6-v2. Retrieval prefers current policy documents by precedence (KB-00.1). Unsupported queries abstain and open a ticket.  
On 52 practice questions, gold section retrieval accuracy ≈ **0.673**.

**Step 3 – Conversation + tools**  
State tracks order_id and verification status. `lookup_order` is called only after the customer supplies last-4 phone digits or delivery pincode. `create_ticket` is used for handovers; success is claimed only when the tool returns `created=True`.

**Step 4 – Voice**  
Thin wrapper around Gnani STT/TTS (`gnani-vachana`). Requires `GNANI_API_KEY`. Agent brain is unchanged. Audio batch runner writes text replies + retrieved section IDs.

### 2. Step 1 vs Step 2 comparison

Pure prompting baseline has no access to ZentroMart policies → effective accuracy ≈ 0 on document-dependent items.  
After RAG, retrieval of gold section IDs improved to ~67%. Exact numbers are in `outputs/evaluation_summary.json`.

### 3. What went wrong and what would be fixed

- Deterministic reply synthesis is used for reproducibility without external LLM keys; swapping in a real LLM (while keeping retrieval and tool calls) would improve naturalness.
- Verification and multi-turn memory are rule-based; an LLM planner would handle more varied phrasing.
- Voice layer is fully specified but not executed here because no Gnani key was supplied in the environment.

### 4. Architecture and compliance

All answers are derived from retrieved chunks or tool results. Section IDs are preserved. Dataset date 20 October 2026 is respected. No real customer data is used. Secrets stay in `.env`.

### 5. How to run

```bash
pip install -r requirements.txt
python -m src.evaluate
python run.py --input_dir sample_inputs --output_dir sample_outputs
```

This report is kept concise as required. Full source, evaluation outputs and README are in the repository.  
A PDF version is available in the local submission package.
