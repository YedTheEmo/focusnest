#!/usr/bin/env python3
"""
FocusNest Database Initialization Script
This script creates the SQLite database and tables for FocusNest.
"""

import sqlite3
import os
from pathlib import Path

def create_database():
    """Create the SQLite database and tables."""
    
    # Create data directory if it doesn't exist
    data_dir = Path("../data")
    data_dir.mkdir(exist_ok=True)
    
    # Database path
    db_path = data_dir / "focusnest.db"
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create notes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create links table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_note INTEGER NOT NULL,
        to_note INTEGER NOT NULL,
        strength REAL DEFAULT 1.0,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (from_note) REFERENCES notes (id) ON DELETE CASCADE,
        FOREIGN KEY (to_note) REFERENCES notes (id) ON DELETE CASCADE,
        UNIQUE(from_note, to_note)
    )
    """)
    
    # Create tags table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER NOT NULL,
        tag_name TEXT NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
        UNIQUE(note_id, tag_name)
    )
    """)
    
    # Create metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER NOT NULL,
        key TEXT NOT NULL,
        value TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
        UNIQUE(note_id, key)
    )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_title ON notes (title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_created ON notes (created)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_from ON links (from_note)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_to ON links (to_note)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_note ON tags (note_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags (tag_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_note ON metadata (note_id)")
    
    # Insert sample data
    cursor.execute("""
    INSERT OR IGNORE INTO notes (id, title, content, created) VALUES 
    (1, 'Welcome to FocusNest', 
     'Welcome to your new knowledge management system!

This is your first note. You can:

- Create new notes by clicking the "New Note" button
- Link notes together using [[Note Title]] syntax
- Visualize your knowledge graph
- Search through all your notes

Try creating a link to [[My Second Note]] to see how linking works!

## Getting Started

1. **Creating Notes**: Use the "New Note" button or Ctrl+N
2. **Linking**: Use [[Note Title]] syntax to create connections
3. **Graph View**: Click the graph button to visualize connections
4. **Search**: Use the search bar to find notes quickly

Happy note-taking!', 
     datetime('now'))
    """)
    
    cursor.execute("""
    INSERT OR IGNORE INTO notes (id, title, content, created) VALUES 
    (2, 'My Second Note', 
     'This is your second note, linked from the [[Welcome to FocusNest]] note.

You can create bidirectional links between notes. When you reference [[Welcome to FocusNest]], it creates a connection that you can see in the graph view.

## Ideas to Try

- Create notes about your projects
- Link related concepts together
- Use tags with #hashtag syntax
- Build your personal knowledge graph

The more connections you create, the more powerful your knowledge system becomes!', 
     datetime('now'))
    """)
    
    cursor.execute("""
    INSERT OR IGNORE INTO notes (id, title, content, created) VALUES 
    (3, 'Knowledge Management Tips', 
     'Here are some tips for effective knowledge management with FocusNest:

## Best Practices

1. **Atomic Notes**: Keep each note focused on a single concept
2. **Descriptive Titles**: Use clear, searchable titles
3. **Regular Linking**: Connect related ideas with [[links]]
4. **Consistent Tagging**: Use #tags for categorization
5. **Regular Review**: Use the resurfacing feature to rediscover old notes

## Linking Strategies

- Link to [[My Second Note]] when discussing examples
- Reference [[Welcome to FocusNest]] for basic concepts
- Create hub notes that link to many related topics

Building a knowledge graph takes time, but the connections become incredibly valuable!', 
     datetime('now'))
    """)
    
    # Create some sample links
    cursor.execute("INSERT OR IGNORE INTO links (from_note, to_note, strength) VALUES (1, 2, 1.0)")
    cursor.execute("INSERT OR IGNORE INTO links (from_note, to_note, strength) VALUES (2, 1, 1.0)")
    cursor.execute("INSERT OR IGNORE INTO links (from_note, to_note, strength) VALUES (3, 1, 1.0)")
    cursor.execute("INSERT OR IGNORE INTO links (from_note, to_note, strength) VALUES (3, 2, 1.0)")
    
    # Create some sample tags
    cursor.execute("INSERT OR IGNORE INTO tags (note_id, tag_name) VALUES (1, 'welcome')")
    cursor.execute("INSERT OR IGNORE INTO tags (note_id, tag_name) VALUES (1, 'getting-started')")
    cursor.execute("INSERT OR IGNORE INTO tags (note_id, tag_name) VALUES (2, 'example')")
    cursor.execute("INSERT OR IGNORE INTO tags (note_id, tag_name) VALUES (3, 'tips')")
    cursor.execute("INSERT OR IGNORE INTO tags (note_id, tag_name) VALUES (3, 'knowledge-management')")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully at: {db_path.absolute()}")
    print("✅ Sample notes and links added")
    print("\nDatabase tables created:")
    print("  - notes (id, title, content, created, updated)")
    print("  - links (id, from_note, to_note, strength, created)")
    print("  - tags (id, note_id, tag_name, created)")
    print("  - metadata (id, note_id, key, value, created)")
    
    return db_path

def verify_database(db_path):
    """Verify that the database was created correctly."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    expected_tables = ['notes', 'links', 'tags', 'metadata']
    
    print(f"\nDatabase verification:")
    for table in expected_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table} table: {count} records")
        else:
            print(f"  ❌ {table} table: missing")
    
    conn.close()

if __name__ == "__main__":
    print("FocusNest Database Initialization")
    print("=" * 40)
    
    try:
        db_path = create_database()
        verify_database(db_path)
        
        print(f"\nSetup complete!")
        print(f"Your database is ready at: {db_path}")
        print("\nNext steps:")
        print("1. Start your FastAPI backend: python backend/run.py")
        print("2. Open frontend/index.html in your browser")
        print("3. Start creating and linking your notes!")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
