"""Call analysis service using Groq LLM"""

def analyze_call(client, transcript):
    """
    Analyze call transcript using AI
    
    Args:
        client: Groq client instance
        transcript: Call transcript text
        
    Returns:
        str: AI analysis with structured insights
    """
    prompt = f"""Analyze this call:

{transcript}

Format:
**Summary:** [Brief overview]
**Sentiment:** [Positive/Neutral/Negative]
**Escalation Risk:** [0-100%]
**Why:** [Explain the risk score with quotes]
**Emotional Journey:** [Beginning → Peak frustration → End state]
**Category:** [Issue type]
**Action:** [What to do next]"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a customer call analyst. Provide structured insights."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return completion.choices[0].message.content
