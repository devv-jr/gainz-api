#!/usr/bin/env python3
"""
Script para generar ejercicios automáticamente basándose en las imágenes disponibles
"""

import os
import json
import re
from typing import Dict, List, Tuple

# Mapeo de carpetas a grupos musculares en inglés
MUSCLE_GROUP_MAP = {
    'abs': 'abs',
    'biceps': 'biceps',
    'espalda': 'back',
    'gemelos': 'calves',
    'hombros': 'shoulders',
    'pectorales': 'chest',
    'piernas': 'legs',
    'triceps': 'triceps'
}

# Mapeo de equipamiento común
EQUIPMENT_MAP = {
    'mancuernas': 'dumbbells',
    'mancuerna': 'dumbbells',
    'barra': 'barbell',
    'cable': 'cable',
    'polea': 'cable',
    'maquina': 'machine',
    'smith': 'smith_machine',
    'banco': 'bench',
    'peso-corporal': 'bodyweight',
    'balon': 'exercise_ball',
    'banda': 'resistance_band'
}

def clean_exercise_name(filename: str) -> str:
    """Limpia el nombre del archivo para crear un nombre de ejercicio legible"""
    # Quitar extensión
    name = filename.replace('.png', '')
    
    # Reemplazar guiones por espacios
    name = name.replace('-', ' ')
    
    # Capitalizar cada palabra
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name

def extract_equipment(filename: str) -> List[str]:
    """Extrae el equipamiento del nombre del archivo"""
    equipment = []
    filename_lower = filename.lower()
    
    for spanish_eq, english_eq in EQUIPMENT_MAP.items():
        if spanish_eq in filename_lower:
            equipment.append(english_eq)
    
    # Equipamiento por defecto si no se encuentra ninguno específico
    if not equipment:
        equipment = ['bodyweight']
    
    return list(set(equipment))  # Eliminar duplicados

def determine_difficulty(filename: str, muscle_group: str) -> str:
    """Determina la dificultad basada en el ejercicio"""
    filename_lower = filename.lower()
    
    # Ejercicios para principiantes
    beginner_keywords = ['peso-corporal', 'maquina', 'sentado', 'pared', 'balon']
    if any(keyword in filename_lower for keyword in beginner_keywords):
        return 'beginner'
    
    # Ejercicios avanzados
    advanced_keywords = ['dominadas', 'bulgara', 'peso-muerto', 'smith', 'una-mano', 'salto']
    if any(keyword in filename_lower for keyword in advanced_keywords):
        return 'advanced'
    
    return 'intermediate'

def get_secondary_muscles(primary_muscle: str, filename: str) -> List[str]:
    """Determina músculos secundarios basándose en el ejercicio"""
    filename_lower = filename.lower()
    secondary = []
    
    if primary_muscle == 'chest':
        secondary = ['triceps', 'shoulders']
    elif primary_muscle == 'back':
        if 'peso-muerto' in filename_lower:
            secondary = ['legs', 'glutes']
        else:
            secondary = ['biceps']
    elif primary_muscle == 'shoulders':
        secondary = ['triceps']
    elif primary_muscle == 'legs':
        if 'sentadilla' in filename_lower or 'prensa' in filename_lower:
            secondary = ['glutes']
        elif 'femoral' in filename_lower or 'peso-muerto' in filename_lower:
            secondary = ['glutes', 'back']
        else:
            secondary = ['glutes']
    elif primary_muscle == 'biceps':
        secondary = []
    elif primary_muscle == 'triceps':
        secondary = []
    elif primary_muscle == 'abs':
        secondary = []
    elif primary_muscle == 'calves':
        secondary = []
    
    return secondary

def generate_exercise_steps(exercise_name: str, equipment: List[str]) -> List[Dict]:
    """Genera pasos básicos para el ejercicio"""
    steps = [
        {
            "order": 1,
            "title": "Posición inicial",
            "instruction": f"Adopta la posición inicial correcta para {exercise_name.lower()}",
            "duration_sec": None
        },
        {
            "order": 2,
            "title": "Ejecución",
            "instruction": f"Realiza el movimiento de {exercise_name.lower()} de forma controlada",
            "duration_sec": 2
        },
        {
            "order": 3,
            "title": "Retorno",
            "instruction": "Regresa a la posición inicial de forma controlada",
            "duration_sec": 2
        }
    ]
    
    return steps

def generate_tips(exercise_name: str, equipment: List[str]) -> List[str]:
    """Genera consejos básicos para el ejercicio"""
    tips = [
        "Mantén una postura correcta durante todo el ejercicio",
        "Controla la respiración durante el movimiento",
        "No uses momentum, enfócate en el control del peso"
    ]
    
    if 'barbell' in equipment or 'dumbbells' in equipment:
        tips.append("Usa un peso apropiado para tu nivel")
    
    if 'bodyweight' in equipment:
        tips.append("Enfócate en la técnica antes que en la velocidad")
        
    return tips

def generate_exercises_json():
    """Genera el JSON completo de ejercicios basándose en las imágenes"""
    base_path = "/home/devjr/Escritorio/gainz-api/static/images"
    exercises = []
    exercise_id = 1
    
    # Recorrer cada carpeta de grupo muscular
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        
        # Saltar archivos que no son carpetas
        if not os.path.isdir(folder_path) or folder == '.gitkeep':
            continue
            
        # Obtener grupo muscular
        primary_muscle = MUSCLE_GROUP_MAP.get(folder, folder)
        
        # Recorrer imágenes en la carpeta
        for filename in os.listdir(folder_path):
            if not filename.endswith('.png'):
                continue
                
            # Generar datos del ejercicio
            exercise_name = clean_exercise_name(filename)
            slug = filename.replace('.png', '')
            equipment = extract_equipment(filename)
            difficulty = determine_difficulty(filename, primary_muscle)
            secondary_muscles = get_secondary_muscles(primary_muscle, filename)
            
            exercise = {
                "id": exercise_id,
                "slug": slug,
                "name": exercise_name,
                "summary": f"Ejercicio de {folder} enfocado en {exercise_name.lower()}",
                "description": f"{exercise_name} es un excelente ejercicio para desarrollar y fortalecer {folder}.",
                "primary_muscle": primary_muscle,
                "secondary_muscles": secondary_muscles,
                "equipment": equipment,
                "difficulty": difficulty,
                "steps": generate_exercise_steps(exercise_name, equipment),
                "tips": generate_tips(exercise_name, equipment),
                "images": [
                    {
                        "url": f"https://gainz-api.onrender.com/static/images/{folder}/{filename}",
                        "type": "demonstration",
                        "width": 800,
                        "height": 600
                    }
                ]
            }
            
            exercises.append(exercise)
            exercise_id += 1
            
            print(f"Agregado: {exercise_name} (ID: {exercise_id - 1})")
    
    return exercises

if __name__ == "__main__":
    print("Generando ejercicios basándose en imágenes disponibles...")
    
    exercises = generate_exercises_json()
    
    # Guardar el resultado
    output_file = "/home/devjr/Escritorio/gainz-api/data/exercises_complete_from_images.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(exercises, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Generados {len(exercises)} ejercicios")
    print(f"📁 Archivo guardado en: {output_file}")
    
    # Mostrar resumen por grupo muscular
    muscle_counts = {}
    for exercise in exercises:
        muscle = exercise['primary_muscle']
        muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
    
    print("\n📊 Resumen por grupo muscular:")
    for muscle, count in sorted(muscle_counts.items()):
        print(f"  {muscle}: {count} ejercicios")
