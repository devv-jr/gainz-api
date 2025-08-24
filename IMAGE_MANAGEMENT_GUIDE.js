/**
 * 🖼️ GUÍA COMPLETA: MANEJO DE IMÁGENES EN GAINZAPI v2
 * 
 * IMPORTANTE: Hay 3 formas de manejar imágenes
 */

// ===========================================
// OPCIÓN 1: IMÁGENES ESTÁTICAS (RECOMENDADO PARA EJEMPLOS)
// ===========================================

// 1. Coloca imágenes en /static/images/ ANTES del deploy
// 2. Las imágenes se incluyen en el repositorio Git
// 3. Se sirven directamente desde el servidor

const STATIC_IMAGES_EXAMPLE = {
  // Estructura de ejercicio v2 con imágenes estáticas
  "images": [
    {
      "url": "https://tu-app.onrender.com/static/images/pushup-start.jpg",
      "type": "step",
      "width": 800,
      "height": 600
    },
    {
      "url": "https://tu-app.onrender.com/static/images/pushup-down.jpg",
      "type": "step", 
      "width": 800,
      "height": 600
    }
  ]
};

// ===========================================
// OPCIÓN 2: UPLOAD DINÁMICO (DESPUÉS DEL DEPLOY)
// ===========================================

// Función para subir imagen desde React Native
const uploadExerciseImage = async (imageUri, exerciseId) => {
  try {
    // 1. Preparar el archivo
    const formData = new FormData();
    formData.append('file', {
      uri: imageUri,
      type: 'image/jpeg',
      name: `exercise-${exerciseId}-${Date.now()}.jpg`
    });

    // 2. Subir imagen
    const uploadResponse = await fetch('https://tu-app.onrender.com/images/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      }
    });

    const uploadResult = await uploadResponse.json();
    // uploadResult.url = "/static/images/exercise-1001-1629789600000.jpg"

    // 3. Actualizar ejercicio con la nueva imagen
    const exerciseData = {
      // ... otros campos del ejercicio
      "images": [
        {
          "url": `https://tu-app.onrender.com${uploadResult.url}`,
          "type": "step",
          "width": 800,
          "height": 600
        }
      ]
    };

    // 4. Guardar ejercicio actualizado
    const updateResponse = await fetch(`https://tu-app.onrender.com/v2/exercises/${exerciseId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(exerciseData)
    });

    return await updateResponse.json();

  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
};

// ===========================================
// OPCIÓN 3: IMÁGENES EXTERNAS (URLs PÚBLICAS)
// ===========================================

const EXTERNAL_IMAGES_EXAMPLE = {
  "images": [
    {
      "url": "https://example.com/pushup-demo.gif",
      "type": "demonstration",
      "width": 400,
      "height": 300
    },
    {
      "url": "https://unsplash.com/photos/fitness-exercise.jpg",
      "type": "step",
      "width": 800,
      "height": 600
    }
  ]
};

// ===========================================
// FLUJO COMPLETO EN REACT NATIVE
// ===========================================

import React, { useState } from 'react';
import { View, Button, Image, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useAuth } from './GainzHooks';
import GainzAPI from './GainzAPI';

const ExerciseImageManager = ({ exerciseId }) => {
  const [uploading, setUploading] = useState(false);
  const { isAuthenticated, login } = useAuth();
  const gainzAPI = new GainzAPI();

  const pickAndUploadImage = async () => {
    try {
      // 1. Verificar autenticación
      if (!isAuthenticated) {
        const result = await login('admin', 'password');
        if (!result.success) {
          Alert.alert('Error', 'Debes autenticarte primero');
          return;
        }
      }

      // 2. Seleccionar imagen
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (result.canceled) return;

      setUploading(true);

      // 3. Subir imagen
      const uploadResult = await gainzAPI.uploadImage({
        uri: result.assets[0].uri,
        type: 'image/jpeg',
        name: `exercise-${exerciseId}-${Date.now()}.jpg`
      });

      if (!uploadResult.success) {
        Alert.alert('Error', 'No se pudo subir la imagen');
        return;
      }

      // 4. Obtener ejercicio actual
      const currentExercise = await gainzAPI.getExerciseV2(exerciseId);

      // 5. Agregar nueva imagen al ejercicio
      const updatedExercise = {
        ...currentExercise,
        images: [
          ...currentExercise.images,
          {
            url: `https://tu-app.onrender.com${uploadResult.data.url}`,
            type: "step",
            width: result.assets[0].width,
            height: result.assets[0].height
          }
        ],
        updated_at: new Date().toISOString()
      };

      // 6. Actualizar ejercicio
      const updateResult = await gainzAPI.updateExerciseV2(exerciseId, updatedExercise);

      if (updateResult.success) {
        Alert.alert('¡Éxito!', 'Imagen agregada al ejercicio');
      } else {
        Alert.alert('Error', 'No se pudo actualizar el ejercicio');
      }

    } catch (error) {
      console.error('Error completo:', error);
      Alert.alert('Error', error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <View>
      <Button 
        title={uploading ? "Subiendo..." : "Agregar Imagen"} 
        onPress={pickAndUploadImage}
        disabled={uploading}
      />
    </View>
  );
};

// ===========================================
// EJEMPLO COMPLETO: CREAR EJERCICIO V2 CON IMÁGENES
// ===========================================

const createCompleteExercise = async () => {
  const gainzAPI = new GainzAPI();
  
  // 1. Autenticarse
  await gainzAPI.login('admin', 'password');

  // 2. Crear ejercicio completo
  const newExercise = {
    id: 1002,
    slug: "deadlift-complete",
    name: "Peso Muerto",
    summary: "Ejercicio compuesto fundamental para posterior y core",
    description: "El peso muerto es uno de los mejores ejercicios para desarrollar fuerza general...",
    primary_muscle: "hamstrings",
    secondary_muscles: ["glutes", "lower-back", "traps"],
    equipment: ["barbell", "plates"],
    difficulty: "intermediate",
    steps: [
      {
        order: 1,
        title: "Preparación",
        instruction: "Coloca los pies a la anchura de caderas, barra sobre medios pies",
        duration_sec: null
      },
      {
        order: 2, 
        title: "Agarre",
        instruction: "Agarra la barra con agarre prono, manos a la anchura de hombros",
        duration_sec: null
      },
      {
        order: 3,
        title: "Levantamiento",
        instruction: "Levanta manteniendo espalda recta, extendiendo caderas y rodillas",
        duration_sec: 3
      }
    ],
    tips: [
      "Mantén la barra cerca del cuerpo durante todo el movimiento",
      "No redondees la espalda baja",
      "El movimiento inicia desde las caderas, no desde la espalda"
    ],
    images: [
      {
        url: "https://tu-app.onrender.com/static/images/deadlift-setup.jpg",
        type: "step",
        width: 800,
        height: 600
      },
      {
        url: "https://tu-app.onrender.com/static/images/deadlift-lift.jpg",
        type: "step", 
        width: 800,
        height: 600
      }
    ],
    tags: ["compound", "strength", "posterior-chain"],
    variations: [
      {
        name: "Peso muerto rumano",
        difficulty: "intermediate",
        description: "Enfoque en isquiosurales con menor flexión de rodillas"
      }
    ],
    estimated: {
      sets: 3,
      reps_min: 5,
      reps_max: 8,
      rest_sec: 180
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  // 3. Crear ejercicio
  const result = await gainzAPI.createExerciseV2(newExercise);
  
  if (result.success) {
    console.log('✅ Ejercicio creado con imágenes:', result.data);
  }
  
  return result;
};

export { 
  uploadExerciseImage, 
  ExerciseImageManager, 
  createCompleteExercise,
  STATIC_IMAGES_EXAMPLE,
  EXTERNAL_IMAGES_EXAMPLE 
};
