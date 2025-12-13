import sqlite3
import re
import os
import time
from geopy.geocoders import Nominatim

def normalize(text):
    # Cleans names to help finding matches (e.g. "AIX DSP AGORA" == "AGORA")
    if not text: return set()
    noise = r"\b(dsp|creche|crèche|les|le|la|de|du|des|et|&|aix|paris|lyon|bordeaux|micro|l|d)\b"
    text = text.lower()
    text = re.sub(noise, "", text)
    text = re.sub(r"[^a-z0-9]", " ", text)
    return set([w for w in text.split() if len(w) >= 3])

def fix_map_final():
    print("🌍 Starting Address-Based Map Fix...")
    
    kml_file = "nurseries.kml"
    if not os.path.exists(kml_file):
        print("❌ Error: nurseries.kml not found.")
        return

    # 1. READ KML & EXTRACT ADDRESSES
    print("📂 Reading Addresses from KML...")
    kml_data = []
    with open(kml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to capture Name and Address blocks
    # We use a pattern that looks for <name> then captures until </Placemark> to find the address
    placemarks = re.findall(r"<Placemark>.*?</Placemark>", content, re.DOTALL)
    
    for p in placemarks:
        name_match = re.search(r"<name>(.*?)</name>", p)
        addr_match = re.search(r"<address>(.*?)</address>", p)
        
        if name_match and addr_match:
            kml_data.append({
                'name': name_match.group(1).strip(),
                'tokens': normalize(name_match.group(1)),
                'address': addr_match.group(1).strip()
            })
    
    print(f"✅ Found {len(kml_data)} addresses in KML.")

    # 2. CONNECT TO DATABASE
    conn = sqlite3.connect("grandir_system.db")
    cursor = conn.cursor()
    
    # Ensure columns exist
    try:
        cursor.execute("ALTER TABLE nurseries ADD COLUMN latitude REAL")
        cursor.execute("ALTER TABLE nurseries ADD COLUMN longitude REAL")
    except: pass

    cursor.execute("SELECT id, name FROM nurseries WHERE latitude IS NULL OR latitude = 0")
    db_nurseries = cursor.fetchall()
    
    print(f"🎯 Trying to locate {len(db_nurseries)} nurseries from DB...")

    # 3. MATCH & GEOCODE
    geolocator = Nominatim(user_agent="grandir_final_fix_v2")
    success_count = 0

    for nursery_id, db_name in db_nurseries:
        db_tokens = normalize(db_name)
        if not db_tokens: continue

        # A. Find the matching KML entry
        best_match = None
        best_score = 0

        for kml in kml_data:
            common = db_tokens.intersection(kml['tokens'])
            if len(common) > best_score:
                best_score = len(common)
                best_match = kml
        
        # B. If we found a match, Geocode the ADDRESS
        if best_match and best_score > 0:
            try:
                # print(f"   🔎 Geocoding: {best_match['address']}")
                location = geolocator.geocode(best_match['address'], timeout=5)
                
                if location:
                    cursor.execute("UPDATE nurseries SET latitude = ?, longitude = ? WHERE id = ?", 
                                 (location.latitude, location.longitude, nursery_id))
                    success_count += 1
                    print(f"✅ Fixed: {db_name} ({location.latitude}, {location.longitude})")
                else:
                    print(f"⚠️ Address not found: {best_match['address']}")
                
                # Respect API limits (important!)
                time.sleep(1.1) 

            except Exception as e:
                print(f"❌ Error: {e}")

    conn.commit()
    conn.close()
    print("-" * 40)
    print(f"🚀 FINAL SUCCESS: {success_count} nurseries located on the map!")
    print("-" * 40)

if __name__ == "__main__":
    fix_map_final()