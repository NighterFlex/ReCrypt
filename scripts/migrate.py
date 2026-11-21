
import json
import sqlite3
import hashlib
import secrets
import os

from pathlib import Path
from datetime import datetime, timezone

from Crypto.Cipher import DES, AES
from Crypto.Util.Padding import unpad


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

ARCHIVE_DIR = BASE_DIR / "archive" / "legacy_records"
OUTPUT_DIR = BASE_DIR / "migrated" / "aes_records"
SECRET_DIR = BASE_DIR / "secrets"
DATABASE = BASE_DIR / "data" / "provenance.db"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SECRET_DIR.mkdir(parents=True, exist_ok=True)
DATABASE.parent.mkdir(parents=True, exist_ok=True)


# Load the old DES key
with open(SECRET_DIR / "des_key.bin", "rb") as file:
    des_key = file.read()

if len(des_key) != 8:
    raise ValueError("Invalid DES key. Expected 8 bytes.")


# Create an AES-256 key if one does not already exist
AES_KEY_FILE = SECRET_DIR / "aes_key.bin"

if not AES_KEY_FILE.exists():
    with open(AES_KEY_FILE, "wb") as file:
        file.write(secrets.token_bytes(32))

with open(AES_KEY_FILE, "rb") as file:
    aes_key = file.read()

if len(aes_key) != 32:
    raise ValueError("Invalid AES key. Expected 32 bytes.")


# Connect to SQLite and create the ledger
connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS migration_ledger (
    record_id TEXT PRIMARY KEY,
    source_file TEXT,
    output_file TEXT,
    original_sha256 TEXT,
    status TEXT,
    message TEXT,
    migrated_at TEXT
)
""")

connection.commit()


def update_ledger(record_id, source, output, status,
                  original_hash=None, message=""):

    cursor.execute("""
    INSERT INTO migration_ledger (
        record_id, source_file, output_file,
        original_sha256, status, message, migrated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)

    ON CONFLICT(record_id) DO UPDATE SET
        source_file = excluded.source_file,
        output_file = excluded.output_file,
        original_sha256 = excluded.original_sha256,
        status = excluded.status,
        message = excluded.message,
        migrated_at = excluded.migrated_at
    """, (
        record_id,
        str(source),
        str(output),
        original_hash,
        status,
        message,
        datetime.now(timezone.utc).isoformat()
    ))

    connection.commit()


# Process every legacy record
legacy_files = sorted(ARCHIVE_DIR.glob("*.json"))

if not legacy_files:
    print("No legacy records found.")
else:
    for source_file in legacy_files:

        record_id = source_file.stem
        output_file = OUTPUT_DIR / f"{record_id}.json"

        # Skip records already verified
        cursor.execute(
            "SELECT status FROM migration_ledger WHERE record_id = ?",
            (record_id,)
        )

        existing = cursor.fetchone()

        if existing and existing[0] == "VERIFIED":
            print(f"{record_id}: Already verified. Skipping.")
            continue

        try:
            update_ledger(
                record_id, source_file, output_file,
                "MIGRATING", message="Migration started."
            )

            # Read the legacy record
            with open(source_file, "r") as file:
                legacy = json.load(file)

            iv = bytes.fromhex(legacy["iv"])
            ciphertext = bytes.fromhex(legacy["ciphertext"])

            # Decrypt DES record
            des_cipher = DES.new(des_key, DES.MODE_CBC, iv)
            plaintext = unpad(
                des_cipher.decrypt(ciphertext),
                DES.block_size
            )

            # Calculate original SHA-256 hash
            original_hash = hashlib.sha256(plaintext).hexdigest()

            # Encrypt using AES-256-GCM
            nonce = secrets.token_bytes(12)

            aes_cipher = AES.new(
                aes_key,
                AES.MODE_GCM,
                nonce=nonce
            )

            encrypted_data, tag = aes_cipher.encrypt_and_digest(plaintext)

            migrated_record = {
                "id": record_id,
                "nonce": nonce.hex(),
                "ciphertext": encrypted_data.hex(),
                "tag": tag.hex(),
                "sha256": original_hash
            }

            # Save migrated record safely
            temp_file = output_file.with_suffix(".tmp")

            with open(temp_file, "w") as file:
                json.dump(migrated_record, file, indent=4)

            os.replace(temp_file, output_file)

            # Verify AES authentication
            with open(output_file, "r") as file:
                saved_record = json.load(file)

            verify_cipher = AES.new(
                aes_key,
                AES.MODE_GCM,
                nonce=bytes.fromhex(saved_record["nonce"])
            )

            recovered_data = verify_cipher.decrypt_and_verify(
                bytes.fromhex(saved_record["ciphertext"]),
                bytes.fromhex(saved_record["tag"])
            )

            # Compare SHA-256 hashes
            recovered_hash = hashlib.sha256(
                recovered_data
            ).hexdigest()

            if recovered_hash != original_hash:
                raise ValueError("SHA-256 verification failed.")

            # Mark record as verified
            update_ledger(
                record_id,
                source_file,
                output_file,
                "VERIFIED",
                original_hash,
                "AES-GCM and SHA-256 verification successful."
            )

            print(f"{record_id}: Migration successful!")

        except Exception as error:

            update_ledger(
                record_id,
                source_file,
                output_file,
                "FAILED",
                message=str(error)
            )

            print(f"{record_id}: Migration failed: {error}")


connection.close()

print("\nMigration process completed.")
