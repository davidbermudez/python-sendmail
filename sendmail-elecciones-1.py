import csv
from dotenv import load_dotenv
import os
import smtplib
import time
import datetime
import uuid
import locale
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Leer variables de entorno
load_dotenv()
# Set locale
locale.setlocale(locale.LC_ALL, 'es_ES')


def html_a_texto(mensaje_html):
    # Elimina las etiquetas HTML y convierte algunos elementos básicos
    texto = mensaje_html
    texto = re.sub(r'<br\s*/?>', '\n', texto)  # Reemplaza <br> por saltos de línea
    texto = re.sub(r'</p>', '\n\n', texto)    # Reemplaza </p> por doble salto de línea
    texto = re.sub(r'<li>', '• ', texto)      # Reemplaza <li> por viñeta
    texto = re.sub(r'<.*?>', '', texto)       # Elimina cualquier otra etiqueta
    texto = re.sub(r'\n{3,}', '\n\n', texto)  # Normaliza saltos de línea
    texto = texto.strip()
    return texto


def registrar_envio(archivo_registro, token, email, fecha_hora, numero):
    # Añade una línea al archivo de registro con token, email y fecha-hora
    with open(archivo_registro, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([numero, token, email, fecha_hora])


def generar_token():
    # Genera un token único utilizando UUID
    return str(uuid.uuid4())


def enviar_email(destinatario, mensaje_html, imagen_oculta_url, subject):
    # Configura los detalles del servidor SMTP
    servidor_smtp = 'smtp.gmail.com'
    puerto = 587
    remitente = os.getenv("USERNAME")
    contraseña = os.getenv("PASS_GMAIL1")

    # Crea un objeto de conexión SMTP
    server = smtplib.SMTP(servidor_smtp, puerto)
    server.starttls()
    server.login(remitente, contraseña)

    # Construye el mensaje MIME como 'related'
    mensaje = MIMEMultipart('related')
    mensaje['From'] = 'AUGC <' + remitente + '>'
    mensaje['To'] = destinatario
    mensaje['Subject'] = subject

    # Subparte 'alternative' para texto y HTML
    alt_part = MIMEMultipart('alternative')
    # Versión texto generada automáticamente
    mensaje_txt = html_a_texto(mensaje_html)
    # Incluye la imagen oculta en el HTML principal
    imagen_oculta_html = f'<img src="{imagen_oculta_url}" width="1" height="1" style="display:none">'
    mensaje_html_con_imagen = mensaje_html + imagen_oculta_html
    
    # Adjunta ambas versiones
    alt_part.attach(MIMEText(mensaje_txt, 'plain'))
    alt_part.attach(MIMEText(mensaje_html_con_imagen, 'html'))

    mensaje.attach(alt_part)

    # Adjunta imágenes embebidas
    # Añade imagen <image1>
    image1 = MIMEImage(open('mainlogo.jpg', 'rb').read())
    image1.add_header('Content-ID', '<image1>')
    mensaje.attach(image1)

    # Añade imagen <image2>
    image2 = MIMEImage(open('VotoPorCorreo.png', 'rb').read())
    image2.add_header('Content-ID', '<image2>')
    mensaje.attach(image2)

    # Envía el correo electrónico
    try:
        server.sendmail(remitente, destinatario, mensaje.as_string())
        result = True
    except Exception  as e:
        print(f"Error enviando correo a {destinatario}: {e}")
        result = False

    # Cierra la conexión SMTP
    server.quit()
    return result


def lee_datos(archivo_csv):
    # leer
    content = []
    with open(archivo_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            elements = []
            for element in row:
                elements.append(element)
            content.append(elements)

    return content

def leer_plantilla_html(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        return archivo.read()
    

def render_template(archivo_csv):
    imagen_oculta_url_base = 'https://usuarios.augc.org/access_mail.php?'  # URL base de la imagen oculta
    archivo_registro = 'registro_envios.csv'  # Nuevo archivo para el registro
    contenido = lee_datos(archivo_csv)
    plantilla_html = leer_plantilla_html('template1.html')
    counter = 0
    limite = os.getenv("LIMIT")
    for row in contenido:        
        nombre = row[1]
        genero = row[3]
        email_ = row[6]
        print (row)
        if email_ and email_ != 'mail' and nombre != 'Nombre':
            token = generar_token()
            # Genera una URL única para la imagen oculta con el token
            imagen_oculta_url = f"{imagen_oculta_url_base}correo_id={token}"
            inclusivo = "Estimado" if genero == "Masculino" else "Estimada"
            mensaje_html = plantilla_html.format(
                title='¡Ya puedes votar en estas elecciones!',
                subtitle='ELECCIONES CONSEJO GUARDIA CIVIL 2025',
                content=f'<p>{inclusivo} {nombre},<br/></p> \
                    <p>Desde el 13 de agosto y hasta el 3 de octubre, tienes la oportunidad de solicitar el voto por \
                        correspondencia para las elecciones al Consejo de la Guardia Civil, que se celebrarán el 28 y 29 de octubre</p> \
                    <p>En AUGC sabemos que esos días pueden ser complicados para muchos, por lo que queremos ofrecerte una alternativa más cómoda y segura: \
                        votar desde tu Unidad, sin necesidad de desplazamientos innecesarios y evitando cualquier imprevisto que te impida ejercer tu derecho \
                        al voto de forma presencial.</p> \
                    <p>El proceso es sencillo y rápido. Solo tienes que acceder a la intranet utilizando tu tarjeta TIP o tu DNI electrónico. Además, te hemos \
                        preparado un breve vídeo explicativo para que puedas completar tu solicitud sin dificultades</p> \
                    <p>Tu voz es fundamental para el futuro de la Guardia Civil, ¡no dejes pasar esta oportunidad de participar!</p> \
                    <p>¡Te animamos a votar por correspondencia!</p>',
                enlace_url='https://drive.google.com/file/d/1oRCUoD9HFGhRtzBH8MFn3foPfh-JOnvA/preview',
                enlace_text = 'Cómo solicitar el voto por correo',                
                image_logo = f'<img src="cid:image1" alt="Logo_AUGC" class="logo" width="411" height="80">',
                image_content = f'<img src="cid:image2" alt="content" class="image" width="600" height="315">',
                firma = f'Asociación Unificada de Guardias Civiles',                
                imagen_oculta_url=imagen_oculta_url,
                idMessage=token
            )            
            if enviar_email(email_, mensaje_html, imagen_oculta_url, f'¿{nombre}, sabes que ya puedes votar en las próximas elecciones?'):
                print(f"Correo enviado a {email_}")
                fecha_hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                registrar_envio(archivo_registro, token, email_, fecha_hora, counter)
            else:
                print(f"Error al enviar a {email_}")
        else:
            print(f"Correo no válido o fila de encabezado: {email_}")
            
        counter += 1
        if counter == limite:
            break
        time.sleep(13)  # Espera 13 segundos entre cada envío


if __name__ == "__main__":
    archivo_csv = 'Mailing_all_delegations.csv'
    render_template(archivo_csv)