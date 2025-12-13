import sqlite3
import pandas as pd

def inspect_database():
    print("🔎 GRANDIR SYSTEM INSPECTION REPORT")
    print("=" * 40)
    
    conn = sqlite3.connect("grandir_system.db")
    cursor = conn.cursor()

    # --- CHECK 1: CANDIDATE STATUS COUNTS ---
    print("\n📊 CANDIDATE SCREENING RESULTS:")
    print("-" * 30)
    try:
        cursor.execute("SELECT status, COUNT(*) FROM candidates GROUP BY status")
        results = cursor.fetchall()
        for status, count in results:
            # Add emojis for readability
            icon = "❓"
            if status == 'rejected': icon = "⛔"
            elif status == 'qualified_vip': icon = "💎"
            elif status == 'qualified_standard': icon = "✅"
            elif status == 'qualified_hold': icon = "⚠️"
            elif status == 'new': icon = "🆕"
            
            print(f"{icon} {status.ljust(20)}: {count}")
    except Exception as e:
        print(f"❌ Error reading candidates: {e}")

    # --- CHECK 2: TOTAL MATCHES FOUND ---
    print("\n🔗 MATCHING ENGINE RESULTS:")
    print("-" * 30)
    try:
        cursor.execute("SELECT COUNT(*) FROM matches")
        match_count = cursor.fetchone()[0]
        print(f"Total Matches Created: {match_count}")
        
        # Breakdown by Urgency
        cursor.execute("""
            SELECT n.urgency_level, COUNT(*) 
            FROM matches m 
            JOIN jobs j ON m.job_id = j.id 
            JOIN nurseries n ON j.nursery_id = n.id 
            GROUP BY n.urgency_level
        """)
        urgency_counts = cursor.fetchall()
        for level, count in urgency_counts:
            print(f"   -> Matches for {level} Nurseries: {count}")
            
    except Exception as e:
        print(f"❌ Error reading matches: {e}")

    # --- CHECK 3: SPOT CHECK (Audit a VIP) ---
    print("\n🕵️ VIP AUDIT (Sample Check):")
    print("-" * 30)
    try:
        # Find one VIP candidate and show why they are VIP
        cursor.execute("""
            SELECT c.id, c.name, c.qualification_level, c.zip_code, n.name, n.urgency_level 
            FROM candidates c
            JOIN matches m ON c.id = m.candidate_id
            JOIN jobs j ON m.job_id = j.id
            JOIN nurseries n ON j.nursery_id = n.id
            WHERE c.status = 'qualified_vip'
            LIMIT 1
        """)
        vip = cursor.fetchone()
        
        if vip:
            print(f"Candidate: {vip[1]} (ID: {vip[0]})")
            print(f"Quals:     {vip[2]}")
            print(f"Location:  {vip[3]}")
            print(f"Matched:   {vip[4]}")
            print(f"Reason:    Urgency is '{vip[5]}' (Should be Red/Rouge)")
        else:
            print("⚠️ No VIP candidates found. Check your 'Red' nursery logic.")
            
    except Exception as e:
        print(f"❌ Error auditing VIP: {e}")

    conn.close()
    print("\n" + "=" * 40)
    print("End of Report")

if __name__ == "__main__":
    inspect_database()