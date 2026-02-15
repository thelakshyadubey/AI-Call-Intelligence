"""Audio transcription service using Groq Whisper"""

def transcribe_audio(client, audio_file, filename):
    """
    Transcribe audio file to text using Groq Whisper
    
    Args:
        client: Groq client instance
        audio_file: Audio file bytes
        filename: Name of the audio file
        
    Returns:
        str: Transcribed text
    """
    transcription = client.audio.transcriptions.create(
        file=(filename, audio_file),
        model="whisper-large-v3",
        response_format="json",
        language="en"
    )
    return transcription.text
