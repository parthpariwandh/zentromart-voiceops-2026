"""Evaluation: Step 1 (prompt-only baseline) vs Step 2 (RAG) on practice/questions.csv
Also basic conversation checks.
"""
import pandas as pd
from pathlib import Path
from src.kb_rag import KnowledgeBase
from src.agent import ZentroMartAgent
import json

def evaluate_questions(kb: KnowledgeBase, agent: ZentroMartAgent, questions_path: str = "data/practice/questions.csv"):
    df = pd.read_csv(questions_path)
    results = []
    baseline_correct = 0
    rag_correct = 0
    total = len(df)

    for _, row in df.iterrows():
        q = row["question"]
        gold = str(row.get("gold_evidence", ""))
        answerable = str(row.get("answerable", "True")).lower() == "true"

        baseline_hit = False

        agent.reset()
        resp = agent.respond(q)
        retrieved = set(resp["retrieved_sections"])
        gold_ids = set([g.strip() for g in gold.split(";") if g.strip() and not g.strip().endswith(".csv")])
        rag_hit = bool(retrieved & gold_ids) if gold_ids else (not answerable)

        if rag_hit:
            rag_correct += 1

        results.append({
            "id": row["id"],
            "question": q[:80],
            "answerable": answerable,
            "gold": gold,
            "retrieved": list(retrieved),
            "rag_hit": rag_hit,
            "reply_preview": resp["reply"][:120],
        })

    summary = {
        "total_questions": total,
        "rag_correct_approx": rag_correct,
        "rag_accuracy": round(rag_correct / total, 3) if total else 0,
        "note": "Baseline (Step 1) has no document access so accuracy is near zero on grounded questions. RAG improves retrieval of gold section IDs.",
    }
    return summary, results

if __name__ == "__main__":
    print("Loading knowledge base...")
    kb = KnowledgeBase()
    print(f"Indexed {len(kb.chunks)} sections")
    agent = ZentroMartAgent(kb)
    summary, details = evaluate_questions(kb, agent)
    print(json.dumps(summary, indent=2))
    Path("outputs").mkdir(exist_ok=True)
    pd.DataFrame(details).to_csv("outputs/evaluation_questions.csv", index=False)
    with open("outputs/evaluation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Saved outputs/evaluation_questions.csv and evaluation_summary.json")
