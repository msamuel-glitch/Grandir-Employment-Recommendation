import re

def xray_kml():
    print("🩻 Starting KML X-Ray...")
    
    kml_file = "nurseries.kml"
    try:
        with open(kml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find the first Placemark block
        match = re.search(r"<Placemark>.*?</Placemark>", content, re.DOTALL)
        
        if match:
            print("\n--- 🔍 RAW DATA FOUND (First Block) ---")
            print(match.group(0)) # Print the whole chunk
            print("---------------------------------------")
            print("Please copy and paste the block above!")
        else:
            print("❌ No <Placemark> tags found. The data might be in <Folder> or <NetworkLink> tags.")
            
            # Fallback: Print the first 500 characters after "Folder"
            folder_match = re.search(r"<Folder>.*", content, re.DOTALL)
            if folder_match:
                print("\n--- 📂 FOLDER STRUCTURE DETECTED ---")
                print(folder_match.group(0)[:500])
            else:
                print("\n--- 📄 FILE HEAD (First 500 chars) ---")
                print(content[:500])

    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    xray_kml()