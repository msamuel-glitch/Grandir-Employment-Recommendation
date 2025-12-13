from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os

# --- DATABASE HELPER CLASS ---
class GrandirDatabase:
    def __init__(self, db_path="grandir_system.db"):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_stats(self):
        """Calculates REAL stats from the 42k candidates and 300+ nurseries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Real Urgency Counts
        cursor.execute("SELECT urgency_level, COUNT(*) FROM nurseries GROUP BY urgency_level")
        urgency_rows = cursor.fetchall()
        urgency_counts = {'Red': 0, 'Orange': 0, 'Verte': 0}
        
        for row in urgency_rows:
            label = str(row[0]).lower()
            if 'red' in label or 'rouge' in label: urgency_counts['Red'] += row[1]
            elif 'orange' in label: urgency_counts['Orange'] += row[1]
            else: urgency_counts['Verte'] += row[1]

        # 2. Real Candidate Funnel
        cursor.execute("SELECT status, COUNT(*) FROM candidates GROUP BY status")
        status_rows = cursor.fetchall()
        cand_stats = {row['status']: row[1] for row in status_rows}

        # 3. Real Qualification Split
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN qualification_level LIKE '%Auxiliaire%' OR qualification_level LIKE '%EJE%' THEN 1 ELSE 0 END) as cat1,
                SUM(CASE WHEN qualification_level LIKE '%CAP%' OR qualification_level LIKE '%AEPE%' THEN 1 ELSE 0 END) as cat2
            FROM candidates
        """)
        qual_row = cursor.fetchone()
        
        conn.close()

        return {
            'red_alert_count': urgency_counts['Red'],
            'orange_alert_count': urgency_counts['Orange'],
            'green_count': urgency_counts['Verte'],
            'vip_candidates': cand_stats.get('qualified_vip', 0),
            'rejected_candidates': cand_stats.get('rejected', 0),
            'total_candidates': sum(cand_stats.values()),
            'cat1Qualified': qual_row['cat1'] or 0,
            'cat2Qualified': qual_row['cat2'] or 0
        }

    def get_all_jobs(self, limit=1000):
        """Fetches jobs and applies the 'Leslie Protocol' logic"""
        conn = self.get_connection()
        cursor = conn.cursor()
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
            urgency = str(row['urgency_level'])
            cat_req = str(row['cat_requirement'] or '')
            title = str(row['title']).upper()

            # --- THE LESLIE PROTOCOL (HQ Logic) ---
            # Rule: RED nurseries OR (ORANGE nurseries AND CAT 1 jobs)
            is_red = 'Red' in urgency or 'Rouge' in urgency
            is_orange = 'Orange' in urgency
            is_cat1 = 'CAT 1' in cat_req.upper() or 'AUXILIAIRE' in title or 'EJE' in title or 'INFIRMIER' in title
            
            assigned_to = "Local Manager"
            if is_red or (is_orange and is_cat1):
                assigned_to = "Leslie (HQ)"

            jobs.append({
                'id': row['id'],
                'title': row['title'],
                'location': row['location'],
                'creche': row['nursery'],
                'urgency': row['urgency_level'],
                'owner': assigned_to,
                'cat_criteria': cat_req
            })
        return jobs

# --- FLASK SERVER ---
app = Flask(__name__)
CORS(app)
db = GrandirDatabase()

@app.route('/')
def home(): return "BloomPath System Online 🟢"

@app.route('/api/stats')
def get_stats(): return jsonify(db.get_stats())

@app.route('/api/matches')
def get_matches():
    # Returns jobs with the new 'owner' field
    return jsonify({'matches': db.get_all_jobs(limit=2000)})

@app.route('/api/candidates')
def get_candidates():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates LIMIT 100")
    rows = cursor.fetchall()
    conn.close()
    
    data = []
    for r in rows:
        # Map statuses to Grandir Workflow
        status = "A QUALIFIER"
        if r['status'] == 'rejected': status = "REJETÉ"
        elif r['status'] == 'qualified_vip': status = "ENTRETIEN RH (URGENT)"
        elif r['status'] == 'qualified_standard': status = "ECHANGE À PROGRAMMER"
            
        data.append({
            'ref': str(r['id']),
            'ville': r['city'],
            'postal_code': r['zip_code'],
            'diplomas': r['qualification_level'],
            'grandir_status': status,
            'cat1': 'CAT 1' in str(r['qualification_level']).upper()
        })
    return jsonify({'candidates': data})

@app.route('/api/nurseries')
def get_nurseries():
    # Returns only geolocated nurseries for the map
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, urgency_level, latitude, longitude FROM nurseries WHERE latitude IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return jsonify({'nurseries': [dict(row) for row in rows]})

@app.route('/api/messages')
def get_messages():
    # Returns simulated messages for the "Innovative Chat" UI
    # In production, this would query the 'message_logs' table
    return jsonify({'messages': [
        {"name": "Adama Barry", "phone": "+33612345678", "time": "2025-01-10T10:30:00", "body": "Félicitations ! Votre profil correspond à un poste urgent (BORDEAUX). Répondez OUI.", "type": "qualified_vip", "status": "unread"},
        {"name": "Jean Martin", "phone": "+33698765432", "time": "2025-01-10T09:15:00", "body": "Merci pour votre candidature. Malheureusement, nous recherchons des profils CAT1.", "type": "rejected", "status": "read"},
        {"name": "Sarah Connor", "phone": "+3365551234", "time": "2025-01-09T14:20:00", "body": "Entretien confirmé pour mardi 14h.", "type": "qualified_standard", "status": "read"}
    ]})

if __name__ == '__main__':
    # Get PORT from environment variable, default to 5000 if not found
    port = int(os.environ.get('PORT', 5000))
    # host='0.0.0.0' is crucial for cloud deployments
    app.run(host='0.0.0.0', port=port)