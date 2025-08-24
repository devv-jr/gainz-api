# 💪 GainzAPI - API de Ejercicios para Gimnasio

API REST moderna construida con FastAPI para gestionar ejercicios de gimnasio. Diseñada específicamente para la aplicación móvil GAINZAPP desarrollada en React Native/Expo.

## 🚀 Características

- ✅ **Dos versiones de API** (v1 básica, v2 avanzada)
- ✅ **Autenticación JWT** para operaciones administrativas
- ✅ **Base de datos SQLite** con migración automática
- ✅ **Upload de imágenes** con validación
- ✅ **Filtros y búsqueda** avanzada
- ✅ **Documentación automática** con Swagger/OpenAPI
- ✅ **CORS configurado** para React Native
- ✅ **Rate limiting** para protección
- ✅ **Logging completo** y manejo de errores
- ✅ **Health check** endpoint

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno para Python
- **SQLite** - Base de datos ligera
- **JWT** - Autenticación con tokens
- **Pydantic** - Validación de datos
- **Uvicorn/Gunicorn** - Servidor ASGI

## 📚 Documentación de la API

Una vez desplegada, la documentación interactiva estará disponible en:
- **Swagger UI**: `https://tu-app.onrender.com/docs`
- **ReDoc**: `https://tu-app.onrender.com/redoc`

## 🔧 Configuración para Producción

### Variables de Entorno Requeridas

```bash
# En Render, configurar estas variables:
SECRET_KEY=tu-clave-secreta-super-segura-aqui
ADMIN_USER=admin
ADMIN_PASS=tu-password-seguro
ORIGINS=exp://127.0.0.1:19000,https://tu-app.onrender.com
```

### Despliegue en Render

1. **Conecta tu repositorio** a Render
2. **Configura las variables de entorno** arriba mencionadas
3. **Render detectará automáticamente** el `Procfile` y `requirements.txt`
4. **El build será automático** usando `runtime.txt` para Python 3.12

## 📱 Cliente JavaScript para React Native

Se incluyen dos archivos para consumir la API desde React Native:

### `GainzAPI.js` - Cliente principal
```javascript
import GainzAPI from './GainzAPI';

const gainzAPI = new GainzAPI('https://tu-app.onrender.com');

// Obtener ejercicios
const exercises = await gainzAPI.getExercisesV2();

// Buscar ejercicios
const results = await gainzAPI.getExercisesV2({ 
  query: 'push up', 
  muscle: 'chest' 
});
```

### `GainzHooks.js` - Hooks personalizados
```javascript
import { useExercises, useAuth } from './GainzHooks';

const ExercisesScreen = () => {
  const { exercises, loading, searchExercises } = useExercises('v2');
  const { isAuthenticated, login } = useAuth();
  
  // Tu componente aqui...
};
```

## 🔒 Endpoints Principales

### Públicos (Sin autenticación)

- `GET /` - Información de la API
- `GET /health` - Health check
- `GET /v1/exercises/` - Listar ejercicios v1
- `GET /v1/exercises/{id}` - Obtener ejercicio v1
- `GET /v2/exercises/` - Listar ejercicios v2 (con filtros)
- `GET /v2/exercises/{id}` - Obtener ejercicio v2

### Privados (Requieren autenticación)

- `POST /auth/token` - Obtener token de acceso
- `POST /v2/exercises/` - Crear ejercicio
- `PUT /v2/exercises/{id}` - Actualizar ejercicio  
- `DELETE /v2/exercises/{id}` - Eliminar ejercicio
- `POST /images/upload` - Subir imagen
- `POST /v2/exercises/migrate` - Migrar datos a BD

## 📊 Estructura de Datos

### Ejercicio v1 (Básico)
```json
{
  "id": 1,
  "name": "Push Up",
  "muscle": "chest",
  "equipment": "bodyweight",
  "difficulty": "beginner",
  "instructions": "Do a push up"
}
```

### Ejercicio v2 (Avanzado)
```json
{
  "id": 1,
  "slug": "push-up",
  "name": "Push Up",
  "summary": "Basic upper body exercise",
  "description": "Complete push up instructions...",
  "primary_muscle": "chest",
  "secondary_muscles": ["triceps", "shoulders"],
  "equipment": ["bodyweight"],
  "difficulty": "beginner",
  "steps": [
    {
      "order": 1,
      "instruction": "Start in plank position",
      "duration_sec": null
    }
  ],
  "tips": ["Keep your core tight"],
  "images": [
    {
      "url": "https://example.com/image.jpg",
      "type": "step",
      "width": 800,
      "height": 600
    }
  ],
  "video_url": null,
  "tags": ["push", "upper-body"],
  "variations": [],
  "estimated": {
    "sets": 3,
    "reps_min": 8,
    "reps_max": 12,
    "rest_sec": 60
  },
  "created_at": "2025-08-23T10:30:00",
  "updated_at": "2025-08-23T10:30:00"
}
```

## 🔍 Filtros Disponibles

### v1 Exercises
- `muscle` - Músculo específico
- `equipment` - Equipamiento específico  
- `difficulty` - Nivel de dificultad

### v2 Exercises
- `query` - Búsqueda en nombre y descripción
- `muscle` - Músculo principal
- `equipment` - Equipamiento específico
- `page` - Página (paginación)
- `limit` - Elementos por página

## 🛡️ Seguridad

- **JWT tokens** con expiración de 24 horas
- **Rate limiting** para prevenir abuso
- **CORS** configurado específicamente para React Native
- **Validación de datos** con Pydantic
- **Logging** completo de errores y accesos

## ⚡ Rendimiento

- **Paginación** en endpoints v2
- **Índices de base de datos** en campos principales
- **Compresión gzip** automática
- **Caching** de archivos estáticos

## 🧪 Testing

```bash
# Ejecutar tests
python -m pytest tests/ -v

# Tests incluidos:
# ✅ Verificación de base de datos
# ✅ Endpoints públicos funcionando
# ✅ Estructura de datos correcta
```

## 📝 Logging

La API incluye logging completo:
- Errores HTTP con detalles
- Errores de validación
- Excepciones no controladas  
- Accesos a endpoints protegidos

## 🚀 Para usar en tu React Native App

1. **Cambia la URL base** en `GainzAPI.js` por tu URL de Render
2. **Instala AsyncStorage**: `npx expo install @react-native-async-storage/async-storage`
3. **Importa y usa** los hooks o el cliente directo

```bash
# En tu proyecto React Native
npm install @react-native-async-storage/async-storage

# Copia los archivos
cp GainzAPI.js tu-proyecto-rn/src/services/
cp GainzHooks.js tu-proyecto-rn/src/hooks/
```

## 🎯 Estado de Producción

### ✅ LISTO PARA PRODUCCIÓN:
- Estructura modular y profesional
- Autenticación y autorización
- Manejo de errores global
- Logging configurado
- Tests básicos funcionando
- CORS configurado
- Variables de entorno seguras
- Documentación automática

### 🔄 RECOMENDACIONES ADICIONALES:
- Monitoreo con herramientas como Sentry
- Backup automático de la base de datos
- Tests de integración más extensos
- Cache con Redis para mayor rendimiento
- Métricas de uso y análisis

**¡Tu API está lista para producción! 🚀**
