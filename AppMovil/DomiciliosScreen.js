// DomicilioScreen.js 
import React, { useState, useRef, useEffect } from 'react';
import { 
    View, Text, StyleSheet, TouchableOpacity, TextInput, 
    ScrollView, Alert, SafeAreaView, Dimensions, ActivityIndicator, Modal, Animated, FlatList
} from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Audio } from 'expo-av';

const { height, width } = Dimensions.get('window');

const colors = {
    primary: '#007AFF', 
    orange: '#F59E0B',
    red: '#EF4444',
    green: '#10B981',
    blue: '#3B82F6',
    indigo: '#4F46E5',
};

// --- PANTALLA: DOMICILIO (🍕) ---
const DomicilioScreen = ({ onBack }) => {
    const [productos, setProductos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [carrito, setCarrito] = useState([]);
    const [enviando, setEnviando] = useState(false);

    useEffect(() => {
        obtenerMenuDesdeDjango();
    }, []);

    const obtenerMenuDesdeDjango = async () => {
        try {
            // Conexión con tu backend Django
            const response = await fetch('http://192.168.1.10:8080/domicilio/api/productos/');
            const data = await response.json();
            setProductos(data);
        } catch (error) {
            console.log("Error de conexión, usando datos locales de respaldo");
            setProductos([
                { id: 1, nombre: 'Pizza Margarita', precio: 12, descripcion: 'Queso y tomate natural' },
                { id: 2, nombre: 'Hamburguesa Pro', precio: 8, descripcion: 'Doble carne y queso cheddar' },
                { id: 3, nombre: 'Refresco Familiar', precio: 3, descripcion: '2 Litros' }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const agregarAlCarrito = (prod) => {
        setCarrito([...carrito, prod]);
    };

    // CONEXIÓN CON TUS ARCHIVOS MODELS.PY Y VIEWS.PY
    const enviarPedidoADjango = async () => {
        if (carrito.length === 0) return;
        
        setEnviando(true);
        const total = carrito.reduce((sum, item) => sum + item.precio, 0);

        const datosPedido = {
            cliente_id: 2, // ID de Norbelys en tu base de datos
            items: carrito.map(i => i.id),
            monto_total: total,
            estado: 'Pendiente'
        };

        try {
            const response = await fetch('http://192.168.1.10:8080/domicilio/api/pedidos/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosPedido),
            });

            if (response.ok) {
                Alert.alert("¡Pedido Enviado!", `Norbelys, tu pedido por $${total} ha sido registrado.`);
                setCarrito([]);
            } else {
                Alert.alert("Error", "El servidor de Django rechazó el pedido.");
            }
        } catch (error) {
            Alert.alert("Error de Red", "No se pudo conectar con 192.168.1.10:8080");
        } finally {
            setEnviando(false);
        }
    };

    return (
        <SafeAreaView style={{flex: 1, backgroundColor: '#F3F4F6'}}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>DOMICILIOS 🍕</Text>
                <TouchableOpacity onPress={onBack}><Text style={{color:'white'}}>Cerrar</Text></TouchableOpacity>
            </View>

            {loading ? (
                <ActivityIndicator size="large" color={colors.red} style={{marginTop: 50}} />
            ) : (
                <ScrollView contentContainerStyle={{padding: 15, paddingBottom: 100}}>
                    {productos.map((item) => (
                        <View key={item.id} style={styles.cardProducto}>
                            <View style={{flex: 1}}>
                                <Text style={styles.prodNombre}>{item.nombre}</Text>
                                <Text style={styles.prodDesc}>{item.descripcion}</Text>
                                <Text style={styles.prodPrecio}>${item.precio}</Text>
                            </View>
                            <TouchableOpacity 
                                style={styles.btnAgregar} 
                                onPress={() => agregarAlCarrito(item)}
                            >
                                <Text style={{color: 'white', fontWeight: 'bold', fontSize: 20}}>+</Text>
                            </TouchableOpacity>
                        </View>
                    ))}
                </ScrollView>
            )}
            
            {carrito.length > 0 && (
                <View style={styles.contenedorPedidoFlotante}>
                    <TouchableOpacity 
                        style={[styles.btnVerCarrito, {backgroundColor: colors.green}]}
                        onPress={enviarPedidoADjango}
                        disabled={enviando}
                    >
                        {enviando ? (
                            <ActivityIndicator color="white" />
                        ) : (
                            <Text style={{color: 'white', fontWeight: 'bold', fontSize: 16}}>
                                CONFIRMAR PEDIDO (${carrito.reduce((sum, i) => sum + i.precio, 0)})
                            </Text>
                        )}
                    </TouchableOpacity>
                </View>
            )}
        </SafeAreaView>
    );
};

// --- PANTALLA: TRANSPORTE (MANTENIENDO TU ORIGINAL) ---
const TransporteScreen = ({ onBack }) => {
    const mapRef = useRef(null);
    const [origen, setOrigen] = useState('Caracas');
    const [destino, setDestino] = useState('Valencia');
    const [loading, setLoading] = useState(false);
    const [viajando, setViajando] = useState(false);
    const animVal = useRef(new Animated.Value(0)).current;
    const [sound, setSound] = useState();

    const [rutaActual, setRutaActual] = useState([
        { latitude: 10.4806, longitude: -66.9036 },
        { latitude: 10.1620, longitude: -68.0077 }
    ]);

    const carLat = animVal.interpolate({ inputRange: [0, 1], outputRange: [rutaActual[0].latitude, rutaActual[1].latitude] });
    const carLon = animVal.interpolate({ inputRange: [0, 1], outputRange: [rutaActual[0].longitude, rutaActual[1].longitude] });

    useEffect(() => {
        return sound ? () => { sound.unloadAsync(); } : undefined;
    }, [sound]);

    async function reproducirClaxon() {
        try {
            const { sound } = await Audio.Sound.createAsync({ uri: 'https://www.soundjay.com/transportation/car-horn-01.mp3' });
            setSound(sound);
            await sound.playAsync();
        } catch (e) { console.log("Error sonido"); }
    }

    const manejarBusqueda = async () => {
        setLoading(true);
        // Lógica de búsqueda simplificada
        setLoading(false);
    };

    const confirmarViaje = async () => {
        if (viajando) return;
        await reproducirClaxon();
        setViajando(true);
        animVal.setValue(0);
        Animated.timing(animVal, { toValue: 1, duration: 4000, useNativeDriver: false }).start(() => {
            Alert.alert("¡Llegamos!", "El transporte ha llegado a su destino.");
            setViajando(false);
        });
    };

    return (
        <View style={{ flex: 1, backgroundColor: 'white' }}>
            <View style={{ height: height * 0.45 }}>
                <MapView ref={mapRef} style={StyleSheet.absoluteFillObject} initialRegion={{ latitude: 10.4806, longitude: -66.9036, latitudeDelta: 0.8, longitudeDelta: 0.8 }}>
                    <Polyline coordinates={rutaActual} strokeColor="red" strokeWidth={5} />
                    <Marker coordinate={rutaActual[0]} />
                    <Marker coordinate={rutaActual[1]} />
                    <Marker.Animated coordinate={{ latitude: carLat, longitude: carLon }}>
                        <Text style={{fontSize: 35}}>🚕</Text>
                    </Marker.Animated>
                </MapView>
                <View style={styles.floatInputs}>
                    <TextInput style={styles.inputMap} value={origen} onChangeText={setOrigen} />
                    <TextInput style={[styles.inputMap, {marginTop: 10}]} value={destino} onChangeText={setDestino} />
                    <TouchableOpacity style={styles.btnIrMapSimple} onPress={manejarBusqueda}>
                        <Text style={{color:'white', fontWeight:'bold'}}>ACTUALIZAR RUTA</Text>
                    </TouchableOpacity>
                </View>
            </View>
            <View style={styles.panelBajo}>
                <Text style={{fontWeight: 'bold', fontSize: 18}}>TU TRANSPORTE</Text>
                <TouchableOpacity 
                    style={[styles.btnFinal, {backgroundColor: viajando ? colors.indigo : colors.primary, marginTop: 20}]} 
                    onPress={confirmarViaje}
                >
                    <Text style={{color: 'white', fontWeight: 'bold'}}>{viajando ? "EN CAMINO..." : "PEDIR AHORA"}</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={onBack} style={{marginTop: 20}}><Text style={{color:'gray'}}>VOLVER</Text></TouchableOpacity>
            </View>
        </View>
    );
};

// --- APP PRINCIPAL ---
export default function App() {
    const [screen, setScreen] = useState('home');
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    if (!isLoggedIn) return (
        <View style={styles.loginFull}>
            <Text style={styles.loginLogo}>SuperService</Text>
            <TouchableOpacity style={styles.loginBtn} onPress={() => setIsLoggedIn(true)}>
                <Text style={{color: 'white', fontWeight: 'bold'}}>ENTRAR COMO NORBE</Text>
            </TouchableOpacity>
        </View>
    );

    if (screen === 'transporte') return <TransporteScreen onBack={() => setScreen('home')} />;
    if (screen === 'domicilio') return <DomicilioScreen onBack={() => setScreen('home')} />;

    return (
        <SafeAreaView style={{flex:1, backgroundColor: '#F3F4F6'}}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>SuperService</Text>
                <TouchableOpacity onPress={() => setIsLoggedIn(false)}><Text style={{color:'white'}}>Salir</Text></TouchableOpacity>
            </View>
            <ScrollView contentContainerStyle={{padding: 20}}>
                <Text style={{fontSize: 22, fontWeight: 'bold', marginVertical: 20}}>Bienvenida, Norbelys</Text>
                <View style={styles.cuadricula}>
                    <TouchableOpacity onPress={() => setScreen('transporte')} style={[styles.card, {backgroundColor: colors.orange}]}>
                        <Text style={{fontSize: 40}}>🚕</Text>
                        <Text style={{color: 'white', fontWeight: 'bold'}}>Transporte</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => setScreen('domicilio')} style={[styles.card, {backgroundColor: colors.red}]}>
                        <Text style={{fontSize: 40}}>🍕</Text>
                        <Text style={{color: 'white', fontWeight: 'bold'}}>Domicilio</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    loginFull: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.indigo },
    loginLogo: { color: 'white', fontSize: 35, fontWeight: 'bold', marginBottom: 40 },
    loginBtn: { backgroundColor: colors.orange, paddingVertical: 15, paddingHorizontal: 50, borderRadius: 20 },
    header: { padding: 20, paddingTop: 50, backgroundColor: colors.indigo, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
    headerTitle: { color: 'white', fontSize: 24, fontWeight: 'bold' },
    cuadricula: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
    card: { width: '48%', aspectRatio: 1, borderRadius: 20, alignItems: 'center', justifyContent: 'center', marginBottom: 15, elevation: 5 },
    floatInputs: { position: 'absolute', top: 20, left: 20, right: 20 },
    inputMap: { backgroundColor: 'white', padding: 12, borderRadius: 10, elevation: 5 },
    btnIrMapSimple: { backgroundColor: colors.primary, padding: 12, borderRadius: 10, marginTop: 10, alignItems: 'center' },
    panelBajo: { flex: 1, backgroundColor: 'white', borderTopLeftRadius: 30, borderTopRightRadius: 30, marginTop: -20, padding: 20, alignItems: 'center' },
    btnFinal: { width: '100%', padding: 18, borderRadius: 15, alignItems: 'center' },
    cardProducto: { flexDirection: 'row', backgroundColor: 'white', padding: 15, borderRadius: 15, marginBottom: 10, alignItems: 'center', elevation: 2 },
    prodNombre: { fontWeight: 'bold', fontSize: 16 },
    prodDesc: { color: 'gray', fontSize: 12 },
    prodPrecio: { color: colors.green, fontWeight: 'bold', marginTop: 5 },
    btnAgregar: { backgroundColor: colors.red, width: 45, height: 45, borderRadius: 22.5, justifyContent: 'center', alignItems: 'center' },
    contenedorPedidoFlotante: { position: 'absolute', bottom: 0, left: 0, right: 0, padding: 20, backgroundColor: 'white', borderTopWidth: 1, borderColor: '#DDD' },
    btnVerCarrito: { padding: 18, borderRadius: 15, alignItems: 'center' }
});