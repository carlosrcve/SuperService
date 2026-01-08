import React, { useState, useEffect } from 'react';
import { db, initializeAuth, currentUserId } from './firebase_setup';
import { collection, query, where, onSnapshot } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

// Estilos
const headerColor = 'bg-indigo-700 text-white';

const ChatListScreen = ({ navigate, startChat }) => {
    const [chats, setChats] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [userId, setUserId] = useState(null);

    useEffect(() => {
        let unsubscribe = () => {};

        const setup = async () => {
            const id = await initializeAuth();
            setUserId(id);
            if (!id || !db) {
                setIsLoading(false);
                return;
            }

            // Path de la colección de chats: /artifacts/{appId}/users/{userId}/chats
            const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
            const chatsCollectionPath = `artifacts/${appId}/users/${id}/chats`;
            const q = collection(db, chatsCollectionPath);

            // Escuchar cambios en tiempo real
            unsubscribe = onSnapshot(q, (snapshot) => {
                const fetchedChats = snapshot.docs.map(doc => {
                    const data = doc.data();
                    const partnerName = data.partnerId === id ? "Tú mismo" : (data.partnerName || "Usuario SuperApp");
                    return {
                        id: doc.id,
                        ...data,
                        partnerName: partnerName,
                        lastMessageTime: data.lastMessageTime?.toDate ? data.lastMessageTime.toDate() : new Date(),
                    };
                }).sort((a, b) => b.lastMessageTime.getTime() - a.lastMessageTime.getTime()); // Ordenar por hora
                
                setChats(fetchedChats);
                setIsLoading(false);
            }, (error) => {
                console.error("Error fetching chats:", error);
                setIsLoading(false);
            });
        };

        setup();

        return () => unsubscribe();
    }, []);

    // Función de ayuda para formatear la hora
    const formatTime = (date) => {
        if (!date) return '';
        const options = { hour: '2-digit', minute: '2-digit' };
        return date.toLocaleTimeString([], options);
    };

    if (isLoading) {
        return (
            <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl items-center justify-center">
                <p className="text-xl text-indigo-700 font-semibold">Cargando Chats...</p>
                <p className="text-xs text-gray-500 mt-2">ID de Usuario: {userId || 'No autenticado'}</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl">
            {/* Encabezado */}
            <div className={`${headerColor} p-4 flex items-center shadow-md`}>
                <button 
                    className="text-white text-3xl hover:opacity-80 transition mr-4" 
                    onClick={() => navigate('home')} 
                >
                    &larr;
                </button>
                <h1 className="text-xl font-bold text-white flex-1">Bandeja de Mensajes</h1>
            </div>

            {/* Lista de Chats */}
            <div className="flex-1 overflow-y-auto p-2">
                {chats.length === 0 ? (
                    <div className="text-center p-8 text-gray-500">
                        <p className="mb-2 text-3xl">💬</p>
                        <p>Aún no tienes conversaciones. ¡Comienza una ahora!</p>
                        {/* Botón de ejemplo para crear un chat (simulado) */}
                        <button 
                            className="mt-4 px-4 py-2 bg-indigo-500 text-white rounded-lg shadow-md hover:bg-indigo-600 transition"
                            onClick={() => startChat("MockPartnerId123", "Repartidor Juan")}
                        >
                            Iniciar Chat de Prueba
                        </button>
                    </div>
                ) : (
                    chats.map(chat => (
                        <button
                            key={chat.id}
                            className="w-full bg-white p-4 rounded-xl shadow-sm flex items-center transition duration-150 hover:bg-indigo-50 border-b border-gray-100"
                            onClick={() => startChat(chat.partnerId, chat.partnerName, chat.id)}
                        >
                            {/* Icono del socio */}
                            <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mr-4">
                                <span className="text-2xl">{chat.partnerIcon || '👤'}</span>
                            </div>
                            
                            <div className="flex-1 text-left min-w-0">
                                <div className="flex justify-between items-start">
                                    <p className="text-lg font-semibold text-gray-900 truncate">
                                        {chat.partnerName}
                                    </p>
                                    <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                                        {formatTime(chat.lastMessageTime)}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-500 truncate mt-0.5">
                                    {chat.lastMessageText || "Toca para iniciar conversación."}
                                </p>
                            </div>
                        </button>
                    ))
                )}
            </div>
            {/* Mostrar el ID del usuario actual para facilitar la depuración y prueba */}
            <div className="p-2 text-xs text-center text-gray-400 border-t">
                Tu ID de Firebase: {userId}
            </div>
        </div>
    );
};

export default ChatListScreen;