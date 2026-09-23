from app.admin.principal import enviar_correo_citacion # ajusta el import a donde realmente esté tu función

resultado = enviar_correo_citacion(
    email="tu_correo_real@gmail.com",
    nombres="Prueba",
    fecha="2026-10-01",
    hora="10:00",
    lugar="Oficina principal",
    mensaje="Este es un correo de prueba."
)

print(resultado)