import sqlite3
import pandas as pd

def import_jobs_with_location():
    print("🚀 Importing Jobs (Version 2: With Location)...")

    connection = sqlite3.connect("grandir_system.db")
    cursor = connection.cursor()

    # Reset Tables
    cursor.execute("DROP TABLE IF EXISTS jobs")
    cursor.execute("DROP TABLE IF EXISTS nurseries")
    
    # Create Nurseries (Added Location)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nurseries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        urgency_level TEXT DEFAULT 'Verte'
    )
    """)
    
    # Create Jobs (Added Location column)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT UNIQUE,
        title TEXT,
        cat_requirement TEXT,
        location TEXT,       -- NEW: Needed for matching
        nursery_id INTEGER,
        FOREIGN KEY(nursery_id) REFERENCES nurseries(id)
    )
    """)

    file_path = r"C:\Users\Hp\OneDrive - Université Paris Sciences et Lettres\Borris\Desktop\Course B1\BDD\Grandir\Dashboard\Back end\db\jobs.xls"
    df = pd.read_excel(file_path, sheet_name="Liste des annonces", header=0)

    for index, row in df.iterrows():
        job_ref = str(row.get("Référence", "Unknown"))
        job_title = str(row.get("Titre de l'annonce", "Unknown"))
        cat_level = str(row.get("CAT", "Unknown"))
        nursery_name = str(row.get("CRECHES", "Unknown"))
        
        # --- NEW: LOCATION ---
        job_location = str(row.get("Localisation", "")).strip()

        # Urgency Logic
        raw_tag = ""
        for col in df.columns:
            if "Tags" in str(col): 
                raw_tag = str(row.get(col, "")).lower()
                break
        urgency = "Red" if "rouge" in raw_tag else "Orange" if "or" in raw_tag or "orange" in raw_tag else "Verte"

        if nursery_name in ["Unknown", "nan"]: continue

        # Handle Nursery
        cursor.execute("SELECT id, urgency_level FROM nurseries WHERE name = ?", (nursery_name,))
        result = cursor.fetchone()

        if result:
            nursery_id = result[0]
            # Update urgency if this job is more urgent
            if urgency == "Red" and result[1] != "Red":
                cursor.execute("UPDATE nurseries SET urgency_level = 'Red' WHERE id = ?", (nursery_id,))
        else:
            cursor.execute("INSERT INTO nurseries (name, urgency_level) VALUES (?, ?)", (nursery_name, urgency))
            nursery_id = cursor.lastrowid

        # Handle Job
        cursor.execute("SELECT id FROM jobs WHERE reference = ?", (job_ref,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO jobs (reference, title, cat_requirement, location, nursery_id)
                VALUES (?, ?, ?, ?, ?)
            """, (job_ref, job_title, cat_level, job_location, nursery_id))

    connection.commit()
    connection.close()
    print("✅ Jobs re-imported with location data.")

if __name__ == "__main__":
    import_jobs_with_location()