# 📱 GUÍA: ACCESO A GAINZ API DESDE REACT NATIVE

## 🌐 **URL Base de tu API en Render**
```javascript
const API_BASE_URL = 'https://gainz-api.onrender.com';
```

## 🔧 **Configuración del Cliente API**

### 1. **Instalar dependencias**
```bash
npm install axios
# o
yarn add axios
```

### 2. **Crear servicio API (api/exercisesService.js)**
```javascript
import axios from 'axios';

const API_BASE_URL = 'https://gainz-api.onrender.com';

// Configurar cliente axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
```

## 📝 **Funciones para Ejercicios**

### 3. **Servicio de ejercicios (services/exerciseService.js)**
```javascript
import apiClient from '../api/exercisesService';

class ExerciseService {
  
  // Obtener todos los ejercicios
  async getAllExercises(limit = 50, page = 1) {
    try {
      const response = await apiClient.get('/v2/exercises/', {
        params: { limit, page }
      });
      return response.data;
    } catch (error) {
      throw new Error('Error al obtener ejercicios: ' + error.message);
    }
  }

  // Filtrar por grupo muscular
  async getExercisesByMuscle(muscle, limit = 50) {
    try {
      const response = await apiClient.get('/v2/exercises/', {
        params: { muscle, limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Error al obtener ejercicios de ${muscle}: ` + error.message);
    }
  }

  // Filtrar por equipamiento
  async getExercisesByEquipment(equipment, limit = 50) {
    try {
      const response = await apiClient.get('/v2/exercises/', {
        params: { equipment, limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Error al obtener ejercicios con ${equipment}: ` + error.message);
    }
  }

  // Obtener ejercicio por ID
  async getExerciseById(id) {
    try {
      const response = await apiClient.get(`/v2/exercises/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(`Error al obtener ejercicio ${id}: ` + error.message);
    }
  }

  // Buscar ejercicios
  async searchExercises(query, limit = 20) {
    try {
      const response = await apiClient.get('/v2/exercises/', {
        params: { query, limit }
      });
      return response.data;
    } catch (error) {
      throw new Error('Error en búsqueda: ' + error.message);
    }
  }
}

export default new ExerciseService();
```

## 📱 **Ejemplos de uso en componentes React Native**

### 4. **Hook personalizado (hooks/useExercises.js)**
```javascript
import { useState, useEffect } from 'react';
import ExerciseService from '../services/exerciseService';

export const useExercises = (muscle = null, equipment = null) => {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        setLoading(true);
        setError(null);
        
        let data;
        if (muscle) {
          data = await ExerciseService.getExercisesByMuscle(muscle);
        } else if (equipment) {
          data = await ExerciseService.getExercisesByEquipment(equipment);
        } else {
          data = await ExerciseService.getAllExercises();
        }
        
        setExercises(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchExercises();
  }, [muscle, equipment]);

  return { exercises, loading, error };
};
```

### 5. **Componente de lista de ejercicios**
```javascript
import React from 'react';
import { View, Text, FlatList, Image, ActivityIndicator, StyleSheet } from 'react-native';
import { useExercises } from '../hooks/useExercises';

const ExercisesList = ({ muscle }) => {
  const { exercises, loading, error } = useExercises(muscle);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#0066cc" />
        <Text>Cargando ejercicios...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>❌ {error}</Text>
      </View>
    );
  }

  const renderExercise = ({ item }) => (
    <View style={styles.exerciseCard}>
      <Image 
        source={{ uri: item.images[0]?.url }} 
        style={styles.exerciseImage}
        resizeMode="cover"
      />
      <View style={styles.exerciseInfo}>
        <Text style={styles.exerciseName}>{item.name}</Text>
        <Text style={styles.exerciseDescription}>{item.summary}</Text>
        <View style={styles.tags}>
          <Text style={styles.muscle}>{item.primary_muscle}</Text>
          <Text style={styles.difficulty}>{item.difficulty}</Text>
          <Text style={styles.equipment}>{item.equipment.join(', ')}</Text>
        </View>
      </View>
    </View>
  );

  return (
    <FlatList
      data={exercises}
      keyExtractor={(item) => item.id.toString()}
      renderItem={renderExercise}
      showsVerticalScrollIndicator={false}
    />
  );
};

const styles = StyleSheet.create({
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    fontSize: 16,
  },
  exerciseCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
    marginHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    flexDirection: 'row',
  },
  exerciseImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 12,
  },
  exerciseInfo: {
    flex: 1,
  },
  exerciseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  exerciseDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  muscle: {
    backgroundColor: '#e3f2fd',
    color: '#1976d2',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    fontSize: 12,
    marginRight: 4,
  },
  difficulty: {
    backgroundColor: '#f3e5f5',
    color: '#7b1fa2',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    fontSize: 12,
    marginRight: 4,
  },
  equipment: {
    backgroundColor: '#e8f5e8',
    color: '#388e3c',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    fontSize: 12,
  },
});

export default ExercisesList;
```

## 🔍 **Ejemplo de uso por grupos musculares**

### 6. **Componente selector de músculos**
```javascript
import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import ExercisesList from './ExercisesList';

const MuscleGroups = () => {
  const [selectedMuscle, setSelectedMuscle] = useState('chest');

  const muscleGroups = [
    { key: 'chest', label: '💪 Pectorales', count: 12 },
    { key: 'back', label: '🏋️ Espalda', count: 21 },
    { key: 'legs', label: '🦵 Piernas', count: 29 },
    { key: 'shoulders', label: '🏆 Hombros', count: 17 },
    { key: 'biceps', label: '💪 Bíceps', count: 14 },
    { key: 'triceps', label: '🔥 Tríceps', count: 13 },
    { key: 'abs', label: '⚡ Abdominales', count: 9 },
    { key: 'calves', label: '🚀 Gemelos', count: 2 },
  ];

  return (
    <View style={styles.container}>
      {/* Selector de grupos musculares */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.muscleSelector}
      >
        {muscleGroups.map((muscle) => (
          <TouchableOpacity
            key={muscle.key}
            style={[
              styles.muscleButton,
              selectedMuscle === muscle.key && styles.selectedMuscle
            ]}
            onPress={() => setSelectedMuscle(muscle.key)}
          >
            <Text style={[
              styles.muscleText,
              selectedMuscle === muscle.key && styles.selectedMuscleText
            ]}>
              {muscle.label}
            </Text>
            <Text style={styles.countText}>{muscle.count}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Lista de ejercicios */}
      <ExercisesList muscle={selectedMuscle} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  muscleSelector: {
    paddingVertical: 16,
    paddingHorizontal: 8,
  },
  muscleButton: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 4,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
    alignItems: 'center',
  },
  selectedMuscle: {
    backgroundColor: '#2196f3',
  },
  muscleText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  selectedMuscleText: {
    color: '#fff',
  },
  countText: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
});

export default MuscleGroups;
```

## 🔧 **URLs importantes de tu API**

```javascript
// Ejercicios
'https://gainz-api.onrender.com/v2/exercises/'              // Todos los ejercicios
'https://gainz-api.onrender.com/v2/exercises/?muscle=chest' // Por músculo
'https://gainz-api.onrender.com/v2/exercises/1'             // Ejercicio específico

// Imágenes
'https://gainz-api.onrender.com/static/images/chest/press-banca.png'
```

## ⚡ **Optimizaciones recomendadas**

### 7. **Cache con AsyncStorage**
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const CACHE_KEY = 'exercises_cache';
const CACHE_DURATION = 1000 * 60 * 60; // 1 hora

export const getCachedExercises = async (key) => {
  try {
    const cached = await AsyncStorage.getItem(`${CACHE_KEY}_${key}`);
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      if (Date.now() - timestamp < CACHE_DURATION) {
        return data;
      }
    }
    return null;
  } catch (error) {
    return null;
  }
};

export const setCachedExercises = async (key, data) => {
  try {
    const cacheData = {
      data,
      timestamp: Date.now(),
    };
    await AsyncStorage.setItem(`${CACHE_KEY}_${key}`, JSON.stringify(cacheData));
  } catch (error) {
    console.error('Error caching exercises:', error);
  }
};
```

## 📱 **¡Listo para usar!**

Con esta configuración tendrás acceso completo a los **117 ejercicios** de tu API desde React Native con:
- ✅ Filtrado por grupos musculares
- ✅ Filtrado por equipamiento  
- ✅ Búsqueda de ejercicios
- ✅ Imágenes optimizadas
- ✅ Manejo de errores
- ✅ Estados de carga
- ✅ Cache para mejor rendimiento

**URL base:** `https://gainz-api.onrender.com`
