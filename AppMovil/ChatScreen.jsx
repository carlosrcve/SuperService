
import React, { useState, useEffect, useRef } from 'react';
// IMPORTACIÓN FIJA: Ahora recibe 'db' y 'userId' como props
import { collection, query, orderBy, onSnapshot, addDoc, serverTimestamp, doc, setDoc } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const ChatScreen = ({ navigate, partnerId, partnerName, chatId, db, userId }) => { // RECIBIENDO PROPS
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        let unsubscribe = () => {};

        // Se inicializa solo si db, userId y chatId están presentes
        if (!userId || !db || !chatId) return;

        // Ruta de la subcolección de mensajes dentro del chat
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const messagesPath = `artifacts/${appId}/users/${userId}/chats/${chatId}/messages`;
        
        // Consulta para obtener mensajes ordenados por timestamp
        const q = query(collection(db, messagesPath), orderBy("timestamp"));

        unsubscribe = onSnapshot(q, (snapshot) => {
            const fetchedMessages = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data(),
                timestamp: doc.data().timestamp?.toDate ? doc.data().timestamp.toDate() : new Date(),
            }));
            setMessages(fetchedMessages);
            // Esperar un ciclo para asegurar que el DOM se actualice antes de scrollear
            setTimeout(scrollToBottom, 100); 
        }, (error) => {
            console.error("Error fetching messages:", error);
        });

        return () => unsubscribe();
    }, [chatId, db, userId]); // Dependencias: db, userId, chatId

    /**
     * Enviar el mensaje a Firestore
     */
    const handleSendMessage = async (e) => {
        e.preventDefault();
        const trimmedMessage = newMessage.trim();
        if (!trimmedMessage || !userId || !chatId || !db) return; // Validación de db

        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const messagesPath = `artifacts/${appId}/users/${userId}/chats/${chatId}/messages`;
        const chatDocRef = doc(db, `artifacts/${appId}/users/${userId}/chats`, chatId);
        
        try {
            // 1. Agregar el nuevo mensaje a la subcolección
            await addDoc(collection(db, messagesPath), {
                text: trimmedMessage,
                senderId: userId,
                timestamp: serverTimestamp(),
            });

            // 2. Actualizar el documento principal del chat para mostrar el último mensaje y hora
            await setDoc(chatDocRef, {
                lastMessageText: trimmedMessage,
                lastMessageTime: serverTimestamp(),
                // Asegurar que el nombre y el partnerId existan en el documento del chat
                partnerId: partnerId,
                partnerName: partnerName,
            }, { merge: true }); // Usamos merge para solo actualizar estos campos
            
            setNewMessage('');

        } catch (error) {
            console.error("Error sending message:", error);
            console.error("Error al enviar mensaje. Revisa la consola.");
        }
    };
    
    // Función de ayuda para formatear la hora
    const formatTime = (date) => {
        if (!date || isNaN(date.getTime())) return '';
        const options = { hour: '2-digit', minute: '2-digit' };
        return date.toLocaleTimeString([], options);
    };

    const ChatBubble = ({ message }) => {
        const isMe = message.senderId === userId;
        return (
            <div className={`flex mb-4 ${isMe ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-lg px-4 py-2 rounded-xl shadow-md ${
                    isMe ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-white text-gray-800 rounded-tl-none border border-gray-200'
                }`}>
                    <p className="text-sm break-words">{message.text}</p>
                    <span className={`block text-right text-xs mt-1 ${isMe ? 'text-indigo-200' : 'text-gray-500'}`}>
                        {formatTime(message.timestamp)}
                    </span>
                </div>
            </div>
        );
    };


    return (
        <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl">
            {/* Encabezado del Chat */}
            <div className="bg-indigo-700 p-4 flex items-center shadow-md">
                <button 
                    className="text-white text-3xl hover:opacity-80 transition mr-4" 
                    onClick={() => navigate('chatList')} 
                >
                    &larr;
                </button>
                <h1 className="text-xl font-bold text-white flex-1">{partnerName}</h1>
            </div>

            {/* Área de Mensajes (Scrollable) */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {messages.map(msg => (
                    <ChatBubble key={msg.id} message={msg} />
                ))}
                <div ref={messagesEndRef} /> {/* Punto de anclaje para el scroll */}
            </div>

            {/* Input para Nuevo Mensaje */}
            <div className="p-3 bg-white border-t border-gray-200">
                <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
                    <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        className="flex-1 p-3 rounded-full border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                        placeholder="Escribe un mensaje..."
                        disabled={!chatId}
                    />
                    <button
                        type="submit"
                        className={`p-3 rounded-full shadow-md transition duration-200 
                            ${!newMessage.trim() || !chatId ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'}`}
                        disabled={!newMessage.trim() || !chatId}
                    >
                         <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatScreen;