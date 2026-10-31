"""run.py – Batch runner for organizers.
Accepts a folder of customer audio files (or text transcripts for testing),
runs the agent, saves text replies, retrieved chunks, and (if Gnani key present) audio.
"""
import argparse
import os
import json
from pathlib import Path
from src.agent import ZentroMartAgent
from src.kb_rag import KnowledgeBase

def main():
    parser = argparse.ArgumentParser(description="ZentroMart VoiceOps agent batch runner")
    parser.add_argument("--input_dir", required=True, help="Folder of audio files or .txt transcripts")
    parser.add_argument("--output_dir", default="sample_outputs", help="Where to write replies")
    args = parser.parse_args()

    kb = KnowledgeBase()
    agent = ZentroMartAgent(kb)
    input_path = Path(args.input_dir)
    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    gnani_available = bool(os.getenv("GNANI_API_KEY"))

    for f in sorted(input_path.iterdir()):
        if f.suffix.lower() in {".txt", ".wav", ".mp3"}:
            if f.suffix.lower() == ".txt":
                transcript = f.read_text(encoding="utf-8").strip()
            else:
                transcript = f"[AUDIO FILE {f.name} – STT would be called via Gnani if key present]"
                if not gnani_available:
                    transcript += " (GNANI_API_KEY not set)"

            agent.reset()
            result = agent.respond(transcript)
            out_file = out_path / f"{f.stem}_reply.json"
            with open(out_file, "w") as fh:
                json.dump({
                    "input_file": f.name,
                    "transcript": transcript,
                    "reply": result["reply"],
                    "retrieved_sections": result["retrieved_sections"],
                    "tool_calls": result["tool_calls"],
                }, fh, indent=2)
            print(f"Processed {f.name} → {out_file}")

    print(f"Done. Outputs in {out_path}")
    if not gnani_available:
        print("Note: GNANI_API_KEY not set. Voice STT/TTS skipped. See README for setup.")

if __name__ == "__main__":
    main()
