import React from 'react';

/**
 * Componente reutilizable para la entrada de texto de ubicación (Origen o Destino).
 * Utiliza íconos de Lucide.
 * * @param {object} props - Propiedades del componente
 * @param {string} props.id - ID único para la entrada
 * @param {string} props.label - Etiqueta descriptiva (e.g., "Punto de Recogida")
 * @param {string} props.value - Valor actual de la entrada
 * @param {function} props.onChange - Handler para el cambio de valor
 * @param {string} props.icon - Nombre del ícono de Lucide (e.g., "MapPin", "Flag")
 * @param {string} props.color - Color del ícono (clases de Tailwind)
 * @returns {JSX.Element}
 */
const LocationInput = ({ id, label, value, onChange, icon: Icon, color }) => {
    return (
        <div className="flex items-center bg-white p-3 rounded-xl shadow-md transition duration-150 hover:shadow-lg focus-within:ring-2 focus-within:ring-indigo-500">
            {/* Ícono de Lucide (simulado con SVG por robustez) */}
            <div className={`w-6 h-6 flex items-center justify-center ${color}`}>
                {Icon === 'MapPin' && (
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 21.7c-3.3 0-6-2.7-6-6 0-3.3 6-13 6-13s6 9.7 6 13c0 3.3-2.7 6-6 6z"/><circle cx="12" cy="10" r="3"/></svg>
                )}
                {Icon === 'Flag' && (
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>
                )}
            </div>
            
            <div className="flex-1 ml-3">
                <label htmlFor={id} className="block text-xs font-medium text-gray-500">
                    {label}
                </label>
                <input
                    id={id}
                    type="text"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={`Ingresa tu ${label.toLowerCase()}`}
                    className="w-full text-gray-800 text-base font-semibold border-none p-0 focus:ring-0"
                />
            </div>
        </div>
    );
};

export default LocationInput;