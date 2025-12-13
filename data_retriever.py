import sqlite3
import random
import time
from datetime import datetime

# --- PART 1: THE ROBOT SCOUTS (Simulated for now) ---

def scout_indeed():
    print("🕵️‍♀️ Scouting Indeed for new candidates...")
    # In the future, this will actually go to indeed.com
    # For now, we simulate finding a perfect candidate
    fake_candidates = [
        {"name": "Marie Curie", "job": "Auxiliaire de Puériculture", "location": "Paris"},
        {"name": "Louis Pasteur", "job": "Éducateur Jeunes Enfants", "location": "Lyon"},
    ]
    # Simulate thinking time
    time.sleep(1)
    return random.choice(fake_candidates)

def scout_linkedin():
    print("🕵️‍♀️ Scouting LinkedIn for new candidates...")
    # Simulate finding someone
    time.sleep(1)
    return {"name": "Sophie Germain", "job": "Directrice Crèche", "location": "Bordeaux"}

# --- PART 2: THE GATEKEEPER (Saves to Database) ---

def save_new_candidate(candidate_data, source_website):
    connection = sqlite3.connect("grandir_system.db")
    cursor = connection.cursor()

    # 1. Check if they already exist! (No duplicates allowed)
    # We check if someone with the same name exists
    cursor.execute("SELECT id FROM candidates WHERE name = ?", (candidate_data['name'],))
    existing = cursor.fetchone()

    if existing:
        print(f"⚠️ {candidate_data['name']} is already in our database! Skipping.")
    else:
        # 2. Insert the new person
        # We assume they are 'new' and give them a generic CAT2 level for now
        cursor.execute("""
            INSERT INTO candidates (name, qualification_level, source, status)
            VALUES (?, ?, ?, ?)
        """, (candidate_data['name'], candidate_data['job'], source_website, 'new'))
        
        print(f"✅ SUCCESS! Added {candidate_data['name']} from {source_website}.")
        connection.commit()

    connection.close()

# --- PART 3: THE MAIN LOOP ---
# This runs the whole factory

if __name__ == "__main__":
    print("🏭 Grandir Data Ingestion Engine Starting...")
    print("-" * 40)

    # 1. Check Indeed
    new_find = scout_indeed()
    save_new_candidate(new_find, "Indeed")

    # 2. Check LinkedIn
    new_find = scout_linkedin()
    save_new_candidate(new_find, "LinkedIn")

    print("-" * 40)
    print("😴 Scouts are sleeping now.")