"""Database repository for call records (AWS S3 storage)"""
import os
import re
import tempfile
from datetime import datetime
from io import BytesIO

import pandas as pd
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FILE_KEY = os.getenv("S3_FILE_KEY", "call_records.xlsx")

# Optional: Use local storage if S3 not configured (for local development)
USE_S3 = os.getenv("USE_S3", "true").lower() == "true"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
LOCAL_EXCEL_FILE = os.path.join(PROJECT_ROOT, "call_records.xlsx")

CANONICAL_COLUMNS = ["Date", "File Name", "Transcript", "Analysis"]

# Initialize S3 client
s3_client = None
if USE_S3:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
    except Exception as e:
        print(f"Warning: Could not initialize S3 client: {e}")
        print("Falling back to local storage")
        USE_S3 = False


def _normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and ensure canonical columns exist.

    This prevents schema drift (e.g., 'Filename' vs 'File Name') from causing
    blanks/NaNs in key fields.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)

    working = df.copy()
    col_lookup = {str(c).strip().lower(): c for c in working.columns}

    def _coalesce(target: str, candidates: list[str]) -> None:
        existing_target = target if target in working.columns else None
        candidate_cols = [col_lookup.get(c) for c in candidates if col_lookup.get(c) in working.columns]

        if existing_target is None:
            if candidate_cols:
                working[target] = working[candidate_cols[0]]
            else:
                working[target] = pd.NA
        else:
            for c in candidate_cols:
                if c == target:
                    continue
                working[target] = working[target].fillna(working[c])

    _coalesce("Date", ["date", "datetime", "timestamp", "time", "created at", "created_at"])
    _coalesce("File Name", ["file name", "filename", "file_name", "file", "audio", "audio file", "audio_file"])
    _coalesce("Transcript", ["transcript", "transcription", "text"])
    _coalesce("Analysis", ["analysis", "ai analysis", "llm analysis", "insights"])

    # Preserve any extra columns, but always keep canonical columns first.
    ordered = CANONICAL_COLUMNS + [c for c in working.columns if c not in CANONICAL_COLUMNS]
    working = working[ordered]
    return working


def _download_from_s3():
    """Download Excel file from S3 to memory"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
        return BytesIO(response['Body'].read())
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # File doesn't exist yet, return None
            return None
        else:
            raise


def _upload_to_s3(excel_buffer):
    """Upload Excel file from memory to S3"""
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_FILE_KEY,
            Body=excel_buffer.getvalue(),
            ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False


def database_exists():
    """Check if database file exists (S3 or local)"""
    if USE_S3 and s3_client:
        try:
            s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
            return True
        except ClientError:
            return False
    else:
        return os.path.exists(LOCAL_EXCEL_FILE)


def get_all_records():
    """Load all call records from S3 or local storage"""
    if USE_S3 and s3_client:
        try:
            excel_data = _download_from_s3()
            if excel_data is None:
                return pd.DataFrame(columns=CANONICAL_COLUMNS)
            df = pd.read_excel(excel_data)
            return _normalize_schema(df)
        except Exception as e:
            print(f"Error reading from S3: {e}")
            return pd.DataFrame(columns=CANONICAL_COLUMNS)
    else:
        # Fallback to local storage
        if not os.path.exists(LOCAL_EXCEL_FILE):
            return pd.DataFrame(columns=CANONICAL_COLUMNS)
        df = pd.read_excel(LOCAL_EXCEL_FILE)
        return _normalize_schema(df)


def get_record_count():
    """Get total number of records"""
    df = get_all_records()
    return len(df)


def save_record(filename, transcript, analysis):
    """
    Save a new call record to S3 or local storage
    
    Args:
        filename: Name of the audio file
        transcript: Transcribed text
        analysis: AI analysis result
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    safe_filename = "" if filename is None else str(filename)
    safe_filename = os.path.basename(safe_filename).strip()
    if not safe_filename:
        safe_filename = "Unknown"

    new_record = pd.DataFrame(
        {
            "Date": [datetime.now()],
            "File Name": [safe_filename],
            "Transcript": [transcript],
            "Analysis": [analysis],
        }
    )
    
    try:
        # Load existing records or create new
        if database_exists():
            existing = get_all_records()
            updated = pd.concat([existing, new_record], ignore_index=True)
        else:
            updated = new_record

        updated = _normalize_schema(updated)
        updated["File Name"] = updated["File Name"].fillna("Unknown")
        
        # Save to S3 or local
        if USE_S3 and s3_client:
            # Save to memory buffer
            excel_buffer = BytesIO()
            updated.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            
            # Upload to S3
            if _upload_to_s3(excel_buffer):
                return True, None
            else:
                return False, "Failed to upload to S3"
        else:
            # Save to local file
            updated.to_excel(LOCAL_EXCEL_FILE, index=False)
            return True, None
        
    except PermissionError:
        return False, "Excel file is open! Close 'call_records.xlsx' and try again."
    except Exception as e:
        return False, f"Error saving record: {str(e)}"


def prepare_trend_summary(df):
    """Prepare data summary for trend analysis"""
    if df.empty:
        return "No data available"

    expected_cols = {"Date", "File Name", "Analysis"}
    missing_cols = expected_cols - set(df.columns)
    if missing_cols:
        return (
            "The database is missing required columns: "
            f"{', '.join(sorted(missing_cols))}. "
            "Expected columns: Date, File Name, Analysis."
        )

    working = df.copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working = working.dropna(subset=["Date"])
    if working.empty:
        return "No valid dates found in the database."

    working = working.sort_values("Date")

    def _extract(pattern: str, text: str) -> str | None:
        if not isinstance(text, str) or not text.strip():
            return None
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if not match:
            return None
        value = match.group(1).strip()
        return value if value else None

    def _extract_int(pattern: str, text: str) -> int | None:
        value = _extract(pattern, text)
        if value is None:
            return None
        m = re.search(r"\d+", value)
        if not m:
            return None
        try:
            return int(m.group(0))
        except ValueError:
            return None

    analysis_text = working["Analysis"].astype(str)
    working["Sentiment"] = analysis_text.apply(
        lambda t: _extract(r"\*\*Sentiment:\*\*\s*([^\n\r]+)", t)
    )
    working["Category"] = analysis_text.apply(
        lambda t: _extract(r"\*\*Category:\*\*\s*([^\n\r]+)", t)
    )
    working["Escalation Risk (%)"] = analysis_text.apply(
        lambda t: _extract_int(r"\*\*Escalation\s*Risk:\*\*\s*([^\n\r]+)", t)
    )

    total_calls = len(working)
    date_min = working["Date"].min().date()
    date_max = working["Date"].max().date()

    sentiment_counts = (
        working["Sentiment"].fillna("Unknown").str.strip().value_counts(dropna=False)
    )
    category_counts = (
        working["Category"].fillna("Unknown").str.strip().value_counts(dropna=False)
    )

    risk_series = pd.to_numeric(working["Escalation Risk (%)"], errors="coerce")
    avg_risk = float(risk_series.dropna().mean()) if risk_series.notna().any() else None
    median_risk = float(risk_series.dropna().median()) if risk_series.notna().any() else None
    high_risk = int((risk_series >= 70).sum()) if risk_series.notna().any() else 0

    recent = working.tail(10).copy()
    recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d %H:%M")
    recent_cols = ["Date", "File Name", "Sentiment", "Escalation Risk (%)", "Category"]
    recent_table = recent[recent_cols].to_string(index=False)

    lines: list[str] = []
    lines.append(f"Total Calls: {total_calls}")
    lines.append(f"Date Range: {date_min} to {date_max}")
    lines.append("")
    lines.append("Sentiment (all calls):")
    for k, v in sentiment_counts.items():
        lines.append(f"- {k}: {int(v)}")
    lines.append("")
    lines.append("Top Categories (all calls):")
    for k, v in category_counts.head(8).items():
        lines.append(f"- {k}: {int(v)}")
    lines.append("")
    if avg_risk is not None:
        lines.append(
            f"Escalation Risk (%): avg={avg_risk:.1f}, median={median_risk:.1f}, high(>=70)={high_risk}"
        )
    else:
        lines.append("Escalation Risk (%): Not available (could not parse from Analysis)")
    lines.append("")
    lines.append("Most Recent 10 Calls:")
    lines.append(recent_table)
    lines.append("")
    lines.append(
        "Instruction: Base insights strictly on the counts/table above. Do not invent totals." 
        "If a field is Unknown, treat it as missing data."
    )

    return "\n".join(lines)
