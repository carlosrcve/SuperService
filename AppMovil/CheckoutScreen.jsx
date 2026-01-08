import React, { useState } from 'react';

const CheckoutScreen = ({ navigate, store, cart }) => {
    const [isProcessing, setIsProcessing] = useState(false);
    
    if (!store || !cart || cart.length === 0) {
        return (
            <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl p-4">
                <p className="text-center text-red-500 mt-10">No hay elementos en el carrito para procesar.</p>
                <button onClick={() => navigate('domicilios')} className="mt-4 bg-indigo-500 text-white p-3 rounded-xl">
                    Volver a Domicilios
                </button>
            </div>
        );
    }

    // Calcular el total
    const subtotal = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
    const deliveryFee = 3.50;
    const total = (subtotal + deliveryFee).toFixed(2);
    
    // Simulación de la dirección de entrega
    const [deliveryAddress, setDeliveryAddress] = useState("Av. Principal #123, Torre Oeste, Apt. 5A");

    /**
     * Simula el procesamiento del pedido y navega a la pantalla de seguimiento.
     */
    const handlePlaceOrder = () => {
        setIsProcessing(true);
        setTimeout(() => {
            setIsProcessing(false);
            
            // Datos necesarios para la simulación de seguimiento
            const orderDetails = {
                storeName: store.name,
                total: total,
                destination: deliveryAddress,
            };

            // ¡Navegar a la nueva pantalla de seguimiento 3D!
            navigate('orderTracking', orderDetails);
        }, 1500);
    };

    const headerColor = 'bg-emerald-600 text-white';

    return (
        <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl">
            {/* Encabezado */}
            <div className={`${headerColor} p-4 flex items-center shadow-md`}>
                <button 
                    className="text-white text-3xl hover:opacity-80 transition mr-4" 
                    onClick={() => navigate('storeDetail', store)} 
                    disabled={isProcessing}
                >
                    &larr;
                </button>
                <h1 className="text-xl font-bold flex-1">Finalizar Pedido 🛒</h1>
            </div>

            {/* Contenido Principal */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                
                {/* Resumen de la Tienda */}
                <div className="bg-white p-4 rounded-xl shadow-lg">
                    <h2 className="text-lg font-bold text-gray-800 mb-1">{store.name}</h2>
                    <p className="text-sm text-gray-500">{store.cuisine}</p>
                </div>
                
                {/* Dirección de Entrega */}
                <div className="bg-white p-4 rounded-xl shadow-lg">
                    <h3 className="text-base font-semibold text-gray-700 mb-2">Dirección de Entrega</h3>
                    <input
                        type="text"
                        value={deliveryAddress}
                        onChange={(e) => setDeliveryAddress(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg p-2 focus:ring-emerald-500 focus:border-emerald-500"
                        disabled={isProcessing}
                    />
                </div>
                
                {/* Ítems del Carrito */}
                <div className="bg-white p-4 rounded-xl shadow-lg">
                    <h3 className="text-base font-semibold text-gray-700 mb-3">Tu Pedido</h3>
                    {cart.map((item, index) => (
                        <div key={index} className="flex justify-between text-sm py-1 border-b last:border-b-0">
                            <span className="text-gray-600">{item.quantity} x {item.name}</span>
                            <span className="font-medium">${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                    ))}
                </div>

                {/* Resumen de Pagos */}
                <div className="bg-white p-4 rounded-xl shadow-lg">
                    <div className="flex justify-between text-gray-600 text-sm mb-1">
                        <span>Subtotal:</span>
                        <span>${subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-gray-600 text-sm mb-3 border-b pb-2">
                        <span>Costo de Envío:</span>
                        <span>${deliveryFee.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between font-bold text-lg text-gray-800">
                        <span>Total a Pagar:</span>
                        <span>${total}</span>
                    </div>
                </div>

            </div>

            {/* Pie de Página: Botón de Pago */}
            <div className="p-4 border-t bg-white">
                <button
                    onClick={handlePlaceOrder}
                    disabled={isProcessing}
                    className={`w-full py-3 rounded-xl text-white font-bold text-lg shadow-xl transition duration-300 
                        ${isProcessing
                            ? 'bg-emerald-400 cursor-not-allowed flex items-center justify-center' 
                            : 'bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800'
                        }`}
                >
                    {isProcessing ? (
                        <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Procesando Pago...
                        </span>
                    ) : (
                        `Realizar Pedido ($${total})`
                    )}
                </button>
            </div>
        </div>
    );
};

export default CheckoutScreen;