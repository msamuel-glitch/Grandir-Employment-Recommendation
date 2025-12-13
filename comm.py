import sqlite3
import datetime

# SMS TEMPLATES (From your Mind Map Logic)
TEMPLATES = {
    "rejected": "Bonjour {name}, malheureusement votre candidature ne correspond pas aux critères (Diplôme requis). Bonne continuation.",
    "qualified_vip": "Félicitations {name}! Votre profil correspond à une crèche URGENTE ({nursery}) près de chez vous. Répondez OUI pour un entretien immédiat!",
    "qualified_standard": "Bonjour {name}, votre profil a retenu notre attention. Cliquez ici pour réserver un créneau d'entretien : calendly.com/grandir",
    "qualified_hold": "Bonjour {name}, votre profil est validé ! Nous vous contacterons dès qu'un poste s'ouvre dans votre secteur."
}

def run_communication_cycle():
    print("📡 Starting Communication Engine...")
    
    conn = sqlite3.connect("grandir_system.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Create a Table to store the messages (The "Sent Items" folder)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS message_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        phone TEXT,
        message_type TEXT,
        message_body TEXT,
        sent_at DATETIME
    )
    """)

    # 2. Find Candidates who have been Screened but NOT contacted yet
    # We exclude 'new' (not screened) and those already contacted.
    cursor.execute("""
        SELECT * FROM candidates 
        WHERE status IN ('rejected', 'qualified_vip', 'qualified_standard', 'qualified_hold')
    """)
    candidates = cursor.fetchall()
    
    print(f"📨 Preparing messages for {len(candidates)} candidates...")
    
    messages_sent = 0

    for cand in candidates:
        status = cand['status']
        name = cand['name']
        phone = cand['phone']
        cand_id = cand['id']
        
        # Determine the nursery name for VIPs (Personalization)
        nursery_name = "Grandir"
        if status == 'qualified_vip':
            # Fetch the specific RED job they matched
            cursor.execute("""
                SELECT n.name FROM matches m 
                JOIN jobs j ON m.job_id = j.id 
                JOIN nurseries n ON j.nursery_id = n.id
                WHERE m.candidate_id = ? AND n.urgency_level LIKE '%Red%'
                LIMIT 1
            """, (cand_id,))
            result = cursor.fetchone()
            if result:
                nursery_name = result[0]

        # Generate the Message
        if status in TEMPLATES:
            msg_body = TEMPLATES[status].format(name=name, nursery=nursery_name)
            
            # 3. "Send" the message (Log it to DB)
            cursor.execute("""
                INSERT INTO message_logs (candidate_id, phone, message_type, message_body, sent_at)
                VALUES (?, ?, ?, ?, ?)
            """, (cand_id, phone, status, msg_body, datetime.datetime.now()))
            
            messages_sent += 1
            
            # Optional: Print the first 5 messages to the console so you can see them
            if messages_sent <= 5:
                print(f"\n[SIMULATION SMS] To: {phone} ({status})")
                print(f"   \"{msg_body}\"")

    conn.commit()
    conn.close()
    
    print("-" * 40)
    print(f"✅ COMMUNICATION CYCLE COMPLETE.")
    print(f"📝 Generated {messages_sent} SMS logs in the database.")
    print("-" * 40)

if __name__ == "__main__":
    run_communication_cycle()