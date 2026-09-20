from app.ai.memory.summarizer import summarize_messages


def test_summarizer_extracts_keywords():
    messages = [
        "I prefer currency INR and want to focus on savings.",
        "My risk tolerance is medium.",
        "I want retirement planning advice.",
    ]

    summary = summarize_messages(messages, max_chars=500)
    assert summary
    assert "inr" in summary.lower() or "risk" in summary.lower() or "retirement" in summary.lower()
