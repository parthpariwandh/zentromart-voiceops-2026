"""ZentroMart VoiceOps Capstone – Knowledge Base RAG Module
Preserves section IDs, status, effective_from. Prioritizes current policies.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

class KnowledgeBase:
    def __init__(self, kb_dir: str = "data/kb", model_name: str = "all-MiniLM-L6-v2"):
        self.kb_dir = Path(kb_dir)
        self.chunks: List[Dict[str, Any]] = []
        self.embedder = SentenceTransformer(model_name)
        self.embeddings = None
        self._load_and_chunk()

    def _parse_md(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        meta = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].strip().splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip()
                body = parts[2]
            else:
                body = text
        else:
            body = text
        return meta, body

    def _load_and_chunk(self):
        for md in sorted(self.kb_dir.glob("*.md")):
            meta, body = self._parse_md(md)
            sections = re.split(r"(?=^## \[[A-Z0-9.-]+\])", body, flags=re.MULTILINE)
            for sec in sections:
                sec = sec.strip()
                if not sec or not sec.startswith("##"):
                    continue
                m = re.match(r"## \[([A-Z0-9.-]+)\]\s*(.*)", sec)
                if not m:
                    continue
                section_id = m.group(1)
                title = m.group(2).split("\n")[0].strip()
                content = sec
                self.chunks.append({
                    "section_id": section_id,
                    "title": title,
                    "content": content,
                    "doc_id": meta.get("doc_id", ""),
                    "doc_type": meta.get("doc_type", ""),
                    "status": meta.get("status", "current"),
                    "effective_from": meta.get("effective_from", ""),
                    "file": md.name,
                    "precedence": self._precedence(meta.get("doc_type", ""), meta.get("status", "current")),
                })
        if self.chunks:
            texts = [c["content"] for c in self.chunks]
            self.embeddings = self.embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def _precedence(self, doc_type: str, status: str) -> int:
        if status != "current":
            return 99
        order = {"policy": 1, "agent_guide": 2, "help": 3, "faq": 4, "marketing": 5, "meta": 0}
        return order.get(doc_type, 10)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.embeddings is None or not self.chunks:
            return []
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        scores = np.dot(self.embeddings, q_emb.T).flatten()
        ranked = sorted(enumerate(scores), key=lambda x: (-x[1], self.chunks[x[0]]["precedence"]))
        results = []
        for idx, score in ranked[:top_k]:
            c = self.chunks[idx].copy()
            c["score"] = float(score)
            results.append(c)
        return results

    def get_section(self, section_id: str) -> Dict[str, Any] | None:
        for c in self.chunks:
            if c["section_id"] == section_id:
                return c
        return None
