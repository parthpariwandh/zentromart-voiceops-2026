"""ZentroMart Support Agent – Conversational RAG + Tools
Grounded answers only. Verification before order details. Handover via create_ticket.
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

sys.path.insert(0, str(Path(__file__).parent))
from tools.tools import lookup_order, create_ticket
from kb_rag import KnowledgeBase

TODAY = "2026-10-20"

SYSTEM_PROMPT = """You are ZentroMart's AI support assistant. Always introduce yourself as an AI assistant.
Answer ONLY from the provided knowledge-base excerpts and tool results. Never invent policies, dates, amounts or order details.
If the documents do not cover the question, say you do not have that information and offer to connect the customer to a human colleague.
Before sharing any specific order information, verify the customer (last 4 digits of phone or delivery pincode).
Use tools only when needed. Confirm a ticket was created only if the tool returned created=True.
Be concise, polite, and clear. Prefer current policy documents.
Today's date for all calculations is 20 October 2026.
"""

class ZentroMartAgent:
    def __init__(self, kb: Optional[KnowledgeBase] = None):
        self.kb = kb or KnowledgeBase()
        self.history: List[Dict[str, str]] = []
        self.state: Dict[str, Any] = {
            "order_id": None,
            "verified": False,
            "verification_attempts": 0,
            "customer_name": None,
        }

    def respond(self, user_message: str) -> Dict[str, Any]:
        self.history.append({"role": "user", "content": user_message})
        retrieved = self.kb.retrieve(user_message, top_k=5)
        context = "\n\n".join([f"[{c['section_id']}] {c['title']}\n{c['content']}" for c in retrieved])

        reply, tool_calls = self._generate_reply(user_message, context, retrieved)
        self.history.append({"role": "assistant", "content": reply})
        return {
            "reply": reply,
            "retrieved_sections": [c["section_id"] for c in retrieved],
            "chunks": retrieved,
            "tool_calls": tool_calls,
            "state": self.state.copy(),
        }

    def _generate_reply(self, message: str, context: str, chunks: List[Dict]) -> tuple:
        tool_calls = []
        msg_lower = message.lower()

        order_match = re.search(r"\b(\d{6,8})\b", message)
        if order_match and not self.state["order_id"]:
            self.state["order_id"] = order_match.group(1)

        if self.state["order_id"] and not self.state["verified"]:
            verif_match = re.search(r"\b(\d{4}|\d{6})\b", message)
            if verif_match and self.state["verification_attempts"] < 2:
                self.state["verification_attempts"] += 1
                result = lookup_order(self.state["order_id"], verification_value=verif_match.group(1))
                tool_calls.append({"tool": "lookup_order", "result": result})
                if result.get("verified"):
                    self.state["verified"] = True
                    self.state["customer_name"] = result.get("customer_first_name")
                    return self._order_status_reply(result, chunks), tool_calls
                else:
                    return ("Verification failed. Please provide the last 4 digits of the registered phone number or the delivery pincode for this order. You have one more attempt.", tool_calls)

        if not chunks or all(c["score"] < 0.25 for c in chunks):
            ticket = create_ticket(
                summary=f"Customer asked: {message}. No relevant policy found. Needs human review.",
                order_id=self.state.get("order_id"),
                reason="unsupported_query",
            )
            tool_calls.append({"tool": "create_ticket", "result": ticket})
            if ticket.get("created"):
                return ("I'm sorry, I don't have information about that in our current policies. I've created a support ticket and a human colleague will assist you shortly.", tool_calls)
            return ("I'm sorry, I don't have information about that. I can connect you to a human colleague.", tool_calls)

        top = chunks[0]
        reply = f"As ZentroMart's AI support assistant, based on our policy [{top['section_id']}] ({top['title']}):\n\n{top['content'][:600]}..."
        if self.state["order_id"] and self.state["verified"]:
            reply += "\n\n(I have your order on file and can check specific details if needed.)"
        return reply, tool_calls

    def _order_status_reply(self, order: Dict, chunks: List) -> str:
        status = order.get("status", "unknown")
        return (f"Hello {order.get('customer_first_name', 'there')}, I'm ZentroMart's AI assistant. "
                f"Your order {order['order_id']} is currently '{status}'. "
                f"Promised delivery was {order.get('promised_date', 'N/A')}. "
                f"How else can I help with this order?")

    def reset(self):
        self.history.clear()
        self.state = {"order_id": None, "verified": False, "verification_attempts": 0, "customer_name": None}
