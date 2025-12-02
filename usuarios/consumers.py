# usuarios/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Mensaje, ChatRoom 
import datetime # 🟢 CORRECCIÓN 1: Importación de datetime
from django.utils import timezone # 💡 Recomendado para trabajar con fechas conscientes de zona horaria

# Obtiene el modelo de usuario personalizado del proyecto
UsuarioPersonalizado = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # 1. Obtener la información de la ruta y el usuario
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"] 

        # 2. Manejo de errores de conexión y autenticación
        if not self.room_name or not self.user.is_authenticated:
            print("Conexión rechazada: Sala no encontrada o usuario no autenticado.")
            await self.close()
            return
            
        # 3. Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 4. Aceptar la conexión WebSocket
        await self.accept()


    async def disconnect(self, close_code):
        """Se ejecuta al cerrar la conexión WebSocket."""
        if self.room_name: 
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )


    async def receive(self, text_data):
        """Recibe mensaje de WebSocket, lo guarda y lo reenvía al grupo."""
        print("--- MENSAJE RECIBIDO EN CONSUMER ---") 
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        
        if not message.strip(): 
            return

        # 💡 Generar el timestamp del servidor antes de guardar (usando timezone)
        # Esto es más robusto si DJANGO_USE_TZ = True
        timestamp = timezone.now()
        timestamp_str = timestamp.strftime("%H:%M %p") 

        # 1. Guardar el mensaje en la base de datos (operación síncrona)
        try:
            await self.save_message(message) 
        except Exception as e:
            print(f"Error al guardar mensaje: {e}")
            return

        # 2. Enviar mensaje al grupo de la sala (broadcast)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', 
                'message': message,
                'username': self.user.username,
                'timestamp': timestamp_str, # ⬅️ AHORA ENVIAMOS LA HORA
            }
        )


    async def chat_message(self, event):
        """Recibe el mensaje del grupo y lo envía al WebSocket individual."""
        message = event['message']
        username = event['username']
        timestamp = event['timestamp'] 

        # Enviar mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'is_me': username == self.user.username,
            'timestamp': timestamp, 
        }))
        
        
    @sync_to_async
    def save_message(self, content):
        """
        Método síncrono para interactuar con la ORM de Django y guardar el mensaje.
        """
        try:
            # 🟢 CORRECCIÓN 2: Búsqueda por el campo 'room_name'
            room = ChatRoom.objects.get(room_name=self.room_name) 
        except ChatRoom.DoesNotExist:
            raise Exception(f"Sala {self.room_name} no encontrada para guardar mensaje.")
            
        # 🟢 CORRECCIÓN 3: Se asume que el ForeignKey en Mensaje es 'room'
        # (Si es 'sala', cambia 'room=' por 'sala=')
        Mensaje.objects.create(
            room=room,  
            autor=self.user,
            contenido=content
        )