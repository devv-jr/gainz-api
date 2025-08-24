#!/usr/bin/env python3
"""
Script para exportar todos los ejercicios desde SQLite a JSON
Genera un archivo completo con todos los ejercicios de la base de datos local
"""
import sqlite3
import json
from pathlib import Path
import sys

def export_exercises():
    """Export all exercises from SQLite to JSON"""
    db_path = Path(__file__).parent.parent / "data" / "exercises.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 0
    
    print(f"📖 Reading from database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exercises ORDER BY id")
        
        exercises = []
        for row in cursor.fetchall():
            exercise = dict(row)
            
            # Handle JSON fields - convert string JSON back to objects
            json_fields = ['secondary_muscles', 'equipment', 'steps', 'tips', 'images', 'tags', 'variations']
            for field in json_fields:
                if field in exercise and exercise[field] and isinstance(exercise[field], str):
                    try:
                        exercise[field] = json.loads(exercise[field])
                    except json.JSONDecodeError:
                        print(f"⚠️  Warning: Could not parse JSON for {field} in exercise {exercise.get('id', 'unknown')}")
                        exercise[field] = []
            
            exercises.append(exercise)
        
        conn.close()
        
        # Save complete exercises
        json_path = Path(__file__).parent.parent / "data" / "exercises_complete.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Exported {len(exercises)} exercises to {json_path}")
        
        # Also create a backup with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_path = Path(__file__).parent.parent / "data" / f"exercises_backup_{timestamp}.json"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📦 Backup created: {backup_path}")
        
        return len(exercises)
        
    except Exception as e:
        print(f"❌ Error exporting exercises: {e}")
        return 0

def get_database_info():
    """Get information about the current database"""
    db_path = Path(__file__).parent.parent / "data" / "exercises.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT COUNT(*) FROM exercises")
        total = cursor.fetchone()[0]
        
        # Get muscle group distribution
        cursor.execute("SELECT primary_muscle, COUNT(*) FROM exercises GROUP BY primary_muscle ORDER BY COUNT(*) DESC")
        muscle_groups = cursor.fetchall()
        
        # Get difficulty distribution
        cursor.execute("SELECT difficulty, COUNT(*) FROM exercises GROUP BY difficulty ORDER BY COUNT(*) DESC")
        difficulties = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 Database Statistics:")
        print(f"  Total exercises: {total}")
        print(f"  Muscle groups: {len(muscle_groups)}")
        print(f"  Difficulties: {len(difficulties)}")
        
        print(f"\n🏋️  Muscle Group Distribution:")
        for muscle, count in muscle_groups:
            print(f"  {muscle or 'Unknown'}: {count}")
        
        print(f"\n⭐ Difficulty Distribution:")
        for difficulty, count in difficulties:
            print(f"  {difficulty or 'Unknown'}: {count}")
            
    except Exception as e:
        print(f"❌ Error getting database info: {e}")

if __name__ == "__main__":
    print("🚀 Exercise Export Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        get_database_info()
    else:
        get_database_info()
        print("\n" + "=" * 50)
        total_exported = export_exercises()
        
        if total_exported > 0:
            print(f"\n🎉 Successfully exported {total_exported} exercises!")
            print("   Ready to deploy to production.")
        else:
            print("\n❌ Export failed!")
