/**
 * Custom Hooks para GainzAPI en React Native
 * Hooks útiles para manejar el estado y las operaciones de la API
 */

import { useState, useEffect, useCallback } from 'react';
import GainzAPI from './GainzAPI';

// ⚠️ CAMBIA ESTA URL POR LA DE TU API EN RENDER
const API_URL = 'https://tu-app.onrender.com';
const gainzAPI = new GainzAPI(API_URL);

// ===========================================
// HOOK: useAuth - Manejo de autenticación
// ===========================================

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = useCallback(async () => {
    try {
      const token = await gainzAPI.loadStoredToken();
      setIsAuthenticated(!!token);
    } catch (error) {
      console.error('Error checking auth status:', error);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (username, password) => {
    try {
      setLoading(true);
      await gainzAPI.login(username, password);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      setIsAuthenticated(false);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await gainzAPI.logout();
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  }, []);

  return {
    isAuthenticated,
    loading,
    login,
    logout,
    checkAuthStatus,
  };
};

// ===========================================
// HOOK: useExercises - Manejo de ejercicios
// ===========================================

export const useExercises = (version = 'v2') => {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchExercises = useCallback(async (options = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      let data;
      if (version === 'v1') {
        data = await gainzAPI.getExercisesV1(options);
      } else {
        data = await gainzAPI.getExercisesV2(options);
      }
      
      setExercises(data);
      return data;
    } catch (err) {
      const errorMessage = err.message || 'Error fetching exercises';
      setError(errorMessage);
      console.error('Error fetching exercises:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, [version]);

  const searchExercises = useCallback(async (query, filters = {}) => {
    return await fetchExercises({ query, ...filters });
  }, [fetchExercises]);

  const filterExercises = useCallback(async (filters) => {
    return await fetchExercises(filters);
  }, [fetchExercises]);

  const refreshExercises = useCallback(() => {
    return fetchExercises();
  }, [fetchExercises]);

  return {
    exercises,
    loading,
    error,
    fetchExercises,
    searchExercises,
    filterExercises,
    refreshExercises,
  };
};

// ===========================================
// HOOK: useExercise - Ejercicio individual
// ===========================================

export const useExercise = (exerciseId, version = 'v2') => {
  const [exercise, setExercise] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchExercise = useCallback(async (id = exerciseId) => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      
      let data;
      if (version === 'v1') {
        data = await gainzAPI.getExerciseV1(id);
      } else {
        data = await gainzAPI.getExerciseV2(id);
      }
      
      setExercise(data);
      return data;
    } catch (err) {
      const errorMessage = err.message || 'Error fetching exercise';
      setError(errorMessage);
      console.error('Error fetching exercise:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [exerciseId, version]);

  useEffect(() => {
    if (exerciseId) {
      fetchExercise();
    }
  }, [exerciseId, fetchExercise]);

  return {
    exercise,
    loading,
    error,
    fetchExercise,
    refetch: () => fetchExercise(exerciseId),
  };
};

// ===========================================
// HOOK: useExerciseManagement - CRUD operations
// ===========================================

export const useExerciseManagement = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createExercise = useCallback(async (exerciseData) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await gainzAPI.createExerciseV2(exerciseData);
      return { success: true, data: result };
    } catch (err) {
      const errorMessage = err.message || 'Error creating exercise';
      setError(errorMessage);
      console.error('Error creating exercise:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const updateExercise = useCallback(async (exerciseId, exerciseData) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await gainzAPI.updateExerciseV2(exerciseId, exerciseData);
      return { success: true, data: result };
    } catch (err) {
      const errorMessage = err.message || 'Error updating exercise';
      setError(errorMessage);
      console.error('Error updating exercise:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteExercise = useCallback(async (exerciseId) => {
    try {
      setLoading(true);
      setError(null);
      
      await gainzAPI.deleteExerciseV2(exerciseId);
      return { success: true };
    } catch (err) {
      const errorMessage = err.message || 'Error deleting exercise';
      setError(errorMessage);
      console.error('Error deleting exercise:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    createExercise,
    updateExercise,
    deleteExercise,
  };
};

// ===========================================
// HOOK: useImageUpload - Subida de imágenes
// ===========================================

export const useImageUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const uploadImage = useCallback(async (imageFile) => {
    try {
      setUploading(true);
      setError(null);
      
      const result = await gainzAPI.uploadImage(imageFile);
      return { success: true, data: result };
    } catch (err) {
      const errorMessage = err.message || 'Error uploading image';
      setError(errorMessage);
      console.error('Error uploading image:', err);
      return { success: false, error: errorMessage };
    } finally {
      setUploading(false);
    }
  }, []);

  return {
    uploading,
    error,
    uploadImage,
  };
};

// ===========================================
// HOOK: useApiStatus - Estado de la API
// ===========================================

export const useApiStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkStatus = useCallback(async () => {
    try {
      setLoading(true);
      const healthData = await gainzAPI.healthCheck();
      const apiInfo = await gainzAPI.getApiInfo();
      
      setStatus({
        health: healthData,
        info: apiInfo,
        isOnline: true,
      });
    } catch (error) {
      console.error('API status check failed:', error);
      setStatus({
        health: null,
        info: null,
        isOnline: false,
        error: error.message,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  return {
    status,
    loading,
    checkStatus,
  };
};

// ===========================================
// EJEMPLOS DE USO DE LOS HOOKS
// ===========================================

/*
// En tu componente React Native:

import React from 'react';
import { View, Text, FlatList, Button, Alert } from 'react-native';
import { useExercises, useAuth, useExerciseManagement } from './GainzHooks';

const ExercisesScreen = () => {
  const { exercises, loading, error, searchExercises, refreshExercises } = useExercises('v2');
  const { isAuthenticated, login, logout } = useAuth();
  const { createExercise, loading: creating } = useExerciseManagement();

  const handleSearch = async () => {
    await searchExercises('push', { muscle: 'chest' });
  };

  const handleCreateExercise = async () => {
    if (!isAuthenticated) {
      const result = await login('admin', 'password');
      if (!result.success) {
        Alert.alert('Error', 'Authentication failed');
        return;
      }
    }

    const newExercise = {
      id: Date.now(),
      slug: 'new-exercise',
      name: 'New Exercise',
      description: 'A new exercise description',
      primary_muscle: 'chest',
      difficulty: 'beginner',
      steps: [{ order: 1, instruction: 'Do the exercise' }],
    };

    const result = await createExercise(newExercise);
    if (result.success) {
      Alert.alert('Success', 'Exercise created!');
      refreshExercises();
    } else {
      Alert.alert('Error', result.error);
    }
  };

  if (loading) return <Text>Loading...</Text>;
  if (error) return <Text>Error: {error}</Text>;

  return (
    <View>
      <Button title="Search Exercises" onPress={handleSearch} />
      <Button title="Create Exercise" onPress={handleCreateExercise} disabled={creating} />
      
      <FlatList
        data={exercises}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={{ padding: 10 }}>
            <Text style={{ fontWeight: 'bold' }}>{item.name}</Text>
            <Text>{item.primary_muscle}</Text>
            <Text>{item.description}</Text>
          </View>
        )}
      />
    </View>
  );
};

export default ExercisesScreen;
*/
