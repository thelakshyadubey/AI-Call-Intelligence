import streamlit as st

# Import services
from services.groq_client import get_groq_client, get_api_key
from services.transcription_service import transcribe_audio
from services.analysis_service import analyze_call
from services.trend_service import analyze_trends
from data.repository import (
    database_exists, 
    get_all_records, 
    get_record_count, 
    prepare_trend_summary, 
    save_record
)

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Call Intelligence",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== COMPREHENSIVE UI STYLING ====================


st.markdown("""
<style>
            
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Apply Inter font but DO NOT override icon fonts */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* IMPORTANT: Keep Material Icons working */
    .material-icons {
        font-family: 'Material Icons' !important;
    }
    
            
    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* Background with subtle gradient */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8f8f8 0%, #ffffff 50%, #f5f5f5 100%) !important;
    }
    
    .main, .block-container {
        background-color: transparent !important;
    }
    
    /* Tighter spacing */
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
        max-width: 1200px;
    }
    
    /* Header with gradient background */
    .minimal-header {
        padding: 2rem 0 1.5rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #fafafa 50%, #f8f8f8 100%);
        border: none;
        margin: -1.5rem -2rem 2rem -2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .minimal-header h1 {
        font-size: 2.2rem;
        font-weight: 400;
        color: #000000 !important;
        margin: 0;
    }
    .minimal-header p {
        color: #666666 !important;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* ============ SIDEBAR STYLING ============ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%) !important;
        border-right: none;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
        min-width: 240px !important;
        max-width: 240px !important;
    }
    
    /* Hide sidebar collapse/expand button completely */
    button[data-testid="baseButton-headerNoPadding"] {
        display: none !important;
    }
    
    /* Backup selector for older Streamlit versions */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Sidebar text - force white with high specificity */
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        width: 100%;
        box-shadow: 0 2px 6px rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #f5f5f5 0%, #ebebeb 100%) !important;
        transform: translateY(-1px);
    }
    section[data-testid="stSidebar"] .stButton > button * {
        color: #000000 !important;
    }
    
    /* Sidebar metrics */
    section[data-testid="stSidebar"] [data-testid="stMetric"] {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        border: none !important;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #999999 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem;
        font-weight: 300;
    }
    
    /* ============ MAIN AREA STYLING ============ */
    
    /* All text in main area - ensure visibility */
    .main *,
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
    .main p, .main span, .main div, .main label,
    .element-container * {
        color: #2a2a2a !important;
    }
    
    .main h1, .main h2, .main h3, .main h4 {
        color: #000000 !important;
        font-weight: 500;
    }
    
    .main .caption, .main [data-testid="stCaptionContainer"] {
        color: #666666 !important;
    }
    
    /* Main area buttons */
    .main .stButton > button {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    .main .stButton > button:hover {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transform: translateY(-1px);
    }
    .main .stButton > button * {
        color: #ffffff !important;
    }
    
    /* Main area metrics */
    .main [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f8f8 100%) !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .main [data-testid="stMetricLabel"] {
        color: #666666 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .main [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 2rem;
        font-weight: 300;
    }
    
    /* ============ FILE UPLOADER ============ */
    [data-testid="stFileUploader"] {
        border: 1px solid #e0e0e0 !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%) !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03) !important;
    }
    [data-testid="stFileUploader"] section {
        border: 1px dashed #c0c0c0 !important;
        background: linear-gradient(135deg, #f8f8f8 0%, #f0f0f0 100%) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #999999 !important;
        background: linear-gradient(135deg, #f5f5f5 0%, #ebebeb 100%) !important;
    }
    
    /* File uploader text - force dark colors */
    [data-testid="stFileUploader"] *,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div {
        color: #2a2a2a !important;
    }
    [data-testid="stFileUploader"] small {
        color: #666666 !important;
    }
    
    /* Browse button in file uploader - keep white text on dark button */
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button * {
        color: #ffffff !important;
    }
    
    /* ============ STATUS WIDGETS ============ */
    div[data-testid="stStatusWidget"],
    [data-testid="stStatusWidget"] {
        background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%) !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        margin: 0.5rem 0 !important;
        color: #1a1a1a !important;
    }
    
    /* Ensure status widget text/icons always stay readable */
    div[data-testid="stStatusWidget"] *,
    [data-testid="stStatusWidget"] * {
        color: inherit !important;
    }
    div[data-testid="stStatusWidget"] svg,
    [data-testid="stStatusWidget"] svg {
        fill: currentColor !important;
        color: inherit !important;
    }
    
    /* Completed status widgets - dark background with white text */
    div[data-testid="stStatusWidget"][data-test-script-state="complete"],
    [data-testid="stStatusWidget"][data-test-script-state="complete"],
    div[data-testid="stStatusWidget"][data-state="complete"],
    [data-testid="stStatusWidget"][data-state="complete"],
    div[data-testid="stStatusWidget"][data-test-state="complete"],
    [data-testid="stStatusWidget"][data-test-state="complete"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%) !important;
        border-color: #333333 !important;
        color: #ffffff !important;
    }

    /* Status header bar (e.g., “Transcription complete”, “Analyzing…”) */
    div[data-testid="stStatusWidget"] details > summary,
    [data-testid="stStatusWidget"] details > summary {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 0.85rem 1.1rem !important;
        color: #111111 !important;
        box-shadow: none !important;
        transition: none !important;
        transform: none !important;
    }
    div[data-testid="stStatusWidget"] details > summary *,
    [data-testid="stStatusWidget"] details > summary * {
        color: #111111 !important;
        transition: none !important;
    }
    div[data-testid="stStatusWidget"] details > summary svg,
    [data-testid="stStatusWidget"] details > summary svg {
        fill: currentColor !important;
        color: #111111 !important;
    }
    div[data-testid="stStatusWidget"] details > summary:hover,
    [data-testid="stStatusWidget"] details > summary:hover {
        background: #ffffff !important;
        border-color: #e0e0e0 !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* Streamlit often renders st.status headers as a BaseWeb accordion button.
       Force it to simple white + dark text, and remove hover animation. */
    div[data-testid="stStatusWidget"] [data-baseweb="accordion"] button,
    [data-testid="stStatusWidget"] [data-baseweb="accordion"] button {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        transition: none !important;
        transform: none !important;
        color: #111111 !important;
    }
    div[data-testid="stStatusWidget"] [data-baseweb="accordion"] button:hover,
    [data-testid="stStatusWidget"] [data-baseweb="accordion"] button:hover {
        background: #ffffff !important;
        border-color: #e0e0e0 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    div[data-testid="stStatusWidget"] [data-baseweb="accordion"] button *,
    [data-testid="stStatusWidget"] [data-baseweb="accordion"] button * {
        color: #111111 !important;
        transition: none !important;
    }
    div[data-testid="stStatusWidget"] [data-baseweb="accordion"] button svg,
    [data-testid="stStatusWidget"] [data-baseweb="accordion"] button svg {
        fill: currentColor !important;
        color: #111111 !important;
    }

    /* When status is complete, make the header bar dark + readable */
    div[data-testid="stStatusWidget"][data-test-script-state="complete"] details > summary,
    [data-testid="stStatusWidget"][data-test-script-state="complete"] details > summary,
    div[data-testid="stStatusWidget"][data-state="complete"] details > summary,
    [data-testid="stStatusWidget"][data-state="complete"] details > summary,
    div[data-testid="stStatusWidget"][data-test-state="complete"] details > summary,
    [data-testid="stStatusWidget"][data-test-state="complete"] details > summary {
        background: #ffffff !important;
        border-color: #e0e0e0 !important;
        color: #111111 !important;
    }
    div[data-testid="stStatusWidget"][data-test-script-state="complete"] details > summary *,
    [data-testid="stStatusWidget"][data-test-script-state="complete"] details > summary *,
    div[data-testid="stStatusWidget"][data-state="complete"] details > summary *,
    [data-testid="stStatusWidget"][data-state="complete"] details > summary *,
    div[data-testid="stStatusWidget"][data-test-state="complete"] details > summary *,
    [data-testid="stStatusWidget"][data-test-state="complete"] details > summary * {
        color: #111111 !important;
    }
    div[data-testid="stStatusWidget"][data-test-script-state="complete"] details > summary svg,
    [data-testid="stStatusWidget"][data-test-script-state="complete"] details > summary svg,
    div[data-testid="stStatusWidget"][data-state="complete"] details > summary svg,
    [data-testid="stStatusWidget"][data-state="complete"] details > summary svg,
    div[data-testid="stStatusWidget"][data-test-state="complete"] details > summary svg,
    [data-testid="stStatusWidget"][data-test-state="complete"] details > summary svg {
        fill: currentColor !important;
        color: #111111 !important;
    }

    /* Nested expander header inside status (e.g., “Transcript”) */
    div[data-testid="stStatusWidget"] [data-testid="stExpander"] summary,
    [data-testid="stStatusWidget"] [data-testid="stExpander"] summary,
    div[data-testid="stStatusWidget"] .streamlit-expanderHeader,
    [data-testid="stStatusWidget"] .streamlit-expanderHeader {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        color: #111111 !important;
        box-shadow: none !important;
        transition: none !important;
        transform: none !important;
    }
    div[data-testid="stStatusWidget"] [data-testid="stExpander"] summary *,
    [data-testid="stStatusWidget"] [data-testid="stExpander"] summary * {
        color: #111111 !important;
        transition: none !important;
    }
    div[data-testid="stStatusWidget"] [data-testid="stExpander"] summary svg,
    [data-testid="stStatusWidget"] [data-testid="stExpander"] summary svg {
        fill: currentColor !important;
        color: #111111 !important;
    }
    div[data-testid="stStatusWidget"] [data-testid="stExpander"] summary:hover,
    [data-testid="stStatusWidget"] [data-testid="stExpander"] summary:hover {
        background: #ffffff !important;
        border-color: #e0e0e0 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    /* ============ ALERTS & INFO MESSAGES ============ */
    div[data-testid="stAlert"] {
        background: linear-gradient(135deg, #f0f0f0 0%, #e8e8e8 100%) !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 12px !important;
        color: #1a1a1a !important;
        padding: 1rem 1.25rem !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
        margin: 1rem 0 !important;
    }
    div[data-testid="stAlert"] * {
        color: #1a1a1a !important;
    }
    
    /* Success alerts */
    div[data-testid="stAlert"][data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, #e8f5e8 0%, #d0f0d0 100%) !important;
        border-color: #90c690 !important;
        color: #0d5016 !important;
    }
    div[data-testid="stAlert"][data-baseweb="notification"][kind="success"] * {
        color: #0d5016 !important;
    }
    
    /* Error alerts */
    div[data-testid="stAlert"][data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, #f5e8e8 0%, #f0d0d0 100%) !important;
        border-color: #c69090 !important;
        color: #501616 !important;
    }
    div[data-testid="stAlert"][data-baseweb="notification"][kind="error"] * {
        color: #501616 !important;
    }
    
    /* Warning alerts */
    div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, #f5f0e8 0%, #f0e8d0 100%) !important;
        border-color: #c6a890 !important;
        color: #503016 !important;
    }
    div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] * {
        color: #503016 !important;
    }
    
    /* ============ EXPANDERS ============ */

    /* ===== REMOVE DARK BAR FROM EXPANDERS (Transcript etc.) ===== */

    /* Main expander container */
    div[data-testid="stExpander"],
    [data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        animation: none !important;
        transition: none !important;
    }

    /* Expander header button */
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] button,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] button,
    div[data-testid="stExpander"] .streamlit-expanderHeader,
    [data-testid="stExpander"] .streamlit-expanderHeader {
        background: #ffffff !important;
        color: #111111 !important;
        border: none !important;
        box-shadow: none !important;
        animation: none !important;
        transition: none !important;
        transform: none !important;
    }

    /* Remove hover animation */
    div[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] button:hover,
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] button:hover,
    div[data-testid="stExpander"] .streamlit-expanderHeader:hover,
    [data-testid="stExpander"] .streamlit-expanderHeader:hover {
        background: #ffffff !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* Fix arrow icon color */
    div[data-testid="stExpander"] svg,
    [data-testid="stExpander"] svg {
        fill: #111111 !important;
        color: #111111 !important;
    }
    
    /* Expander content text */
    [data-testid="stExpander"] *,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div {
        color: #2a2a2a !important;
    }
    
    /* ============ PROGRESS BARS ============ */
    .stProgress > div > div {
        background: linear-gradient(90deg, #e0e0e0 0%, #d0d0d0 100%) !important;
        border-radius: 10px !important;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%) !important;
        border-radius: 10px !important;
    }
    
    /* ============ DIVIDERS ============ */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent 0%, #d0d0d0 50%, transparent 100%) !important;
        margin: 2rem 0 !important;
    }
    
    /* ============ DATAFRAMES ============ */
    [data-testid="stDataFrame"] {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    [data-testid="stDataFrame"] * {
        color: #2a2a2a !important;
    }
    
    /* ============ MARKDOWN & TEXT ============ */
    .stMarkdown {
        color: #2a2a2a !important;
    }
    .stMarkdown * {
        color: inherit !important;
    }
    
    /* ============ CUSTOM CONTAINER STYLING ============ */
    .stContainer > div {
        background: transparent !important;
    }
    
    /* Force text visibility in any remaining components */
    .element-container p,
    .element-container span,
    .element-container div,
    .element-container label {
        color: #2a2a2a !important;
    }
    
    /* Custom white container styling */
    .stContainer [style*="background-color: white"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
        color: #1a1a1a !important;
        font-weight: 400 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    }

</style>
""", unsafe_allow_html=True)

# Initialize Groq client
try:
    client = get_groq_client()
    GROQ_API_KEY = get_api_key()
except ValueError as e:
    client = None
    GROQ_API_KEY = None

# ==================== HEADER ====================
st.markdown("""
<div class="minimal-header">
    <h1>AI Call Intelligence</h1>
    <p>Transform customer calls into actionable insights</p>
</div>
""", unsafe_allow_html=True)

if not GROQ_API_KEY:
    st.error("⚠️ Please set your GROQ_API_KEY in the .env file")
    st.stop()

# ==================== SIDEBAR ====================
st.sidebar.markdown("### Analytics")
st.sidebar.markdown("")

total_calls_metric = None
base_record_count = 0

if database_exists():
    base_record_count = int(get_record_count())
    total_calls_metric = st.sidebar.empty()
    total_calls_metric.metric("Total Calls", base_record_count)
    st.sidebar.markdown("")

    trend_scope = st.sidebar.radio(
        "Trend scope",
        ["All calls", "Last N calls"],
        index=0,
    )
    last_n = None
    if trend_scope == "Last N calls":
        # Initialize default value only once
        if 'last_n_value' not in st.session_state:
            st.session_state.last_n_value = min(20, int(base_record_count)) if int(base_record_count) > 0 else 1
        
        last_n = st.sidebar.number_input(
            "N",
            min_value=1,
            max_value=max(1, int(base_record_count)),
            value=st.session_state.last_n_value,
            step=1,
            key="last_n_input"
        )
        st.session_state.last_n_value = last_n
    
    if st.sidebar.button("Analyze Trends", width="stretch", type="primary"):
        df = get_all_records()
        df_for_trends = df
        if last_n is not None:
            df_for_trends = df.tail(int(last_n))

        summary = prepare_trend_summary(df_for_trends)
        
        with st.spinner("Analyzing..."):
            trend_analysis = analyze_trends(client, summary)
        
        st.markdown("### Trends & Insights")
        st.markdown(trend_analysis)
        
        with st.expander("View Database"):
            st.dataframe(df_for_trends, width="stretch", height=300)
else:
    st.sidebar.info("No data yet")

st.sidebar.markdown("---")

# ==================== MAIN ====================
uploaded_files = st.file_uploader(
    "Upload audio files",
    type=["mp3", "wav", "m4a", "flac", "mpeg", "mpga", "mp4"],
    accept_multiple_files=True,
    help="Support for MP3, WAV, M4A, FLAC, MPEG • Max 25MB"
)

if uploaded_files:
    progress_bar = st.progress(0)
    saved_this_run = 0
    
    for idx, audio_file in enumerate(uploaded_files, 1):
        progress_bar.progress(idx / len(uploaded_files))
        
        st.markdown(f"#### {audio_file.name}")
        st.caption(f"File {idx} of {len(uploaded_files)}")
        
        # Transcription
        try:
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio(client, audio_file.read(), audio_file.name)

            st.success("Transcription complete")
            with st.expander("Transcript", expanded=False):
                st.text(transcript)
        except Exception as e:
            st.error(str(e))
            continue
        
        # Analysis
        try:
            with st.spinner("Analyzing..."):
                analysis = analyze_call(client, transcript)

            st.success("Analysis complete")
            st.markdown(analysis)
        except Exception as e:
            st.error(str(e))
            continue
        
        # Save
        success, error = save_record(audio_file.name, transcript, analysis)
        if success:
            st.success("Saved to database", icon="✅")
            saved_this_run += 1
            if total_calls_metric is not None:
                total_calls_metric.metric("Total Calls", base_record_count + saved_this_run)
        else:
            st.warning(error)
        
        if idx < len(uploaded_files):
            st.divider()
    
    progress_bar.empty()
    st.success(f"Processed {len(uploaded_files)} file(s)")

else:
    with st.container():
        st.markdown("""
        <div style="
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            color: black;
        ">
            Upload call recordings to begin analysis
        </div>
        """, unsafe_allow_html=True)

# Footer
st.divider()
