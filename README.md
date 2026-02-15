# 📞 AI Call Intelligence

AI-powered call transcription and analysis system using Groq's Whisper and LLaMA models.

## Features

- 🎙️ **Audio Transcription** - High-accuracy transcription using Groq Whisper (whisper-large-v3)
- 🤖 **AI Analysis** - Comprehensive call analysis with LLaMA 3.3 70B
  - Sentiment detection
  - Category classification
  - Escalation risk assessment
  - Key insights extraction
- 📊 **Trend Analytics** - Aggregate insights across multiple calls
- 💾 **Excel Storage** - Simple and portable data persistence
- 🎨 **Modern UI** - Clean Streamlit interface with custom styling

## Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Groq API (Whisper + LLaMA 3.3)
- **Storage**: Excel (pandas/openpyxl)
- **Language**: Python 3.x

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/thelakshyadubey/AI-Call-Intelligence.git
   cd AI-Call-Intelligence
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # or
   source venv/bin/activate      # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   
   Get your free API key at: https://console.groq.com/

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
AI-Call-Intelligence/
├── app.py                          # Main Streamlit application
├── requirements.txt                 # Python dependencies
├── .env                            # API keys (create this)
├── .gitignore                      # Git ignore rules
├── call_records.xlsx               # Data storage (auto-created)
├── data/
│   ├── __init__.py
│   └── repository.py               # Data persistence layer
└── services/
    ├── __init__.py
    ├── groq_client.py              # Groq API client
    ├── transcription_service.py    # Audio transcription
    ├── analysis_service.py         # Call analysis
    └── trend_service.py            # Trend analytics
```

## Usage

1. **Upload Audio Files**
   - Support for MP3, WAV, M4A, FLAC formats
   - Maximum file size: 25MB per file
   - Multiple files supported

2. **View Analysis**
   - Real-time transcription
   - AI-powered insights
   - Sentiment and risk assessment

3. **Analyze Trends**
   - View all calls or last N calls
   - Aggregate sentiment analysis
   - Category distribution
   - Risk metrics and patterns

## Features in Detail

### Call Analysis Output
- **Summary**: Concise overview of the call
- **Sentiment**: Positive/Negative/Neutral classification
- **Category**: Issue type (Billing, Technical, etc.)
- **Escalation Risk**: Percentage-based risk score
- **Key Points**: Bullet-point highlights
- **Recommended Actions**: Next steps for resolution

### Trend Analysis
- Total calls tracking
- Sentiment distribution across calls
- Top issue categories
- Average and median escalation risk
- High-risk call identification
- Recent call summaries

## Requirements

- Python 3.8+
- Groq API key (free tier available)
- Internet connection for API calls

## Dependencies

```
streamlit
groq
pandas
openpyxl
python-dotenv
```

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

This project is open source and available under the MIT License.

## Author

**Lakshya Dubey**
- GitHub: [@thelakshyadubey](https://github.com/thelakshyadubey)

## Acknowledgments

- Groq for providing fast and accurate AI models
- Streamlit for the excellent web framework
- OpenAI for Whisper model architecture

---

Made with ❤️ using Groq AI
