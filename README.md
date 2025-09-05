## Activa entorno virtual

    source bin/activate

    // deactivate

## Configuración cuenta

Archivo .env

    USERNAME=[cuenta-gmail]
    PASS_GMAIL1=[contraseña-de-aplicación]
    LIMIT=[2000]

## Límites del servicio

    2000 correos personalizados por día
    10000 destinatarios totales

P.E:
    Enviar una campaña durante 12 horas al día, permitiría el envío de 2000 mensajes personalizados, cada 21 segundos.

    Si los mensajes son multidestinatarios (100 destinatarios) alcanzaríamos los 10000 destinatarios totales en sólo 100 mensajes (1 cada 21 segundos, es decir, 2100 segundos o 35 minutos)