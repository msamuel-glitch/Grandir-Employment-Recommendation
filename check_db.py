import sqlite3

def peek_inside_drawer():
    print("👀 Peeking inside the Filing Cabinet...")

    # 1. Open the cabinet
    connection = sqlite3.connect("grandir_system.db")
    cursor = connection.cursor()

    # 2. Grab the first 5 people
    # "SELECT *" means "Give me everything"
    # "LIMIT 5" means "Stop after 5 people"
    cursor.execute("SELECT * FROM candidates LIMIT 5")
    rows = cursor.fetchall()

    # 3. Print them out nicely
    print(f"found {len(rows)} people. Here are the first few:")
    print("-" * 50)
    for person in rows:
        # person is a list like (1, "Jean Dupont", "061234...", ...)
        print(f"Ticket #{person[0]}: {person[1]}") 
        print(f"   📞 Phone: {person[2]}")
        print(f"   📧 Email: {person[3]}")
        print(f"   🎓 Job/Qual: {person[4]}")
        print("-" * 50)

    connection.close()

if __name__ == "__main__":
    peek_inside_drawer()