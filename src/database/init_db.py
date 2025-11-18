import sqlite3
import os

    
def initialize_sqlite_file(db_file:str):
    # Set up the database path
    # addon_path = os.path.dirname(__file__)
    # db_dir = os.path.join(addon_path, "user_files", "db")
    # os.makedirs(db_dir, exist_ok=True)
    # db_file = os.path.join(db_dir, "dictionaries.sqlite")

    # Connect to the database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Create langnames table
    c.execute("""
    CREATE TABLE IF NOT EXISTS langnames (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        langname TEXT UNIQUE NOT NULL
    );
    """)

    # Create dictnames table
    c.execute("""
    CREATE TABLE IF NOT EXISTS dictnames (
        dictname TEXT UNIQUE NOT NULL,
        lid INTEGER NOT NULL,
        fields TEXT,
        addtype TEXT,
        termHeader TEXT,
        duplicateHeader INTEGER,
        FOREIGN KEY (lid) REFERENCES langnames(id)
    );
    """)

    # Create a sample dictionary table
    dict_table = "l1nameSampleDictionary"
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS {dict_table} (
        term CHAR(40) NOT NULL,
        altterm CHAR(40),
        pronunciation CHAR(100),
        pos CHAR(40),
        definition TEXT,
        examples TEXT,
        audio TEXT,
        frequency MEDIUMINT,
        starCount TEXT
    );
    """)
    c.execute(f"CREATE INDEX IF NOT EXISTS it{dict_table} ON {dict_table} (term);")
    c.execute(f"CREATE INDEX IF NOT EXISTS itp{dict_table} ON {dict_table} (term, pronunciation);")
    c.execute(f"CREATE INDEX IF NOT EXISTS ia{dict_table} ON {dict_table} (altterm);")
    c.execute(f"CREATE INDEX IF NOT EXISTS iap{dict_table} ON {dict_table} (altterm, pronunciation);")
    c.execute(f"CREATE INDEX IF NOT EXISTS ia{dict_table}_pron ON {dict_table} (pronunciation);")

    # Commit and close
    conn.commit()
    conn.close()
