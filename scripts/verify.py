
import json
import sqlite3
import hashlib

from pathlib import Path
from Crypto.Cipher import AES


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "migrated" / "aes_records"
SECRET_DIR = BASE_DIR / "secrets"
DATABASE = BASE_DIR / "data" / "provenance.db"


# Load AES key
with open(SECRET_DIR / "aes_key.bin", "rb") as file:
    aes_key = file.read()

if len(aes_key) != 32:
    raise ValueError("Invalid AES key.")


# Connect to provenance ledger
connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()


# Check every migrated record
files = sorted(OUTPUT_DIR.glob("*.json"))

if not files:
    print("No migrated records found.")

for file_path in files:

    record_id = file_path.stem

    try:
        # Read migrated record
        with open(file_path, "r") as file:
            record = json.load(file)

        nonce = bytes.fromhex(record["nonce"])
        ciphertext = bytes.fromhex(record["ciphertext"])
        tag = bytes.fromhex(record["tag"])

        # Verify AES-GCM authentication
        cipher = AES.new(
            aes_key,
            AES.MODE_GCM,
            nonce=nonce
        )

        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        # Calculate SHA-256 hash
        calculated_hash = hashlib.sha256(plaintext).hexdigest()

        # Get original hash from ledger
        cursor.execute("""
            SELECT original_sha256, status
            FROM migration_ledger
            WHERE record_id = ?
        """, (record_id,))

        result = cursor.fetchone()

        if result is None:
            print(f"{record_id}: NOT VERIFIED - Missing ledger entry.")
            continue

        original_hash, status = result

        # Compare hashes and ledger status
        if calculated_hash == original_hash and status == "VERIFIED":
            print(f"{record_id}: VALID")
        else:
            print(f"{record_id}: INVALID - Hash or status mismatch.")

    except Exception as error:
        print(f"{record_id}: INVALID - {error}")


connection.close()

print("\nVerification completed.")
