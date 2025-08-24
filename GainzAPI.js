/**
 * GainzAPI Client para React Native (Expo)
 * Cliente JavaScript para consumir la API de ejercicios de gimnasio
 * 
 * Configuración:
 * - Cambia BASE_URL por la URL de tu API en Render
 * - Guarda el token de autenticación en AsyncStorage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

// ⚠️ CAMBIA ESTA URL POR LA DE TU API EN RENDER
const BASE_URL = 'https://tu-app.onrender.com';

// Token storage keys
const TOKEN_KEY = '@gainz_auth_token';
const TOKEN_EXPIRY_KEY = '@gainz_token_expiry';

class GainzAPI {
  constructor(baseURL = BASE_URL) {
    this.baseURL = baseURL;
    this.token = null;
  }

  // ===========================================
  // AUTENTICACIÓN
  // ===========================================

  /**
   * Iniciar sesión y obtener token
   * @param {string} username - Usuario admin
   * @param {string} password - Contraseña admin
   * @returns {Promise<{access_token: string, token_type: string}>}
   */
  async login(username = 'admin', password = 'password') {
    try {
      const response = await fetch(`${this.baseURL}/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error(`Login failed: ${response.status}`);
      }

      const data = await response.json();
      this.token = data.access_token;
      
      // Guardar token en AsyncStorage
      await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
      await AsyncStorage.setItem(TOKEN_EXPIRY_KEY, Date.now() + (24 * 60 * 60 * 1000)); // 24 horas
      
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Cargar token guardado desde AsyncStorage
   */
  async loadStoredToken() {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      const expiry = await AsyncStorage.getItem(TOKEN_EXPIRY_KEY);
      
      if (token && expiry && Date.now() < parseInt(expiry)) {
        this.token = token;
        return token;
      } else {
        await this.clearToken();
        return null;
      }
    } catch (error) {
      console.error('Error loading token:', error);
      return null;
    }
  }

  /**
   * Limpiar token almacenado
   */
  async clearToken() {
    this.token = null;
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(TOKEN_EXPIRY_KEY);
  }

  /**
   * Cerrar sesión
   */
  async logout() {
    await this.clearToken();
  }

  // ===========================================
  // EJERCICIOS V1 (Básicos)
  // ===========================================

  /**
   * Obtener todos los ejercicios v1 con filtros opcionales
   * @param {Object} filters - Filtros opcionales
   * @param {string} filters.muscle - Músculo específico
   * @param {string} filters.equipment - Equipamiento específico
   * @param {string} filters.difficulty - Dificultad específica
   */
  async getExercisesV1(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.muscle) params.append('muscle', filters.muscle);
      if (filters.equipment) params.append('equipment', filters.equipment);
      if (filters.difficulty) params.append('difficulty', filters.difficulty);

      const url = `${this.baseURL}/v1/exercises/?${params.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch exercises: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching exercises v1:', error);
      throw error;
    }
  }

  /**
   * Obtener un ejercicio específico v1
   * @param {number} exerciseId - ID del ejercicio
   */
  async getExerciseV1(exerciseId) {
    try {
      const response = await fetch(`${this.baseURL}/v1/exercises/${exerciseId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Exercise not found');
        }
        throw new Error(`Failed to fetch exercise: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching exercise v1:', error);
      throw error;
    }
  }

  // ===========================================
  // EJERCICIOS V2 (Avanzados)
  // ===========================================

  /**
   * Obtener todos los ejercicios v2 con filtros y paginación
   * @param {Object} options - Opciones de búsqueda
   * @param {string} options.query - Término de búsqueda
   * @param {string} options.muscle - Músculo específico
   * @param {string} options.equipment - Equipamiento específico
   * @param {number} options.page - Página (default: 1)
   * @param {number} options.limit - Límite por página (default: 50)
   */
  async getExercisesV2(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.query) params.append('query', options.query);
      if (options.muscle) params.append('muscle', options.muscle);
      if (options.equipment) params.append('equipment', options.equipment);
      if (options.page) params.append('page', options.page.toString());
      if (options.limit) params.append('limit', options.limit.toString());

      const url = `${this.baseURL}/v2/exercises/?${params.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch exercises v2: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching exercises v2:', error);
      throw error;
    }
  }

  /**
   * Obtener un ejercicio específico v2
   * @param {number} exerciseId - ID del ejercicio
   */
  async getExerciseV2(exerciseId) {
    try {
      const response = await fetch(`${this.baseURL}/v2/exercises/${exerciseId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Exercise not found');
        }
        throw new Error(`Failed to fetch exercise v2: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching exercise v2:', error);
      throw error;
    }
  }

  /**
   * Crear nuevo ejercicio v2 (requiere autenticación)
   * @param {Object} exerciseData - Datos del ejercicio
   */
  async createExerciseV2(exerciseData) {
    try {
      await this.loadStoredToken();
      if (!this.token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${this.baseURL}/v2/exercises/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
        },
        body: JSON.stringify(exerciseData),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed');
        }
        throw new Error(`Failed to create exercise: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating exercise v2:', error);
      throw error;
    }
  }

  /**
   * Actualizar ejercicio v2 (requiere autenticación)
   * @param {number} exerciseId - ID del ejercicio
   * @param {Object} exerciseData - Datos actualizados del ejercicio
   */
  async updateExerciseV2(exerciseId, exerciseData) {
    try {
      await this.loadStoredToken();
      if (!this.token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${this.baseURL}/v2/exercises/${exerciseId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
        },
        body: JSON.stringify(exerciseData),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed');
        }
        if (response.status === 404) {
          throw new Error('Exercise not found');
        }
        throw new Error(`Failed to update exercise: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating exercise v2:', error);
      throw error;
    }
  }

  /**
   * Eliminar ejercicio v2 (requiere autenticación)
   * @param {number} exerciseId - ID del ejercicio
   */
  async deleteExerciseV2(exerciseId) {
    try {
      await this.loadStoredToken();
      if (!this.token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${this.baseURL}/v2/exercises/${exerciseId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed');
        }
        if (response.status === 404) {
          throw new Error('Exercise not found');
        }
        throw new Error(`Failed to delete exercise: ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Error deleting exercise v2:', error);
      throw error;
    }
  }

  // ===========================================
  // IMÁGENES
  // ===========================================

  /**
   * Subir imagen (requiere autenticación)
   * @param {Object} imageFile - Archivo de imagen
   */
  async uploadImage(imageFile) {
    try {
      await this.loadStoredToken();
      if (!this.token) {
        throw new Error('Authentication required');
      }

      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch(`${this.baseURL}/images/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to upload image: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error uploading image:', error);
      throw error;
    }
  }

  // ===========================================
  // UTILIDADES
  // ===========================================

  /**
   * Verificar estado de la API
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Obtener información de la API
   */
  async getApiInfo() {
    try {
      const response = await fetch(`${this.baseURL}/`);
      return await response.json();
    } catch (error) {
      console.error('Error getting API info:', error);
      throw error;
    }
  }

  /**
   * Migrar datos a base de datos (requiere autenticación)
   */
  async migrate() {
    try {
      await this.loadStoredToken();
      if (!this.token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${this.baseURL}/v2/exercises/migrate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Migration failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error during migration:', error);
      throw error;
    }
  }
}

// ===========================================
// EJEMPLO DE USO
// ===========================================

/*
// Instanciar el cliente
const gainzAPI = new GainzAPI('https://tu-app.onrender.com');

// Ejemplo de uso en un componente React Native:

import React, { useEffect, useState } from 'react';
import { View, Text, FlatList } from 'react-native';

const ExercisesScreen = () => {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExercises();
  }, []);

  const loadExercises = async () => {
    try {
      // Cargar ejercicios básicos
      const data = await gainzAPI.getExercisesV1();
      setExercises(data);
    } catch (error) {
      console.error('Error loading exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchExercises = async (query) => {
    try {
      const data = await gainzAPI.getExercisesV2({ query });
      setExercises(data);
    } catch (error) {
      console.error('Error searching exercises:', error);
    }
  };

  if (loading) {
    return <Text>Loading...</Text>;
  }

  return (
    <FlatList
      data={exercises}
      keyExtractor={(item) => item.id.toString()}
      renderItem={({ item }) => (
        <View>
          <Text>{item.name}</Text>
          <Text>{item.muscle}</Text>
          <Text>{item.instructions || item.description}</Text>
        </View>
      )}
    />
  );
};

export default ExercisesScreen;
*/

export default GainzAPI;
