import React, { useState, useEffect } from 'react';
import { collection, addDoc, deleteDoc, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

const AddressesScreen = ({ navigate, userId, db }) => {
    const [addresses, setAddresses] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [newAddressName, setNewAddressName] = useState('');
    const [newAddressDetail, setNewAddressDetail] = useState('');

    const headerColor = 'bg-indigo-700 text-white';

    // Función para obtener la referencia de la colección de direcciones privada
    const getAddressCollectionRef = () => {
        if (!db || !userId) return null;
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        // Ruta privada: /artifacts/{appId}/users/{userId}/addresses
        return collection(db, `artifacts/${appId}/users/${userId}/addresses`);
    };

    // Efecto para escuchar las direcciones en tiempo real
    useEffect(() => {
        const addressesRef = getAddressCollectionRef();

        if (!addressesRef) {
            console.error("Firestore o UserId no están disponibles para cargar direcciones.");
            setIsLoading(false);
            return;
        }

        const unsubscribe = onSnapshot(addressesRef, (snapshot) => {
            const loadedAddresses = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data()
            }));
            setAddresses(loadedAddresses);
            setIsLoading(false);
            console.log("Firestore: Direcciones cargadas en tiempo real.");
        }, (error) => {
            console.error("Firestore Error en onSnapshot (Direcciones):", error);
            setIsLoading(false);
        });

        return () => unsubscribe();
    }, [db, userId]);

    // Función para añadir una nueva dirección
    const handleAddAddress = async () => {
        if (!newAddressName.trim() || !newAddressDetail.trim()) return;

        const addressesRef = getAddressCollectionRef();
        if (!addressesRef) return;

        const newAddress = {
            name: newAddressName.trim(), // Ej: Casa, Oficina, Gimnasio
            detail: newAddressDetail.trim(), // Ej: Calle Falsa 123, Apto 4A
            createdAt: Date.now(),
        };

        try {
            await addDoc(addressesRef, newAddress);
            setNewAddressName('');
            setNewAddressDetail('');
            console.log("Firestore: Nueva dirección agregada.");
        } catch (error) {
            console.error("Error al añadir dirección:", error);
            // Usar un modal o un mensaje de error en la UI en lugar de alert
        }
    };

    // Función para eliminar una dirección
    const handleDeleteAddress = async (id) => {
        const addressesRef = getAddressCollectionRef();
        if (!addressesRef) return;

        try {
            await deleteDoc(doc(addressesRef, id));
            console.log("Firestore: Dirección eliminada.");
        } catch (error) {
            console.error("Error al eliminar dirección:", error);
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                <p className="mt-4 text-gray-600 font-medium">Cargando direcciones...</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl">
            {/* Encabezado */}
            <div className={`${headerColor} p-4 flex items-center shadow-md`}>
                <button 
                    className="text-white text-3xl hover:opacity-80 transition mr-4" 
                    onClick={() => navigate('profile')} // Volver a Perfil
                >
                    &larr;
                </button>
                <h1 className="text-xl font-bold flex-1">Mis Direcciones</h1>
            </div>

            {/* Formulario para añadir nueva dirección */}
            <div className="p-4 bg-white shadow-lg mb-4">
                <h3 className="text-lg font-bold text-gray-800 mb-3">Añadir Nueva Ubicación</h3>
                <input
                    type="text"
                    placeholder="Ej: Casa"
                    value={newAddressName}
                    onChange={(e) => setNewAddressName(e.target.value)}
                    className="w-full p-3 mb-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                />
                <textarea
                    placeholder="Detalle: Calle Falsa 123, Apto 4A"
                    value={newAddressDetail}
                    onChange={(e) => setNewAddressDetail(e.target.value)}
                    className="w-full p-3 mb-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                    rows="2"
                />
                <button
                    onClick={handleAddAddress}
                    className="w-full py-3 bg-indigo-600 text-white font-bold rounded-xl shadow-md hover:bg-indigo-700 transition duration-200"
                >
                    Guardar Dirección
                </button>
            </div>

            {/* Lista de Direcciones Guardadas */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                <h3 className="text-lg font-bold text-gray-700">Direcciones Guardadas ({addresses.length})</h3>
                {addresses.length === 0 ? (
                    <div className="text-center p-6 bg-white rounded-xl shadow-md text-gray-500">
                        Aún no tienes direcciones guardadas.
                    </div>
                ) : (
                    addresses.map((address) => (
                        <div 
                            key={address.id} 
                            className="flex items-center justify-between p-4 bg-white rounded-xl shadow-md border-l-4 border-indigo-500"
                        >
                            <div className="flex-1 min-w-0 pr-4">
                                <h4 className="font-semibold text-gray-800 truncate">{address.name}</h4>
                                <p className="text-sm text-gray-500 truncate">{address.detail}</p>
                            </div>
                            <button
                                onClick={() => handleDeleteAddress(address.id)}
                                className="text-red-500 hover:text-red-700 p-2 rounded-full transition"
                                title="Eliminar Dirección"
                            >
                                🗑️
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default AddressesScreen;