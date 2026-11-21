
import json
import os
import secrets
from pathlib import Path
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "archive" / "legacy_records"
SECRET_DIR = BASE_DIR / "secrets"

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
SECRET_DIR.mkdir(parents=True, exist_ok=True)

# Generate an 8-byte DES key
des_key = secrets.token_bytes(8)

# Save the key separately
with open(SECRET_DIR / "des_key.bin", "wb") as key_file:
    key_file.write(des_key)

# Create 20 fictional records
records = [
    {
        "id": f"REC-{i:03}",
        "name": f"User {i}",
        "email": f"user{i}@example.com",
        "department": ["IT", "HR", "Finance", "Sales"][i % 4]
    }
    for i in range(1, 21)
]

# Encrypt each record separately
for record in records:
    plaintext = json.dumps(record).encode("utf-8")

    # Generate a random 8-byte IV for DES-CBC
    iv = secrets.token_bytes(8)

    cipher = DES.new(des_key, DES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, DES.block_size))

    encrypted_record = {
        "id": record["id"],
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex()
    }

    output_file = ARCHIVE_DIR / f"{record['id']}.json"

    with open(output_file, "w") as file:
        json.dump(encrypted_record, file, indent=4)

print("Legacy archive generated successfully!")
print(f"Total records: {len(records)}")
print(f"Archive location: {ARCHIVE_DIR}")
