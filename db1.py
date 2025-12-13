import sqlite3  # This imports the tool we need to talk to the database

def create_the_filing_cabinet():
    # 1. Connect to the database
    # If the file "grandir_system.db" doesn't exist, this creates it!
    # This is our "Magical Filing Cabinet."
    connection = sqlite3.connect("grandir_system.db")
    
    # 2. Get a "cursor"
    # Think of the cursor as the robot arm that does the writing for us.
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # Drawer 1: The Candidates
    # We are creating a table (spreadsheet) to hold candidate info.
    # ---------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Each person gets a unique ticket number
        name TEXT,                             -- Their name (Text)
        phone TEXT,                            -- Their phone number
        email TEXT,                            -- Their email
        qualification_level TEXT,              -- Are they CAT1 or CAT2?
        source TEXT,                           -- Did they come from Indeed? LinkedIn?
        status TEXT DEFAULT 'new'              -- Are they 'new', 'qualified', or 'rejected'?
    )
    """)

    # ---------------------------------------------------------
    # Drawer 2: The Jobs (Nurseries)
    # This holds the open positions we need to fill.
    # ---------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,                            -- e.g., "Nursery Assistant"
        location TEXT,                         -- e.g., "Paris"
        urgency TEXT,                          -- e.g., "High", "Low"
        required_qualification TEXT            -- e.g., "CAT1"
    )
    """)

    # ---------------------------------------------------------
    # Drawer 3: The Matches
    # This links a Candidate to a Job.
    # ---------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,                  -- The ticket number of the person
        job_id INTEGER,                        -- The ticket number of the job
        match_score INTEGER,                   -- How good is the match? (0-100)
        FOREIGN KEY(candidate_id) REFERENCES candidates(id),
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    """)

    # 3. Save our changes
    connection.commit()
    
    # 4. Close the connection (Close the filing cabinet)
    connection.close()
    print("Success! The Grandir Filing Cabinet (Database) is built.")

# Run the function
create_the_filing_cabinet()