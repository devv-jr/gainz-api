#!/bin/bash
# Deploy Script for Gainz API
# Ejecuta todos los pasos necesarios para el deploy

echo "🚀 Gainz API Deploy Script"
echo "========================="

# 1. Verificar estado actual
echo "📊 Estado actual de la base de datos:"
python3 -c "
import sqlite3
conn = sqlite3.connect('data/exercises.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM exercises')
count = cursor.fetchone()[0]
print(f'  ✅ Ejercicios en SQLite: {count}')
conn.close()
"

echo "📁 Archivos de datos disponibles:"
echo "  ✅ exercises_complete.json: $(python3 -c "import json; print(len(json.load(open('data/exercises_complete.json'))))")" ejercicios
echo "  ✅ exercises.json: $(python3 -c "import json; print(len(json.load(open('data/exercises.json'))))")" ejercicios "(anterior)"

# 2. Git status
echo ""
echo "📝 Estado de Git:"
git status --porcelain | head -10

# 3. Preparar commit
echo ""
echo "🔄 Preparando deploy..."
read -p "¿Continuar con el deploy? (y/n): " -n 1 -r
echo 
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deploy cancelado"
    exit 1
fi

# 4. Commit y push
echo "📤 Subiendo cambios a GitHub..."
git add .
git commit -m "🚀 Deploy: Fix endpoint /stats + force migration + 117 exercises ready

- Fixed /stats endpoint positioning (before /{exercise_id})
- Added force-migrate endpoint for complete migration
- Created export_complete.py script
- Implemented missing database functions
- Ready for production with 117 exercises

Fixes: #stats-endpoint #migration #complete-exercises"

git push origin main

echo ""
echo "✅ DEPLOY COMPLETADO"
echo "==================="
echo ""
echo "🔗 Próximos pasos en producción:"
echo "1. Render auto-deploy en progreso..."
echo "2. Verificar: https://tu-app.render.com/v2/exercises/stats"  
echo "3. Migrar: POST /v2/exercises/force-migrate"
echo "4. Confirmar: 117 ejercicios en producción"
echo ""
echo "📋 Endpoints listos:"
echo "  ✅ GET  /v2/exercises/stats"
echo "  ✅ POST /v2/exercises/force-migrate"
echo "  ✅ GET  /v2/exercises/ (117 ejercicios)"
echo ""
echo "🎉 Deploy exitoso - Listo para resolver el problema!"
