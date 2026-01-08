// TransporteScreen.js

import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, SafeAreaView, Dimensions, Alert } from 'react-native';
import MapView, { Marker, Polyline } from 'react-native-maps';

const { height } = Dimensions.get('window');

const TransporteScreen = ({ onBack }) => {
    const mapRef = useRef(null);
    const [destino, setDestino] = useState('Higuerote');

    const rutaRoja = [
        { latitude: 10.4806, longitude: -66.9036 },
        { latitude: 10.4850, longitude: -66.1000 },
    ];

    // Función para que el botón IR mueva el mapa
    const irAHiguerote = () => {
        mapRef.current?.animateToRegion({
            latitude: 10.4850,
            longitude: -66.1000,
            latitudeDelta: 0.05,
            longitudeDelta: 0.05,
        }, 1000);
        Alert.alert("SISTEMA", "Ruta Activa hacia Higuerote");
    };

    return (
        <SafeAreaView style={{ flex: 1, backgroundColor: '#1A1A1A' }}> 
            <View style={{ height: height * 0.45 }}>
                <MapView 
                    ref={mapRef}
                    style={StyleSheet.absoluteFillObject}
                    initialRegion={{
                        latitude: 10.4806,
                        longitude: -66.9036,
                        latitudeDelta: 0.5,
                        longitudeDelta: 0.5,
                    }}
                >
                    <Polyline coordinates={rutaRoja} strokeColor="red" strokeWidth={10} zIndex={100} />
                    <Marker coordinate={rutaRoja[0]} />
                    <Marker coordinate={rutaRoja[1]}><Text style={{fontSize: 40}}>🚕</Text></Marker>
                </MapView>

                {/* Contenedor con pointerEvents para dejar pasar clics a los hijos */}
                <View style={styles.buscadorFlotante} pointerEvents="box-none">
                    <View style={styles.barraBlanca}>
                        <TextInput 
                            style={styles.inputB} 
                            value={destino} 
                            onChangeText={setDestino}
                            placeholder="Buscar..."
                        />
                        <TouchableOpacity style={styles.btnIr} onPress={irAHiguerote}>
                            <Text style={{color: 'white', fontWeight: 'bold'}}>IR</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </View>

            <View style={styles.formularioNuevo}>
                <Text style={styles.texto}>DISEÑO ACTUALIZADO</Text>
                
                {/* Botón de Confirmar con zIndex directo */}
                <TouchableOpacity 
                    style={styles.btnAmarillo} 
                    onPress={() => Alert.alert("CONFIRMADO", "Viaje solicitado con éxito")}
                >
                    <Text style={{fontWeight: 'bold', fontSize: 18, color: 'black'}}>CONFIRMAR VIAJE</Text>
                </TouchableOpacity>

                <TouchableOpacity onPress={onBack} style={{marginTop: 30, padding: 10}}>
                    <Text style={{color: 'white', textDecorationLine: 'underline'}}>VOLVER AL MENÚ</Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    buscadorFlotante: { 
        position: 'absolute', 
        top: 50, 
        left: 0, 
        right: 0, 
        alignItems: 'center',
        zIndex: 9999, // Prioridad máxima
    },
    barraBlanca: {
        width: '90%',
        height: 60,
        backgroundColor: 'white',
        borderRadius: 10,
        flexDirection: 'row',
        elevation: 20, // Sombra en Android para "flotar" sobre el mapa
        overflow: 'hidden',
    },
    inputB: { flex: 1, paddingLeft: 15, color: 'black', fontSize: 18 },
    btnIr: { backgroundColor: '#007AFF', paddingHorizontal: 25, justifyContent: 'center', zIndex: 10000 },
    formularioNuevo: { 
        flex: 1, 
        backgroundColor: '#1A1A1A', 
        padding: 25, 
        borderTopLeftRadius: 30, 
        borderTopRightRadius: 30, 
        marginTop: -20, 
        alignItems: 'center',
        zIndex: 5
    },
    texto: { color: '#FF4500', fontSize: 22, fontWeight: 'bold', marginBottom: 20 },
    btnAmarillo: { 
        backgroundColor: '#FFD700', 
        padding: 20, 
        borderRadius: 15, 
        width: '100%', 
        alignItems: 'center',
        elevation: 10 
    }
});

export default TransporteScreen;