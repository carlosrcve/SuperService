# domicilios/utils.py

from math import radians, cos, sin, asin, sqrt

# Radio de la Tierra en kilómetros
R_TIERRA_KM = 6371.0

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos de coordenadas (lat, lon) 
    en kilómetros utilizando la fórmula del Haversine.
    """
    
    # 1. Convertir grados a radianes
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # 2. Diferencias de coordenadas
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # 3. Aplicar fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    
    # 4. Distancia en kilómetros
    distancia_km = R_TIERRA_KM * c

    return distancia_km