# 🚀 Instrucciones de Despliegue para Render

## Problema Identificado

Tu API está mostrando solo 24 ejercicios (v1) en lugar de los 117 ejercicios (v2) porque:

1. **La API v2 estaba configurada para usar SQLite** (base de datos local) en lugar de PostgreSQL
2. **Los datos no habían sido migrados** a PostgreSQL en producción
3. **Faltaban dependencias** de PostgreSQL

## Soluciones Implementadas

### 1. ✅ Dependencias Actualizadas
- Agregado `psycopg2-binary>=2.9.7` para PostgreSQL
- Agregado `sqlalchemy>=2.0.0` para manejo de bases de datos

### 2. ✅ Configuración de Base de Datos
- Detección automática de PostgreSQL vs SQLite
- Uso de `DATABASE_URL` de las variables de entorno en producción
- Fallback a SQLite en desarrollo

### 3. ✅ Módulo de Base de Datos Unificado
- Nuevo archivo `app/database.py` con conexiones unificadas
- Soporte para PostgreSQL y SQLite
- Manejo de errores y logging

### 4. ✅ Router V2 Actualizado
- Conexión a PostgreSQL en producción
- Migración automática desde JSON
- Nuevos endpoints de estadísticas y salud

## 🔧 Pasos para Desplegar

### En Render:

1. **Variables de Entorno Requeridas:**
   ```
   DATABASE_URL=tu_postgresql_url_de_render
   ENVIRONMENT=production
   SECRET_KEY=tu_clave_secreta
   ADMIN_USER=admin
   ADMIN_PASS=tu_password_seguro
   ORIGINS=https://tu-app.com,https://otro-dominio.com
   ```

2. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Command:**
   ```bash
   python scripts/migrate_to_postgres.py && gunicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### 📊 Verificación Post-Despliegue

Después del despliegue, verifica estos endpoints:

1. **Estado general:**
   ```
   GET https://tu-api.onrender.com/
   ```

2. **Estadísticas de la base de datos:**
   ```
   GET https://tu-api.onrender.com/v2/exercises/stats
   ```
   Debe mostrar ~117 ejercicios

3. **Ejercicios v2:**
   ```
   GET https://tu-api.onrender.com/v2/exercises/
   ```

4. **Salud del sistema:**
   ```
   GET https://tu-api.onrender.com/health
   ```

## 🆘 Migración Manual (si es necesario)

Si la migración automática no funciona, puedes ejecutar manualmente:

```bash
POST https://tu-api.onrender.com/v2/exercises/migrate
Authorization: Bearer tu_token_admin
```

## 📝 Notas Importantes

- **La v1 seguirá funcionando** para compatibilidad hacia atrás
- **La v2 tiene más características** y está optimizada para producción
- **Los datos se migran automáticamente** del JSON a PostgreSQL
- **Las imágenes siguen funcionando** igual que antes

## 🔍 Troubleshooting

### Si no ves los ejercicios:
1. Verifica `DATABASE_URL` en las variables de entorno
2. Revisa los logs de Render para errores de migración
3. Usa el endpoint `/v2/exercises/stats` para verificar el conteo

### Si hay errores de conexión:
1. Verifica que PostgreSQL esté funcionando en Render
2. Confirma que `DATABASE_URL` es correcto
3. Revisa los logs para errores de psycopg2

## ✨ Beneficios de la Nueva Configuración

- 🗄️ **Base de datos unificada** - PostgreSQL en producción, SQLite en desarrollo
- 🔄 **Migración automática** - Los datos se migran automáticamente
- 📈 **Mejor rendimiento** - PostgreSQL está optimizado para producción
- 🛡️ **Más robusto** - Mejor manejo de errores y logging
- 📊 **Estadísticas** - Nuevos endpoints para monitorear la salud

¡Tu API debería mostrar ahora los 117 ejercicios en producción! 🎉
