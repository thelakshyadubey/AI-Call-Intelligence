"""Database repository for call records (Excel storage)"""
import os
import re
from datetime import datetime

import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
EXCEL_FILE = os.path.join(PROJECT_ROOT, "call_records.xlsx")

CANONICAL_COLUMNS = ["Date", "File Name", "Transcript", "Analysis"]


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

def database_exists():
    """Check if database file exists"""
    return os.path.exists(EXCEL_FILE)

def get_all_records():
    """Load all call records from Excel"""
    if not database_exists():
        return pd.DataFrame()
    df = pd.read_excel(EXCEL_FILE)
    return _normalize_schema(df)

def get_record_count():
    """Get total number of records"""
    df = get_all_records()
    return len(df)

def prepare_trend_summary(df):
    """Prepare data summary for trend analysis"""
    if df.empty:
        return "No data available"

    expected_cols = {"Date", "File Name", "Analysis"}
    missing_cols = expected_cols - set(df.columns)
    if missing_cols:
        return (
            "The Excel database is missing required columns: "
            f"{', '.join(sorted(missing_cols))}. "
            "Expected columns: Date, File Name, Analysis."
        )

    working = df.copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working = working.dropna(subset=["Date"])
    if working.empty:
        return "No valid dates found in the Excel database."

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

def save_record(filename, transcript, analysis):
    """
    Save a new call record to Excel
    
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
            existing = _normalize_schema(pd.read_excel(EXCEL_FILE))
            updated = pd.concat([existing, new_record], ignore_index=True)
        else:
            updated = new_record

        updated = _normalize_schema(updated)
        updated["File Name"] = updated["File Name"].fillna("Unknown")
        
        # Save to Excel
        updated.to_excel(EXCEL_FILE, index=False)
        return True, None
        
    except PermissionError:
        return False, "Excel file is open! Close 'call_records.xlsx' and try again."
    except Exception as e:
        return False, str(e)
