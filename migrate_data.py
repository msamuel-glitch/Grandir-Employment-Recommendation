import sqlite3
import pandas as pd

def move_candidates_with_location():
    print("🚚 Moving Candidates (Version 2: With Location Data)...")

    connection = sqlite3.connect("grandir_system.db")
    cursor = connection.cursor()

    # 1. Reset Table to add new columns
    cursor.execute("DROP TABLE IF EXISTS candidates")
    cursor.execute("""
    CREATE TABLE candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        qualification_level TEXT,
        source TEXT,
        city TEXT,          -- NEW: Needed for matching
        zip_code TEXT,      -- NEW: Needed for matching
        status TEXT DEFAULT 'new'
    )
    """)

    # 2. Read Excel
    file_path = r"C:\Users\Hp\OneDrive - Université Paris Sciences et Lettres\Borris\Desktop\Course B1\BDD\Grandir\Dashboard\Back end\db\candidates.xls"
    try:
        excel_data = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    count = 0
    for index, row in excel_data.iterrows():
        # ... (Existing Name/Email logic) ...
        first_name = str(row.get("Prénom", "")).strip()
        last_name = str(row.get("Nom", "")).strip()
        full_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Unknown"
        email = str(row.get("Email", "")).strip()
        qualification = str(row.get("Métiers", "Inconnu")).strip()
        
        # Source
        source = "Excel"
        for col in excel_data.columns:
            if str(col).startswith("Provenanc"):
                source = str(row.get(col, "Excel")).strip()
                break
        
        # Phone
        phone = ""
        for col in excel_data.columns:
            if str(col).startswith("Numéro de"):
                phone = str(row.get(col, "")).strip()
                break

        # --- NEW: LOCATION DATA ---
        city = str(row.get("Ville du candidat", "")).strip()
        zip_code = str(row.get("Code postal du candidat", "")).strip()
        if zip_code.endswith(".0"): zip_code = zip_code[:-2] # Fix Excel formatting (75001.0 -> 75001)

        cursor.execute("""
            INSERT INTO candidates (name, phone, email, qualification_level, source, city, zip_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (full_name, phone, email, qualification, source, city, zip_code))
        
        count += 1

    connection.commit()
    connection.close()
    print(f"✅ Re-imported {count} candidates WITH location data.")

if __name__ == "__main__":
    move_candidates_with_location()