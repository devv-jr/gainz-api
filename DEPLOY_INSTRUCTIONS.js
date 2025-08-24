// ⚠️ INSTRUCCIONES PARA REACT NATIVE
// 
// 1. Instala AsyncStorage en tu proyecto React Native:
//    npm install @react-native-async-storage/async-storage
//
// 2. Cambia esta URL por la de tu API en Render:
//    const BASE_URL = 'https://tu-app-name.onrender.com';
//
// 3. Copia estos archivos a tu proyecto:
//    - GainzAPI.js → src/services/GainzAPI.js  
//    - GainzHooks.js → src/hooks/GainzHooks.js
//
// 4. Importa en tus componentes:
//    import GainzAPI from '../services/GainzAPI';
//    import { useExercises, useAuth } from '../hooks/GainzHooks';

console.log(`
🚀 TU API ESTÁ LISTA!

📍 URL de tu API: https://tu-app-name.onrender.com
📖 Documentación: https://tu-app-name.onrender.com/docs
🏥 Health Check: https://tu-app-name.onrender.com/health

🔧 PRÓXIMOS PASOS:
1. Espera a que Render termine el deploy
2. Actualiza la variable ORIGINS con tu URL real
3. Testa los endpoints en /docs
4. Configura React Native con los archivos JS

💡 TIPS:
- Los logs están en la tab "Logs" de Render
- Si hay errores, revisa las variables de entorno
- La primera carga puede ser lenta (cold start)
- Render duerme los servicios gratuitos tras 15min sin uso
`);

export const RENDER_DEPLOYMENT_CONFIG = {
  name: 'gainz-api',
  runtime: 'Python 3',
  buildCommand: 'pip install -r requirements.txt',
  startCommand: 'gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --log-file -',
  branch: 'main',
  environmentVariables: {
    SECRET_KEY: 'tu-clave-secreta-muy-larga-y-segura-aqui',
    ADMIN_USER: 'admin', 
    ADMIN_PASS: 'tu-password-super-seguro',
    ORIGINS: 'exp://127.0.0.1:19000,https://tu-app-name.onrender.com'
  }
};
