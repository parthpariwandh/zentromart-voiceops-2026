# ZentroMart VoiceOps 2026 – Capstone
## From Tokens to Transformers | Consulting & Analytics Club, IIT Guwahati × Gnani.ai

### Overview
Conversational customer-support agent for the fictional Indian online store **ZentroMart**.
- Step 1: Prompting (baseline)
- Step 2: RAG over company documents (section-ID preserving)
- Step 3: Multi-turn conversation + tools (`lookup_order`, `create_ticket`) with verification
- Step 4: Voice wrapper for Gnani STT/TTS (requires `GNANI_API_KEY`)

Answers are grounded in the knowledge base. Unsupported questions trigger abstention + ticket.

### Dataset
Uses the official `Capstone_Project_Dataset_FTTT_2026` (synthetic only). Today's date = 20 October 2026.
Download from: https://drive.google.com/file/d/1jeGjWgZJ4vdfmbB71kghovcCUYNeSHOY/view
See `data/README.md` for extraction instructions.

### Setup
```bash
pip install -r requirements.txt
# Optional voice
pip install gnani-vachana
export GNANI_API_KEY=your_key_here   # from app.gnani.ai/voice
```

### Run evaluation (Step 1 vs Step 2)
```bash
python -m src.evaluate
```
Outputs go to `outputs/`.

### Batch run (organizer command)
```bash
python run.py --input_dir /path/to/audio_or_txt_folder --output_dir sample_outputs
```
Writes one JSON per input with reply text + retrieved section IDs.  
If `GNANI_API_KEY` is set, STT/TTS can be wired (see `src/voice.py`).

### Structure
- `src/kb_rag.py` – chunking + embedding retrieval (preserves `[SECTION-ID]`, precedence)
- `src/agent.py` – conversational agent + verification + tools
- `src/evaluate.py` – practice question scoring
- `run.py` – batch runner
- `report.pdf` – short report (max 4 pages) – see local artifacts or regenerate
- `data/README.md` – dataset download instructions

### Notes
- No API keys are committed.
- Hardcoded answers are avoided; responses come from retrieved chunks or tools.
- For full LLM generation, replace the deterministic reply synthesizer in `agent.py` with a call to any hosted/open LLM while keeping the same retrieval and tool interface.

### GitHub
https://github.com/parthpariwandh/zentromart-voiceops-2026

### License
MIT. Dataset attribution: Official Capstone pack from IIT Guwahati CAC × Gnani.ai.
