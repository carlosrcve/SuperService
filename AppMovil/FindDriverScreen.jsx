
import React, { useState, useEffect } from 'react';

const FindDriverScreen = ({ navigate, rideDetails }) => {
    const [status, setStatus] = useState('Buscando conductor cercano...');
    const [progress, setProgress] = useState(0);
    const [isFound, setIsFound] = useState(false);

    useEffect(() => {
        // Simulación de la barra de progreso
        const progressInterval = setInterval(() => {
            setProgress(prev => {
                if (prev < 90) {
                    return prev + 10;
                }
                return prev;
            });
        }, 500);

        // Simulación de que se encontró un conductor después de 4 segundos
        const findDriverTimeout = setTimeout(() => {
            clearInterval(progressInterval);
            setStatus('¡Conductor Encontrado! 🎉');
            setProgress(100);
            setIsFound(true);
        }, 4000);

        // Después de 6 segundos, navegar a una pantalla de seguimiento (simulada aquí como 'home')
        const redirectTimeout = setTimeout(() => {
            navigate('home', { message: 'Viaje confirmado con el conductor Juan Pérez.' });
        }, 6000);

        // Limpieza de intervalos y timeouts al desmontar
        return () => {
            clearInterval(progressInterval);
            clearTimeout(findDriverTimeout);
            clearTimeout(redirectTimeout);
        };
    }, [navigate]);

    return (
        <div className="flex flex-col h-screen bg-gray-900 font-inter max-w-sm mx-auto shadow-2xl items-center justify-center p-6 text-white">
            
            <div className="text-center w-full">
                
                {/* Icono de búsqueda */}
                <div className={`mb-6 text-7xl transition-all duration-1000 ${isFound ? 'text-green-400 scale-110' : 'text-indigo-400 animate-pulse'}`}>
                    {isFound ? '✅' : '🔍'}
                </div>

                {/* Estado de la búsqueda */}
                <h1 className="text-2xl font-bold mb-2">{status}</h1>
                <p className="text-gray-400 text-sm mb-8">
                    {isFound ? 'Dirigiéndote a la pantalla de seguimiento...' : 'Estamos buscando el conductor mejor calificado.'}
                </p>

                {/* Barra de Progreso */}
                <div className="w-full bg-gray-700 rounded-full h-2.5 mb-8">
                    <div 
                        className={`h-2.5 rounded-full transition-all duration-500 ease-out ${isFound ? 'bg-green-500' : 'bg-indigo-500'}`}
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>

                {/* Detalles del Viaje */}
                <div className="bg-gray-800 p-4 rounded-xl shadow-lg border border-gray-700 text-left">
                    <h3 className="text-lg font-semibold mb-2 text-indigo-300">Detalles del Viaje</h3>
                    <p className="text-sm">
                        <span className="font-medium text-gray-400">Origen:</span> {rideDetails.origin}
                    </p>
                    <p className="text-sm mt-1">
                        <span className="font-medium text-gray-400">Destino:</span> {rideDetails.destination}
                    </p>
                    <p className="text-xl font-bold mt-3 text-green-400">
                        Tarifa: ${rideDetails.fare}
                    </p>
                </div>
            </div>

            {/* Botón de Cancelar */}
            {!isFound && (
                <button
                    onClick={() => navigate('transporte')}
                    className="mt-8 px-6 py-2 border border-red-500 text-red-500 rounded-full font-semibold hover:bg-red-500 hover:text-white transition duration-300"
                >
                    Cancelar Solicitud
                </button>
            )}
        </div>
    );
};

export default FindDriverScreen;