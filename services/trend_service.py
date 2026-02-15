"""Trend analysis service for historical call data"""

def analyze_trends(client, call_data_summary):
    """
    Analyze trends across multiple call records
    
    Args:
        client: Groq client instance
        call_data_summary: Summary of historical call data
        
    Returns:
        str: Trend analysis with insights and recommendations
    """
    prompt = f"""Analyze these call records:
{call_data_summary}

Provide: Trend Analysis, Critical Insights, and Recommendations."""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a customer experience analyst. Find patterns and give actionable insights."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return completion.choices[0].message.content
