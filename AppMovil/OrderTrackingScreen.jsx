import React, { useEffect, useRef, useState } from 'react';
// Importamos Three.js desde el CDN global.
// NOTA: La etiqueta <script> para cargar three.min.js se ha movido al final de App.jsx.
const THREE = window.THREE;

const OrderTrackingScreen = ({ navigate, orderDetails }) => {
    const canvasRef = useRef(null);
    const [statusMessage, setStatusMessage] = useState("Tu pedido está siendo preparado...");

    // Detalles del pedido
    const { storeName, deliveryAddress, total } = orderDetails;

    // Lógica de simulación 3D
    useEffect(() => {
        // Verificación de disponibilidad de Three.js (asume que se carga correctamente en App.jsx)
        if (!canvasRef.current || !THREE) {
            console.error("Canvas o THREE.js no están disponibles. Asegúrate de que el CDN se cargue.");
            return;
        }

        const container = canvasRef.current.parentElement;
        let scene, camera, renderer, car, pathCurve, startTime;
        const clock = new THREE.Clock();

        // 1. Inicialización de la escena
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f4f8); // Fondo gris claro

        // 2. Configuración de la Cámara
        camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        camera.position.set(0, 10, 15);
        camera.lookAt(0, 0, 0);

        // 3. Renderizador
        renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Manejar el redimensionamiento
        const handleResize = () => {
            if (container && renderer) {
                const width = container.clientWidth;
                const height = container.clientHeight;
                renderer.setSize(width, height);
                camera.aspect = width / height;
                camera.updateProjectionMatrix();
            }
        };

        window.addEventListener('resize', handleResize);
        
        // 4. Luces
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
        directionalLight.position.set(10, 20, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        scene.add(directionalLight);

        // 5. Crear Camino (Path)
        const points = [
            new THREE.Vector3(-10, 0, 0),
            new THREE.Vector3(-5, 0, -5),
            new THREE.Vector3(5, 0, -5),
            new THREE.Vector3(10, 0, 0) // Punto de destino
        ];
        pathCurve = new THREE.CatmullRomCurve3(points);

        const geometry = new THREE.TubeGeometry(pathCurve, 20, 0.1, 8, false);
        const material = new THREE.MeshLambertMaterial({ color: 0xcccccc });
        const pathMesh = new THREE.Mesh(geometry, material);
        pathMesh.receiveShadow = true;
        scene.add(pathMesh);

        // 6. Crear Coche (Delivery Car)
        const carGeometry = new THREE.BoxGeometry(1.5, 0.7, 1);
        const carMaterial = new THREE.MeshStandardMaterial({ color: 0x1d4ed8 }); // Azul añil
        car = new THREE.Mesh(carGeometry, carMaterial);
        car.castShadow = true;
        scene.add(car);
        
        // 7. Crear Destino (Target)
        const targetGeometry = new THREE.ConeGeometry(1, 3, 32);
        const targetMaterial = new THREE.MeshLambertMaterial({ color: 0xef4444 }); // Rojo
        const target = new THREE.Mesh(targetGeometry, targetMaterial);
        target.position.copy(points[points.length - 1]);
        target.position.y = 1.5;
        scene.add(target);

        // Función para crear un texto simple (Sprite)
        function createTextSprite(message, color, fontsize, borderThickness) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            
            const font = "Bold " + fontsize + "px Inter";
            context.font = font;
            const metrics = context.measureText(message);
            const textWidth = metrics.width;
            
            // Ajustar el tamaño del canvas para el texto
            canvas.width = textWidth + 2 * borderThickness;
            canvas.height = fontsize + 2 * borderThickness;
            
            context.font = font; // Necesario re-establecer después del resize
            context.fillStyle = `#${color.toString(16).padStart(6, '0')}`;
            context.fillText(message, borderThickness, fontsize + borderThickness);
            
            const texture = new THREE.Texture(canvas);
            texture.needsUpdate = true;
            
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(spriteMaterial);
            // Ajustar escala para que se vea legible en la escena
            sprite.scale.set(textWidth / 100 * 5, 2, 1.0); 
            return sprite;
        }

        const destinationSprite = createTextSprite("DESTINO", 0x333333, 100, 0.5);
        destinationSprite.position.copy(target.position);
        destinationSprite.position.y += 2.5;
        scene.add(destinationSprite);


        startTime = Date.now();
        const tripDuration = 20000; // Simulación de 20 segundos

        // 8. Bucle de Animación
        const animate = () => {
            requestAnimationFrame(animate);

            const elapsed = Date.now() - startTime;
            let t = (elapsed % tripDuration) / tripDuration; // 0 a 1

            if (t > 0.99 && !car.isFinished) {
                 // El coche ha llegado o está muy cerca
                t = 1; 
                car.isFinished = true;
                setStatusMessage(`¡Pedido Entregado! Disfruta tu ${storeName}.`);
                // Detener el movimiento y cambiar color
                car.material.color.set(0x10b981); // Verde esmeralda
                directionalLight.color.set(0x10b981);
                renderer.render(scene, camera);
                // No retornar aquí para que la limpieza final pueda ejecutarse
            }
            
            if (!car.isFinished) {
                 // Obtener la posición en la curva (t va de 0 a 1)
                const position = pathCurve.getPointAt(t);
                car.position.copy(position);
                car.position.y = 0.5; // Ajuste para que flote sobre el camino

                // Rotar el coche en la dirección del movimiento
                const tangent = pathCurve.getTangentAt(t).normalize();
                const up = new THREE.Vector3(0, 1, 0); // Vector 'hacia arriba'
                car.lookAt(position.clone().add(tangent));
            }
           
            // Mover la cámara ligeramente para un efecto dinámico
            const angle = clock.getElapsedTime() * 0.1;
            camera.position.x = Math.sin(angle) * 15;
            camera.position.z = Math.cos(angle) * 15;
            camera.lookAt(car.position.x, car.position.y, car.position.z);
            
            renderer.render(scene, camera);
        };

        animate();
        handleResize(); // Primera llamada para establecer el tamaño

        return () => {
            window.removeEventListener('resize', handleResize);
            // Limpieza de Three.js
            if (renderer) renderer.dispose();
            if (scene) scene.clear();
        };

    }, [orderDetails]);

    return (
        <div className="flex flex-col h-screen bg-gray-100 font-inter max-w-sm mx-auto shadow-2xl">
            {/* Encabezado */}
            <div className="bg-indigo-700 text-white p-4 flex items-center shadow-md">
                <button 
                    className="text-white text-3xl hover:opacity-80 transition mr-4" 
                    onClick={() => navigate('home')} 
                >
                    &larr;
                </button>
                <h1 className="text-xl font-bold flex-1">Seguimiento de Pedido</h1>
            </div>

            {/* Panel de Estado */}
            <div className="p-4 bg-white border-b border-gray-200 shadow-md">
                <div className="flex items-center space-x-3 mb-2">
                    <span className="text-2xl">🚚</span>
                    <p className={`text-lg font-semibold ${statusMessage.includes('Entregado') ? 'text-emerald-600' : 'text-indigo-700'}`}>
                        {statusMessage}
                    </p>
                </div>
                <div className="text-sm text-gray-600">
                    <p>Tienda: <span className="font-medium">{storeName}</span></p>
                    <p>Entrega en: <span className="font-medium">{deliveryAddress}</span></p>
                </div>
            </div>

            {/* Canvas 3D (Simulación de Mapa) */}
            <div className="flex-1 overflow-hidden relative" style={{ minHeight: '300px' }}>
                <canvas ref={canvasRef} className="w-full h-full block" />
            </div>

            {/* Detalles del Pedido */}
            <div className="p-4 bg-white border-t border-gray-200">
                <div className="flex justify-between text-lg font-bold">
                    <span>Total Pagado:</span>
                    <span className="text-emerald-600">${total.toFixed(2)}</span>
                </div>
                <button
                    className="w-full mt-4 p-3 bg-indigo-500 text-white font-bold rounded-xl shadow-lg hover:bg-indigo-600 transition duration-300"
                    onClick={() => navigate('home')}
                >
                    Finalizar y Volver al Inicio
                </button>
            </div>
        </div>
    );
};

export default OrderTrackingScreen;