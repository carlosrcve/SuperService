import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, doc, setDoc, collection, onSnapshot, query, addDoc, serverTimestamp, setLogLevel } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

// Habilitar logs de Firebase para depuración
setLogLevel('Debug');

// Variables globales proporcionadas por el entorno de Canvas (requeridas)
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : null;
const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

// Inicialización
let app;
let db;
let auth;
let userId = null; // ID del usuario autenticado
let isAuthReady = false; // Indica si la autenticación inicial ha terminado

if (firebaseConfig) {
    app = initializeApp(firebaseConfig);
    db = getFirestore(app);
    auth = getAuth(app);
} else {
    console.error("Firebase Configuration is missing. Cannot initialize Firestore.");
}

/**
 * Proceso de Autenticación
 * Utiliza el token si existe, sino, inicia sesión anónimamente.
 */
const initializeAuth = () => {
    return new Promise((resolve) => {
        if (!auth) {
            isAuthReady = true;
            resolve(null);
            return;
        }

        const unsubscribe = onAuthStateChanged(auth, async (user) => {
            if (user) {
                // El usuario ya está autenticado (o la sesión anterior se cargó)
                userId = user.uid;
                isAuthReady = true;
                unsubscribe(); // Detener el listener una vez que la autenticación inicial se completa
                console.log("Firebase Auth Ready. User ID:", userId);
                resolve(userId);
            } else {
                // Si no hay usuario, intenta iniciar sesión
                try {
                    if (initialAuthToken) {
                        const userCredential = await signInWithCustomToken(auth, initialAuthToken);
                        userId = userCredential.user.uid;
                    } else {
                        const userCredential = await signInAnonymously(auth);
                        userId = userCredential.user.uid;
                    }
                    console.log("Authentication successful. User ID:", userId);
                } catch (error) {
                    console.error("Authentication failed:", error.message);
                    // Si falla, usamos un ID temporal
                    userId = crypto.randomUUID(); 
                } finally {
                    isAuthReady = true;
                    unsubscribe();
                    console.log("Firebase Auth Initialization Finished. User ID:", userId);
                    resolve(userId);
                }
            }
        });
    });
};

// Exportar funciones y objetos clave
export { db, auth, initializeAuth, userId as currentUserId, isAuthReady };