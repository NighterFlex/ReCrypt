# 🔐 ReCrypt
### Legacy Archive Migration & Provenance Tracking System

ReCrypt is a Python-based application that migrates legacy DES-encrypted records to modern AES-256-GCM encryption. It also tracks the migration process using a SQLite provenance ledger and verifies migrated records to ensure their integrity.

The project uses 20 fictional records to demonstrate secure archive migration.

## ✨ Features

- **Legacy Archive Generation:** Creates 20 fictional records encrypted with DES-CBC.
- **Modern Encryption:** Migrates records to AES-256-GCM.
- **Integrity Verification:** Uses AES-GCM authentication and SHA-256 hash comparison.
- **Provenance Tracking:** Stores record origin, migration status, verification results, and timestamps in SQLite.
- **Recovery Support:** Identifies unfinished records and retries failed migrations.
- **Interactive Dashboard:** Provides a Streamlit interface to manage migration and view results.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.14 | Main programming language |
| Streamlit | User interface |
| PyCryptodome | DES and AES encryption |
| SQLite | Provenance ledger |
| Pandas | Displaying migration records |
| SHA-256 | Data integrity checking |

## 📁 Project Structure

```text
ReCrypt/
│
├── archive/
│   └── legacy_records/
│
├── migrated/
│   └── aes_records/
│
├── data/
│   └── provenance.db
│
├── secrets/
│   ├── des_key.bin
│   └── aes_key.bin
│
├── scripts/
│   ├── generate_archive.py
│   ├── migrate.py
│   ├── verify.py
│   └── test_recovery.py
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone https://github.com/NighterFlex/ReCrypt.git
cd ReCrypt
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the environment**

Windows:

```bash
venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

## 🚀 Running the Project

**Step 1: Generate the legacy archive**

```bash
python scripts/generate_archive.py
```

This creates 20 fictional records encrypted using DES-CBC and generates the DES key.

**Step 2: Migrate the records**

```bash
python scripts/migrate.py
```

The script decrypts the legacy records, calculates their SHA-256 hashes, encrypts them using AES-256-GCM, and records the results in SQLite.

**Step 3: Verify migrated records**

```bash
python scripts/verify.py
```

This checks AES-GCM authentication and compares the recovered data hashes with the values stored in the provenance ledger.

**Step 4: Launch the dashboard**

```bash
streamlit run app.py
```

The dashboard allows users to start migrations, retry unfinished records, verify records, and view the provenance ledger.

## 🧪 Testing

ReCrypt includes the following test cases:

| Test ID | Test Case | Expected Result |
|---|---|---|
| T01 | Legacy Archive Generation | 20 encrypted records are created. |
| T02 | Successful Migration | All records are migrated and verified. |
| T03 | Independent Verification | All migrated records pass verification. |
| T04 | Duplicate Migration | Previously verified records are skipped. |
| T05 | Interrupted Migration Recovery | Unfinished records are retried. |
| T06 | Invalid and Corrupted Input | Invalid records are detected and marked as failed. |

## 🔒 Security Considerations

- DES is used only to simulate a legacy encryption system. It is not suitable for protecting real sensitive information.
- AES-256-GCM provides encryption and authentication.
- A unique nonce is generated for each AES-GCM encryption.
- SHA-256 is used to compare original and recovered data.
- Encryption keys are stored separately from the encrypted records.
- The original DES archive is preserved for recovery and rollback.
- Only fictional records are used. No real personal information is processed.

**Important:** Never upload encryption keys or other secret files to GitHub.

## 🎯 Project Objective

The main objective of ReCrypt is to demonstrate how legacy encrypted archives can be migrated to modern encryption while maintaining record integrity, tracking migration history, and supporting recovery from interrupted operations.

---

**ReCrypt** | Legacy Archive Migration & Provenance Ledger

*Academic Information Security Project*
