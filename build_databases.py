
import os
import sqlite3
import json
from datetime import datetime

# Ce script est destiné à être exécuté par une GitHub Action.
# Il lit les fichiers JSON du dossier 'sources' et génère les bases de données
# SQLite dans le dossier 'knowledge'.

SOURCES_DIR = 'sources'
KNOWLEDGE_DIR = 'knowledge'

def main():
    print("--- Démarrage du script de build de la base de connaissances ---")
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)

    # Parcourir récursivement les fichiers sources
    for root, _, files in os.walk(SOURCES_DIR):
        for file in files:
            if file.endswith('.json'):
                source_file_path = os.path.join(root, file)
                
                # Déterminer le chemin de la future base de données
                relative_path = os.path.relpath(source_file_path, SOURCES_DIR)
                db_name = os.path.splitext(os.path.basename(relative_path))[0]
                db_dir = os.path.dirname(os.path.join(KNOWLEDGE_DIR, relative_path))
                
                # Cas spécial : awesome-python.json -> python.db
                if db_name == 'awesome-python':
                    db_name = 'python'

                db_path = os.path.join(db_dir, f"{db_name}.db")
                
                if not os.path.exists(db_dir):
                    os.makedirs(db_dir)

                print(f"🗃️ Traitement de {source_file_path} -> {db_path}")
                
                # Charger les données JSON
                with open(source_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Créer et peupler la base de données
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                    content TEXT, source_url TEXT UNIQUE, tags TEXT, last_updated TEXT
                )
                ''')

                for entry in data:
                    try:
                        cursor.execute(
                            'INSERT INTO knowledge (title, content, source_url, tags, last_updated) VALUES (?, ?, ?, ?, ?)',
                            (entry['title'], entry.get('content', ''), entry['source_url'], entry.get('tags', ''), entry['last_updated'])
                        )
                    except sqlite3.IntegrityError:
                        # Ignorer les doublons
                        continue
                
                conn.commit()
                conn.close()
    
    print("--- ✅ Build terminé avec succès ! ---")

if __name__ == '__main__':
    main()
