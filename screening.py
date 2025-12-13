import sqlite3
import re

# Simple distance approximation (Exact geocoding requires external API, using ZIP prefix for now)
def is_location_match(cand_zip, job_location):
    # Simple check: Does the job location string contain the candidate's department (first 2 digits of zip)?
    if not cand_zip or len(cand_zip) < 2: return False
    dept = cand_zip[:2]
    return dept in job_location

def run_screening_and_matching():
    print("🕵️ Starting Screening & Matching Process...")
    
    conn = sqlite3.connect("grandir_system.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Ensure Matches Table Exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        job_id INTEGER,
        match_score INTEGER,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id),
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    """)

    # 2. Get Candidates & Jobs
    cursor.execute("SELECT * FROM candidates WHERE status = 'new'")
    candidates = cursor.fetchall()
    
    cursor.execute("""
        SELECT j.id, j.cat_requirement, j.location, n.urgency_level 
        FROM jobs j 
        JOIN nurseries n ON j.nursery_id = n.id
    """)
    jobs = cursor.fetchall()

    print(f"📊 Processing {len(candidates)} candidates against {len(jobs)} jobs...")

    for cand in candidates:
        cand_id = cand['id']
        qual = str(cand['qualification_level']).lower()
        
        # --- GATE 1: QUALIFICATION ---
        has_cat1 = "cap" in qual or "aepe" in qual
        has_cat2 = "auxiliaire" in qual or "eje" in qual or "infirmier" in qual
        
        new_status = "rejected"
        action = "SMS_REJECTION"

        if has_cat1 or has_cat2:
            # They are qualified! Now check for matches.
            is_vip = False
            match_found = False

            for job in jobs:
                # Basic Matching Logic
                job_cat = str(job['cat_requirement']).upper()
                
                # Check Qualification Match
                qual_match = False
                if "CAT 1" in job_cat and has_cat1: qual_match = True
                elif "CAT 2" in job_cat and (has_cat1 or has_cat2): qual_match = True # Relaxed rule
                elif "CAT 1" not in job_cat and "CAT 2" not in job_cat: qual_match = True # No specific req

                if qual_match:
                    # Check Location Match (using Zip/Dept logic)
                    if is_location_match(cand['zip_code'], str(job['location'])):
                        match_found = True
                        
                        # Save to Matches Table
                        cursor.execute("INSERT INTO matches (candidate_id, job_id, match_score) VALUES (?, ?, ?)", 
                                     (cand_id, job['id'], 100))
                        
                        # Check VIP (Red Urgency)
                        if "Red" in job['urgency_level'] or "Rouge" in job['urgency_level']:
                            is_vip = True
            
            # --- GATE 2: STATUS ASSIGNMENT ---
            if is_vip:
                new_status = "qualified_vip"
                action = "SMS_URGENT_CONGRATS"
            elif match_found:
                new_status = "qualified_standard"
                action = "SMS_BOOKING"
            else:
                # Qualified but no jobs near them
                new_status = "qualified_hold" 
                action = "WAITLIST"

        # Update Candidate Status
        cursor.execute("UPDATE candidates SET status = ? WHERE id = ?", (new_status, cand_id))

    conn.commit()
    conn.close()
    print("✅ Screening Complete! Database updated.")

if __name__ == "__main__":
    run_screening_and_matching()