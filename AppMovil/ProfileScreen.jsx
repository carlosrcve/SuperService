import React from 'react';

const ProfileScreen = ({ navigate, userId }) => {
    // Datos simulados del usuario. En una aplicación real, se cargarían desde Firestore.
    const userProfile = {
        name: "Carlos Hernández",
        email: "carlos.h@ejemplo.com",
        phone: "+58 412 555 1234",
        memberSince: "Agosto 2023",
        profilePicture: "https://placehold.co/100x100/34D399/ffffff?text=CH", // Placeholder para foto de perfil
    };

    const headerColor = 'bg-indigo-700 text-white';

    const SettingItem = ({ icon, title, description, action }) => (
        <button 
            onClick={action} 
            className="flex items-center p-4 bg-white rounded-xl shadow-sm hover:bg-gray-50 transition duration-150 w-full text-left"
        >
            <span className="text-2xl mr-4 text-indigo-500">{icon}</span>
            <div className="flex-1">
                <h4 className="font-semibold text-gray-800">{title}</h4>
                <p className="text-sm text-gray-500">{description}</p>
            </div>
            <span className="text-gray-400 text-lg">&gt;</span>
        </button>
    );

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
                <h1 className="text-xl font-bold flex-1">Mi Perfil</h1>
            </div>

            {/* Contenido Principal */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                
                {/* Tarjeta de Información Básica */}
                <div className="bg-white p-6 rounded-2xl shadow-lg flex items-center">
                    <img 
                        src={userProfile.profilePicture} 
                        alt="Foto de Perfil" 
                        className="w-16 h-16 rounded-full object-cover mr-4 ring-2 ring-indigo-500"
                    />
                    <div>
                        <h2 className="text-xl font-bold text-gray-800">{userProfile.name}</h2>
                        <p className="text-sm text-gray-500">{userProfile.email}</p>
                        <p className="text-xs text-gray-400 mt-1">Miembro desde {userProfile.memberSince}</p>
                    </div>
                </div>

                {/* Sección de Cuenta */}
                <h3 className="text-lg font-bold text-gray-700">Configuración de Cuenta</h3>
                <div className="space-y-3">
                    <SettingItem 
                        icon="📍" 
                        title="Direcciones Guardadas" 
                        description="Gestiona tus domicilios y lugares de trabajo." 
                        action={() => console.log("Navegar a Direcciones")}
                    />
                    <SettingItem 
                        icon="💳" 
                        title="Métodos de Pago" 
                        description="Añade o edita tarjetas y billeteras." 
                        action={() => console.log("Navegar a Pagos")}
                    />
                    <SettingItem 
                        icon="🔒" 
                        title="Seguridad y Privacidad" 
                        description="Cambiar contraseña y ajustes de privacidad." 
                        action={() => console.log("Navegar a Seguridad")}
                    />
                </div>
                
                {/* Sección de Historial */}
                <h3 className="text-lg font-bold text-gray-700 pt-2">Actividad</h3>
                <div className="space-y-3">
                    <SettingItem 
                        icon="📜" 
                        title="Historial de Pedidos" 
                        description="Revisa tus órdenes pasadas y facturas." 
                        action={() => console.log("Navegar a Historial")}
                    />
                    <SettingItem 
                        icon="🚗" 
                        title="Viajes Anteriores" 
                        description="Detalles de tus servicios de transporte." 
                        action={() => console.log("Navegar a Viajes")}
                    />
                </div>

                {/* Información de Depuración (Para el entorno Canvas) */}
                <div className="text-center p-3 bg-indigo-100 rounded-xl text-xs text-gray-600 break-words">
                    <p className="font-semibold mb-1">ID de Usuario (Firebase):</p>
                    <p className="text-indigo-800">{userId || "Cargando..."}</p>
                </div>
                
                {/* Botón de Cierre de Sesión (Simulado) */}
                <button
                    onClick={() => console.log("Simulando Cierre de Sesión")}
                    className="w-full py-3 bg-red-500 text-white font-bold rounded-xl shadow-md hover:bg-red-600 transition duration-200"
                >
                    Cerrar Sesión
                </button>
            </div>
        </div>
    );
};

export default ProfileScreen;