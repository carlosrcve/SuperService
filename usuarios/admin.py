from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UsuarioPersonalizado)
admin.site.register(PerfilConductor)
# Registra los modelos para que aparezcan en el panel de administración
admin.site.register(Mensaje)
admin.site.register(ChatRoom)
