#domicilios/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

# Importa los modelos necesarios
# Asegúrate que el modelo de usuario esté configurado en tu proyecto (settings.AUTH_USER_MODEL)
from django.contrib.auth import get_user_model 
from domicilios.models import Pedido, Mensaje 

User = get_user_model() # Obtiene el modelo de usuario personalizado

class PedidoChatConsumer(AsyncWebsocketConsumer):
    
    # ----------------------------------------------------
    # 1. CONEXIÓN Y DESCONEXIÓN
    # ----------------------------------------------------
    async def connect(self):
        # El pedido_id viene de la URL (ej: /ws/pedido/1/)
        self.pedido_id = self.scope['url_route']['kwargs']['pedido_id']
        self.room_group_name = 'chat_pedido_%s' % self.pedido_id

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Se acepta la conexión
        await self.accept()

    async def disconnect(self, close_code):
        # Abandonar el grupo de la sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # ----------------------------------------------------
    # 2. MANEJO DE MENSAJES RECIBIDOS (del Cliente al Servidor)
    # ----------------------------------------------------
    async def receive(self, text_data):
        """Recibe mensaje de WebSocket, lo guarda y lo reenvía al grupo."""
        
        # 🚨 DEBUG CRÍTICO: Debe aparecer en la consola de Daphne
        print("--- MENSAJE RECIBIDO EN CONSUMER ---") 
        
        try:
            data_json = json.loads(text_data)
            
            # 🟢 CORRECCIÓN: Usar .get() para evitar KeyError y obtener el mensaje
            message = data_json.get('message', '').strip()
            user = self.scope["user"]

            # Si el mensaje está vacío o el usuario no está autenticado, salimos.
            if not message or not user.is_authenticated:
                if not message:
                     print("Mensaje vacío o solo espacios, descartado.")
                else:
                     print("Usuario no autenticado, mensaje descartado.")
                return

            # 1. 💾 Guardar el mensaje en la Base de Datos (Operación SÍNCRONA)
            # Llama a la función corregida save_message
            mensaje_obj = await self.save_message(user, message) 
            
            # 2. 📢 Enviar el mensaje al grupo (Operación ASÍNCRONA)
            timestamp = mensaje_obj.timestamp.strftime('%H:%M') # O el formato que uses
            is_me = (user == mensaje_obj.emisor) # Revisa si el emisor es el usuario actual
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username,
                    'is_me': is_me,
                    'timestamp': timestamp,
                }
            )

        except json.JSONDecodeError:
            print(f"Error: Datos recibidos no son JSON válido: {text_data}")
        except Exception as e:
            print(f"Error grave al procesar o guardar mensaje: {e}")
    # ...

    # ----------------------------------------------------
    # 3. MANEJO DE MENSAJES ENVIADOS (del Servidor al Cliente)
    # ----------------------------------------------------
    # domicilios/consumers.py

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        
        # CRÍTICO: Aquí se usa el 'user_id' que ahora se envía desde receive
        message_user_id = event['user_id'] 
        current_user_id = self.scope["user"].id

        # Determinar si el mensaje es del cliente actual (is_me)
        is_me = message_user_id == current_user_id

        # Envía el mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'is_me': is_me, # Clave para que el frontend alinee la burbuja
            # ⚠️ Nota: El frontend usa su propio timestamp, pero puedes enviar el del servidor si quieres.
        }))

    # ----------------------------------------------------
    # 4. FUNCIÓN ASÍNCRONA PARA GUARDAR EN DB (SÍNCRONA)
    # ----------------------------------------------------
    @sync_to_async
    def save_message(self, user, message):
        # 🔑 Buscar el pedido para el mensaje
        try:
            pedido = Pedido.objects.get(pk=self.pedido_id)
        except Pedido.DoesNotExist:
            raise Exception("Pedido no encontrado")
            
        # 🔑 Crear y guardar el mensaje
        # 🛑 CORRECCIÓN CLAVE: Usamos el nombre correcto 'Mensaje'
        return Mensaje.objects.create(
            pedido=pedido,
            emisor=user,
            contenido=message
        )