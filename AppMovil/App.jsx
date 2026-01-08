import React, { useState, useEffect } from 'react';
import TransporteScreen from './TransporteScreen'; 
import DomiciliosScreen from './DomiciliosScreen'; 
import StoreDetailScreen from './StoreDetailScreen'; 
import CheckoutScreen from './CheckoutScreen'; 
import ChatListScreen from './ChatListScreen'; 
import ChatScreen from './ChatScreen'; 
// Importaciones de Firebase integradas en App.jsx
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
import { getFirestore, setLogLevel } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

// Configuración de Estilos
const baseStyles = {
    screenContainer: "flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl",
    navButton: "p-4 text-center font-bold rounded-xl shadow-lg transition duration-200",
};

// --- PANTALLA DE INICIO (HOME) ---
const HomeScreen = ({ navigate }) => (
    <div className={baseStyles.screenContainer}>
        {/* Cabecera */}
        <header className="bg-indigo-700 text-white p-6 flex justify-between items-center rounded-b-xl shadow-md">
            <h1 className="text-2xl font-extrabold">SuperApp</h1>
            <span className="text-sm">Hola, Carlos 👋</span>
        </header>

        {/* Contenido Principal con Opciones */}
        <main className="flex-1 p-6 overflow-y-auto">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Selecciona un Servicio</h2>

            {/* Opción 1: Transporte */}
            <button
                className={`${baseStyles.navButton} bg-indigo-600 text-white hover:bg-indigo-700 w-full mb-4 flex items-center justify-between`}
                onClick={() => navigate('transporte')}
            >
                <span className="text-3xl mr-4">🚗</span>
                <span className="flex-1 text-left">
                    Transporte de Personas
                    <p className="text-sm font-normal opacity-90 mt-0.5">Viajes rápidos y seguros.</p>
                </span>
                
            </button>

            {/* Opción 2: Domicilios */}
            <button
                className={`${baseStyles.navButton} bg-emerald-500 text-white hover:bg-emerald-600 w-full mb-4 flex items-center justify-between`}
                onClick={() => navigate('domicilios')}
            >
                <span className="text-3xl mr-4">🍔</span>
                <span className="flex-1 text-left">
                    Domicilios & Pedidos
                    <p className="text-sm font-normal opacity-90 mt-0.5">Restaurantes, tiendas y más.</p>
                </span>
            </button>
            
            {/* Opción 3: Chat/Mensajería (Activada) */}
            <button
                className={`${baseStyles.navButton} bg-pink-500 text-white hover:bg-pink-600 w-full flex items-center justify-between`}
                onClick={() => navigate('chatList')}
            >
                <span className="text-3xl mr-4">💬</span>
                <span className="flex-1 text-left">
                    Chat y Mensajería
                    <p className="text-sm font-normal opacity-90 mt-0.5">Comunícate en tiempo real.</p>
                </span>
            </button>

        </main>
    </div>
);


// --- COMPONENTE PRINCIPAL (Maneja el ruteo y Firebase) ---
const App = () => {
    // ESTADO DEL ROUTER
    const [currentScreen, setCurrentScreen] = useState('home');
    const [screenData, setScreenData] = useState(null);
    
    // ESTADO DE FIREBASE
    const [dbInstance, setDbInstance] = useState(null);
    const [authInstance, setAuthInstance] = useState(null); 
    const [currentUserId, setCurrentUserId] = useState(null);
    const [isAuthReady, setIsAuthReady] = useState(false);

    // FUNCIÓN DE INICIALIZACIÓN DE FIREBASE (EMBEDIDA)
    useEffect(() => {
        // Habilitar logs de Firebase para depuración
        setLogLevel('Debug');

        // Variables globales proporcionadas por el entorno de Canvas (requeridas)
        const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : null;
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
        
        if (!firebaseConfig) {
            console.error("Firebase Configuration is missing. Cannot initialize Firestore.");
            setCurrentUserId(crypto.randomUUID()); // Usar un ID temporal si no hay config
            setIsAuthReady(true);
            return;
        }

        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);
        const auth = getAuth(app);
        
        setDbInstance(db);
        setAuthInstance(auth);

        const unsubscribe = onAuthStateChanged(auth, async (user) => {
            if (user) {
                // El usuario ya está autenticado
                setCurrentUserId(user.uid);
                setIsAuthReady(true);
                unsubscribe();
            } else {
                // Si no hay usuario, intenta iniciar sesión
                let userIdTemp;
                try {
                    if (initialAuthToken) {
                        const userCredential = await signInWithCustomToken(auth, initialAuthToken);
                        userIdTemp = userCredential.user.uid;
                    } else {
                        const userCredential = await signInAnonymously(auth);
                        userIdTemp = userCredential.user.uid;
                    }
                } catch (error) {
                    console.error("Authentication failed:", error.message);
                    // Si falla, usamos un ID temporal
                    userIdTemp = crypto.randomUUID(); 
                } finally {
                    setCurrentUserId(userIdTemp);
                    setIsAuthReady(true);
                    unsubscribe();
                    console.log("Firebase Auth Initialization Finished. User ID:", userIdTemp);
                }
            }
        });
        
    }, []);

    const navigate = (screenName, data = null) => {
        setScreenData(data);
        setCurrentScreen(screenName);
    };
    
    const selectStore = (store) => {
        navigate('storeDetail', store);
    };
    
    const startChat = (partnerId, partnerName, chatId = null) => {
        const effectiveChatId = chatId || partnerId; 
        navigate('chatScreen', { partnerId, partnerName, chatId: effectiveChatId });
    };


    if (!isAuthReady) {
        return (
            <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl items-center justify-center">
                <p className="text-xl text-indigo-700 font-semibold">Iniciando Servicios de App...</p>
                <p className="text-sm text-gray-500 mt-2">Autenticando usuario (Firestore)...</p>
            </div>
        );
    }

    const renderScreen = () => {
        // Pasamos dbInstance y currentUserId a los componentes de chat
        const chatProps = { navigate, db: dbInstance, userId: currentUserId };

        switch (currentScreen) {
            case 'transporte':
                return <TransporteScreen navigate={navigate} />;
            case 'domicilios':
                return <DomiciliosScreen navigate={navigate} selectStore={selectStore} />;
            case 'storeDetail':
                return <StoreDetailScreen navigate={navigate} store={screenData} />;
            case 'checkout':
                return <CheckoutScreen navigate={navigate} store={screenData?.store} cart={screenData?.cart} />;
            case 'chatList':
                return <ChatListScreen {...chatProps} startChat={startChat} />;
            case 'chatScreen':
                return <ChatScreen 
                    {...chatProps}
                    partnerId={screenData.partnerId} 
                    partnerName={screenData.partnerName} 
                    chatId={screenData.chatId} 
                />;
            case 'home':
            default:
                return <HomeScreen navigate={navigate} />;
        }
    };

    return renderScreen();
};

export default App;