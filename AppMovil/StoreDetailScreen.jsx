import React, { useState, useMemo } from 'react';

// Estilos base y componentes reutilizables
const baseStyles = {
    screenContainer: "flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl",
    headerColor: 'bg-emerald-600 text-white',
    shadowButton: "shadow-xl hover:shadow-2xl transition duration-300",
};

// Componente para una tarjeta de ítem del menú
const MenuItemCard = ({ item, addToCart }) => (
    <div className="flex justify-between items-center p-4 bg-white rounded-xl shadow-md mb-3 border border-gray-100">
        <div className="flex-1 pr-4">
            <h4 className="text-md font-semibold text-gray-800">{item.name}</h4>
            <p className="text-sm text-gray-500 my-1">{item.description}</p>
            <p className="text-lg font-bold text-emerald-600">${item.price.toFixed(2)}</p>
        </div>
        <button
            onClick={() => addToCart(item)}
            className={`bg-emerald-500 text-white font-bold py-2 px-4 rounded-full text-lg ${baseStyles.shadowButton}`}
        >
            +
        </button>
    </div>
);

// Componente principal de la pantalla
const StoreDetailScreen = ({ navigate, store }) => {
    // Estado del carrito: { itemId: { item, count } }
    const [cartItems, setCartItems] = useState({});

    if (!store) {
        return (
            <div className={baseStyles.screenContainer}>
                <div className="p-6 text-center text-red-500">
                    Error: No se encontró información de la tienda.
                </div>
                <button 
                    onClick={() => navigate('domicilios')} 
                    className="bg-indigo-500 text-white p-3 m-4 rounded-xl"
                >
                    Volver a Tiendas
                </button>
            </div>
        );
    }

    // Lógica para añadir un ítem al carrito
    const addToCart = (item) => {
        setCartItems(prevItems => {
            const currentItem = prevItems[item.id] || { item: item, count: 0 };
            return {
                ...prevItems,
                [item.id]: {
                    ...currentItem,
                    count: currentItem.count + 1,
                }
            };
        });
    };

    // Lógica para quitar un ítem del carrito (opcional, por ahora solo añadimos)
    const removeFromCart = (itemId) => {
        setCartItems(prevItems => {
            const currentItem = prevItems[itemId];
            if (!currentItem || currentItem.count <= 1) {
                // Si la cuenta es 1 o menos, eliminamos el ítem
                const newItems = { ...prevItems };
                delete newItems[itemId];
                return newItems;
            }
            // Si la cuenta es mayor a 1, solo decrementamos
            return {
                ...prevItems,
                [itemId]: {
                    ...currentItem,
                    count: currentItem.count - 1,
                }
            };
        });
    };

    // Calcular el total de ítems y el costo total del carrito
    const { totalItems, totalCost } = useMemo(() => {
        const items = Object.values(cartItems);
        const totalItems = items.reduce((sum, cartItem) => sum + cartItem.count, 0);
        const totalCost = items.reduce((sum, cartItem) => sum + (cartItem.count * cartItem.item.price), 0);
        return { totalItems, totalCost };
    }, [cartItems]);

    // Función para navegar a la caja (checkout)
    const goToCheckout = () => {
        const finalCart = Object.values(cartItems).map(cartItem => ({
            ...cartItem.item,
            quantity: cartItem.count,
            subtotal: cartItem.item.price * cartItem.count,
        }));

        navigate('checkout', {
            store: store,
            cart: finalCart,
            totalCost: totalCost
        });
    };
    
    // Obtener el menú de la tienda
    const menu = store.menu || [];

    return (
        <div className={baseStyles.screenContainer}>
            
            {/* Cabecera con Imagen de la Tienda */}
            <div className="relative h-48">
                <img 
                    src={store.image} 
                    alt={store.name} 
                    className="w-full h-full object-cover"
                    onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/600x400/E5E7EB/6B7280?text=Tienda+SuperApp" }}
                />
                <button 
                    className="absolute top-4 left-4 bg-white text-gray-800 p-2 rounded-full shadow-lg text-xl hover:bg-gray-100" 
                    onClick={() => navigate('domicilios')}
                >
                    &larr;
                </button>
            </div>

            {/* Información de la Tienda */}
            <div className="bg-white p-4 -mt-6 rounded-t-3xl relative z-10 shadow-lg">
                <h1 className="text-2xl font-extrabold text-gray-800">{store.name}</h1>
                <div className="flex items-center text-sm text-gray-500 mt-1 space-x-4">
                    <span>{store.cuisine}</span>
                    <span className="flex items-center text-yellow-600 font-semibold">
                        <span className="text-lg mr-1">⭐</span>{store.rating}
                    </span>
                    <span>🕒 {store.deliveryTime}</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">Envío: $3.50 (Mínimo de pedido $5.00)</p>
            </div>

            {/* Menú de Productos (Scrollable) */}
            <div className="flex-1 overflow-y-auto p-4 pb-20">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Menú Completo</h2>
                
                {menu.length > 0 ? (
                    menu.map(item => (
                        <MenuItemCard 
                            key={item.id} 
                            item={item} 
                            addToCart={addToCart} 
                        />
                    ))
                ) : (
                    <div className="text-center p-10 bg-white rounded-xl shadow-lg">
                        <p className="text-gray-500">Esta tienda aún no tiene un menú cargado.</p>
                    </div>
                )}
            </div>

            {/* Carrito Flotante (Checkout) */}
            {totalItems > 0 && (
                <div className="fixed bottom-0 w-full max-w-sm p-4 bg-transparent">
                    <button
                        onClick={goToCheckout}
                        className={`w-full flex justify-between items-center ${baseStyles.headerColor} text-white p-4 rounded-xl font-bold text-lg ${baseStyles.shadowButton}`}
                    >
                        {/* Indicador de Ítems */}
                        <span className="bg-white text-emerald-600 px-3 py-1 rounded-full text-sm">
                            {totalItems} {totalItems === 1 ? 'Ítem' : 'Ítems'}
                        </span>
                        
                        <span>Ver Carrito</span>
                        
                        {/* Costo Total */}
                        <span>${totalCost.toFixed(2)}</span>
                    </button>
                </div>
            )}
        </div>
    );
};

export default StoreDetailScreen;