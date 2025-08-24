#!/usr/bin/env python3
"""
Script para migrar todos los ejercicios generados desde imágenes a la base SQLite
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def migrate_exercises_to_db():
    """Migra los ejercicios generados desde imágenes a la base de datos SQLite"""
    
    # Paths
    base_path = Path("/home/devjr/Escritorio/gainz-api")
    db_file = base_path / "data" / "exercises.db"
    json_file = base_path / "data" / "exercises_complete_from_images.json"
    
    if not json_file.exists():
        print(f"❌ No se encuentra el archivo JSON: {json_file}")
        return
    
    if not db_file.exists():
        print(f"❌ No se encuentra la base de datos: {db_file}")
        return
    
    # Cargar ejercicios desde JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        exercises = json.load(f)
    
    print(f"📄 Cargados {len(exercises)} ejercicios desde JSON")
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Primero, vamos a limpiar todos los ejercicios existentes para evitar duplicados
    print("🧹 Limpiando ejercicios existentes...")
    cursor.execute("DELETE FROM exercises")
    
    # Insertar todos los ejercicios
    inserted_count = 0
    for exercise in exercises:
        try:
            # Preparar datos para insertar
            created_at = exercise.get('created_at') or datetime.utcnow().isoformat()
            json_data = json.dumps(exercise, ensure_ascii=False)
            
            cursor.execute('''
                INSERT INTO exercises (
                    id, name, slug, primary_muscle, difficulty, json_data, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                exercise['id'],
                exercise['name'],
                exercise['slug'],
                exercise['primary_muscle'],
                exercise['difficulty'],
                json_data,
                created_at
            ))
            
            inserted_count += 1
            print(f"✅ Insertado: {exercise['name']} (ID: {exercise['id']})")
            
        except sqlite3.Error as e:
            print(f"❌ Error insertando {exercise['name']}: {e}")
            continue
    
    # Confirmar cambios
    conn.commit()
    
    # Verificar el resultado
    cursor.execute("SELECT COUNT(*) FROM exercises")
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n🎉 Migración completada:")
    print(f"  📊 Ejercicios insertados: {inserted_count}")
    print(f"  📊 Total en base de datos: {total_count}")
    
    # Mostrar resumen por grupo muscular
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT primary_muscle, COUNT(*) FROM exercises GROUP BY primary_muscle ORDER BY primary_muscle")
    muscle_counts = cursor.fetchall()
    conn.close()
    
    print("\n📊 Resumen por grupo muscular:")
    for muscle, count in muscle_counts:
        print(f"  {muscle}: {count} ejercicios")

if __name__ == "__main__":
    print("🔄 Iniciando migración de ejercicios a SQLite...")
    migrate_exercises_to_db()
    print("✅ Migración completada!")
