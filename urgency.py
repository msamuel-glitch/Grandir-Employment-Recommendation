import sqlite3

def check_store_inventory():
    print("📋 Checking the shelves for URGENT jobs...")
    
    connection = sqlite3.connect("grandir_system.db")
    cursor = connection.cursor()

    # Count how many of each color we have
    cursor.execute("SELECT urgency_level, COUNT(*) FROM nurseries GROUP BY urgency_level")
    counts = cursor.fetchall()

    print("\n📊 NURSERY STATUS REPORT:")
    print("-" * 30)
    for status, count in counts:
        # Add a little icon for visual feedback
        icon = "🔴" if "Red" in status else "🟠" if "Orange" in status else "🟢"
        print(f"{icon} {status}: {count} nurseries")
    print("-" * 30)

    # Show me 3 examples of RED nurseries to verify
    print("\n🔥 Examples of RED (Urgent) Nurseries:")
    cursor.execute("SELECT name FROM nurseries WHERE urgency_level = 'Red' LIMIT 3")
    reds = cursor.fetchall()
    for r in reds:
        print(f"   - {r[0]}")

    connection.close()

if __name__ == "__main__":
    check_store_inventory()