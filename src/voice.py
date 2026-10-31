"""Optional Gnani voice wrapper.
Requires: pip install gnani-vachana and GNANI_API_KEY in environment.
Does not run without credentials.
"""
import os

def voice_turn(audio_path: str, agent) -> tuple:
    """Example integration. Returns (transcript, reply_text)."""
    if not os.getenv("GNANI_API_KEY"):
        return ("[GNANI_API_KEY missing]", "Voice layer requires Gnani credentials. See README.")
    try:
        from gnani.stt import GnaniSTTClient
        from gnani.tts import GnaniTTSClient
        stt = GnaniSTTClient()
        tts = GnaniTTSClient()
        heard = stt.transcribe(audio_path, language_code="en-IN")["transcript"]
        if not heard.strip():
            reply = "Sorry, I didn't catch that. Could you say it again?"
        else:
            result = agent.respond(heard)
            reply = result["reply"]
        tts.synthesize(reply, voice="Kaveri", model="timbre-v2.5", language="en-IN", output_file="reply.wav")
        return heard, reply
    except Exception as e:
        return ("[STT error]", f"Voice layer error: {e}")
