# transporte/consumers.py (Modificado y Corregido)

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Viaje, MensajeViaje

UsuarioPersonalizado = get_user_model()

class ViajeChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # ✅ CORRECCIÓN 1: Guarda el ID del viaje en self.viaje_id para que sea accesible
        self.viaje_id = self.scope['url_route']['kwargs'].get('viaje_id')
        
        # El nombre del grupo es único para este viaje
        self.room_group_name = f'viaje_{self.viaje_id}'
        self.user = self.scope["user"] 

        # 1. Verificar si el usuario está autorizado para este viaje (Cliente, Conductor o Admin)
        # ✅ CORRECCIÓN 2: Llama a is_authorized sin argumento, ya que usa self.viaje_id
        if not await self.is_authorized(): 
            await self.close()
            return

        # 2. Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensaje del WebSocket (cliente)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        
        if not message.strip():
            return

        # 3. Guardar mensaje en la BD (síncrona)
        await self.save_message(message)

        # 4. Enviar mensaje al grupo (broadcast)
        # Nota: El 'username' se envía aquí.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username,
                # Se puede añadir el ID para mayor seguridad en el front-end, pero el username es suficiente aquí
            }
        )

    # Recibir mensaje del grupo (broadcast)
    async def chat_message(self, event):
        # Determina si el mensaje fue enviado por el usuario actual del socket
        is_me = event['username'] == self.user.username 
        
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'is_me': is_me
        }))
        
    @sync_to_async
    # ✅ CORRECCIÓN 3: is_authorized no recibe el ID como argumento, usa self.viaje_id
    def is_authorized(self): 
        """Verifica si el usuario es el cliente, conductor del viaje, o admin."""
        try:
            viaje = Viaje.objects.get(pk=self.viaje_id) # Usa self.viaje_id
            
            # ✅ CORRECCIÓN 4: Permite la conexión a usuarios staff/administradores
            return self.user.is_staff or self.user == viaje.cliente or self.user == viaje.conductor
        except Viaje.DoesNotExist:
            return False

    @sync_to_async
    # ✅ CORRECCIÓN 5: save_message usa self.viaje_id
    def save_message(self, content): 
        """Guarda el mensaje en MensajeViaje."""
        try:
            viaje = Viaje.objects.get(pk=self.viaje_id)
            MensajeViaje.objects.create(
                viaje=viaje,
                emisor=self.user,
                contenido=content
            )
            # Debugging opcional para ver en la consola de Daphne que se guardó
            # print(f"Mensaje guardado en DB para Viaje {self.viaje_id}.") 
        except Viaje.DoesNotExist:
            print(f"ERROR: Viaje {self.viaje_id} no encontrado para guardar mensaje.")