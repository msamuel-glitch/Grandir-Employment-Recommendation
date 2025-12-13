import sqlite3
import re
import os
import time
from geopy.geocoders import Nominatim

def fix_map_final():
    print("🌍 Starting Map Fixer...")
    
    kml_file = "nurseries.kml"
    if not os.path.exists(kml_file):
        print(f"❌ Error: Could not find '{kml_file}' in this folder.")
        return

    # 1. READ KML ADDRESSES
    kml_data = []
    with open(kml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to capture Name and Address blocks from KML
    placemarks = re.findall(r"<Placemark>.*?</Placemark>", content, re.DOTALL)
    
    for p in placemarks:
        name_match = re.search(r"<name>(.*?)</name>", p)
        addr_match = re.search(r"<address>(.*?)</address>", p)
        
        if name_match and addr_match:
            # We normalize the name to match DB (lowercase, remove 'dsp', etc)
            raw_name = name_match.group(1).strip().lower().replace("dsp", "").replace("aix", "").strip()
            kml_data.append({
                'clean_name': raw_name,
                'address': addr_match.group(1).strip()
            })
    
    print(f"✅ Loaded {len(kml_data)} addresses from KML.")

    # 2. CONNECT TO DATABASE
    conn = sqlite3.connect("grandir_system.db")
    cursor = conn.cursor()
    
    # Get nurseries that have no location
    cursor.execute("SELECT id, name FROM nurseries WHERE latitude IS NULL OR latitude = 0")
    db_nurseries = cursor.fetchall()
    
    print(f"🎯 Attempting to locate {len(db_nurseries)} nurseries...")

    geolocator = Nominatim(user_agent="grandir_final_fix_v3")
    success_count = 0

    for nursery_id, db_name in db_nurseries:
        # Normalize DB name
        db_clean = db_name.lower().replace("dsp", "").replace("aix", "").strip()
        
        # Find best match in KML
        best_address = None
        for kml in kml_data:
            # Simple substring match
            if kml['clean_name'] in db_clean or db_clean in kml['clean_name']:
                best_address = kml['address']
                break
        
        if best_address:
            try:
                location = geolocator.geocode(best_address, timeout=5)
                if location:
                    cursor.execute("UPDATE nurseries SET latitude = ?, longitude = ? WHERE id = ?", 
                                 (location.latitude, location.longitude, nursery_id))
                    success_count += 1
                    print(f"📍 Fixed: {db_name}")
                time.sleep(1) # Respect API limits
            except:
                pass

    conn.commit()
    conn.close()
    print(f"🚀 MAP FIXED: {success_count} nurseries updated.")

if __name__ == "__main__":
    fix_map_final()