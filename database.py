import sqlite3

class GrandirDatabase:
    def __init__(self, db_path="grandir_system.db"):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        return conn

    # --- CANDIDATES ---
    def get_all_candidates(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        # We fetch the real status we generated (qualified_vip, etc.)
        cursor.execute("SELECT id, name, city, zip_code, qualification_level, status FROM candidates LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        candidates = []
        for row in rows:
            candidates.append({
                'ref': str(row['id']),
                'ville': row['city'],
                'postal_code': row['zip_code'],
                'diplomas': row['qualification_level'],
                'status': row['status'],
                'cat1': 'CAT 1' in str(row['qualification_level']).upper()
            })
        return candidates

    # --- JOBS (Linked to Nurseries) ---
    def get_all_jobs(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Join Jobs with Nurseries to get Urgency
        cursor.execute("""
            SELECT j.id, j.title, j.location, j.cat_requirement, n.name as nursery, n.urgency_level
            FROM jobs j
            JOIN nurseries n ON j.nursery_id = n.id
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        jobs = []
        for row in rows:
            jobs.append({
                'id': row['id'],
                'title': row['title'],
                'location': row['location'],
                'creche': row['nursery'],
                'urgency': row['urgency_level'],
                'matches': [] # Placeholder for now
            })
        return jobs

    # --- STATS ---
    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Red Alert Count
        cursor.execute("SELECT COUNT(*) FROM nurseries WHERE urgency_level LIKE '%Red%' OR urgency_level LIKE '%Rouge%'")
        red_count = cursor.fetchone()[0]

        # Candidate Breakdown
        cursor.execute("SELECT status, COUNT(*) FROM candidates GROUP BY status")
        rows = cursor.fetchall()
        cand_stats = {row['status']: row[1] for row in rows}
        conn.close()

        return {
            'red_alert_count': red_count,
            'vip_candidates': cand_stats.get('qualified_vip', 0),
            'rejected_candidates': cand_stats.get('rejected', 0),
            'total_candidates': sum(cand_stats.values())
        }