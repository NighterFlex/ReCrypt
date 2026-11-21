
import streamlit as st
import sqlite3
import pandas as pd
import subprocess
import sys

from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "data" / "provenance.db"
ARCHIVE_DIR = BASE_DIR / "archive" / "legacy_records"
MIGRATE_SCRIPT = BASE_DIR / "scripts" / "migrate.py"
VERIFY_SCRIPT = BASE_DIR / "scripts" / "verify.py"


# Page configuration
st.set_page_config(
    page_title="ReCrypt",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 ReCrypt")
st.subheader("Legacy Archive Migration System")

st.write(
    "Migrate legacy DES-encrypted records to "
    "AES-256-GCM and track their verification status."
)

st.divider()


# Run a Python script
def run_script(script_path):
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    return result


# Load records from the database
def load_records():

    if not DATABASE.exists():
        return pd.DataFrame()

    connection = sqlite3.connect(DATABASE)

    data = pd.read_sql_query(
        "SELECT * FROM migration_ledger",
        connection
    )

    connection.close()

    return data


# Count legacy records
legacy_files = list(ARCHIVE_DIR.glob("*.json"))
total_records = len(legacy_files)

records = load_records()

verified = 0
failed = 0
migrating = 0

if not records.empty:
    verified = len(records[records["status"] == "VERIFIED"])
    failed = len(records[records["status"] == "FAILED"])
    migrating = len(records[records["status"] == "MIGRATING"])

pending = max(0, total_records - verified - failed - migrating)


# Dashboard metrics
st.subheader("Archive Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", total_records)
col2.metric("Verified", verified)
col3.metric("Failed", failed)
col4.metric("Pending / In Progress", pending + migrating)

st.divider()


# Migration controls
st.subheader("Migration Controls")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Start / Retry Migration", use_container_width=True):

        with st.spinner("Migrating records..."):
            result = run_script(MIGRATE_SCRIPT)

        st.subheader("Migration Output")
        st.code(result.stdout)

        if result.returncode != 0:
            st.error(result.stderr or "Migration script failed.")
        else:
            st.success("Migration process finished.")


with col2:
    if st.button("🔍 Verify Records", use_container_width=True):

        with st.spinner("Verifying records..."):
            result = run_script(VERIFY_SCRIPT)

        st.subheader("Verification Output")
        st.code(result.stdout)

        if result.returncode != 0:
            st.error(result.stderr or "Verification script failed.")
        else:
            st.success("Verification process finished.")


st.divider()


# Display provenance ledger
st.subheader("Migration Provenance Ledger")

records = load_records()

if not records.empty:

    st.dataframe(
        records,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No migration records found yet.")


# Display records that have not entered the ledger
if total_records > 0:

    tracked_ids = set()

    if not records.empty:
        tracked_ids = set(records["record_id"])

    pending_ids = [
        file.stem for file in legacy_files
        if file.stem not in tracked_ids
    ]

    if pending_ids:
        st.subheader("Not Yet Processed")
        st.write(", ".join(pending_ids))


st.divider()

st.caption(
    "ReCrypt | DES to AES-256-GCM | "
    "SQLite Provenance Tracking"
)
