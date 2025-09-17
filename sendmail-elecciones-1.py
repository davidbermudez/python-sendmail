import csv
from dotenv import load_dotenv
import os
import smtplib
import time
import datetime
import uuid
import locale
import re
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Leer variables de entorno
load_dotenv()
# Set locale
locale.setlocale(locale.LC_ALL, 'es_ES')

# Configura los usuarios y contraseñas en arrays
USUARIOS = [
    os.getenv("USERNAME1"),
    os.getenv("USERNAME2"),
    os.getenv("USERNAME3"),
    os.getenv("USERNAME4"),
    os.getenv("USERNAME5"),
    os.getenv("USERNAME6"),
]
CLAVES = [
    os.getenv("PASS_GMAIL1"),
    os.getenv("PASS_GMAIL2"),
    os.getenv("PASS_GMAIL3"),
    os.getenv("PASS_GMAIL4"),
    os.getenv("PASS_GMAIL5"),
    os.getenv("PASS_GMAIL6"),
]

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

def leer_variables_mensaje_yaml(nombre_archivo):
    with open('templates/' + nombre_archivo, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def registrar_envio(archivo_registro, token, email, fecha_hora, numero, usuario):
    with open(archivo_registro, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([numero, token, email, fecha_hora, usuario])

def generar_token():
    # Genera un token único utilizando UUID
    return str(uuid.uuid4())


#def enviar_email(destinatario, mensaje_html, imagen_oculta_url, subject):
def enviar_email(destinatario, mensaje_html, imagen_oculta_url, subject, remitente, clave, image):
    # Configura los detalles del servidor SMTP
    servidor_smtp = 'smtp.gmail.com'
    puerto = 587
    # Crea un objeto de conexión SMTP
    server = smtplib.SMTP(servidor_smtp, puerto)
    server.starttls()
    server.login(remitente, clave)
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
    image2 = MIMEImage(open(image, 'rb').read())
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
    with open('templates/' + nombre_archivo, 'r', encoding='utf-8') as archivo:
        return archivo.read()
    

def render_template(archivo_csv, plantilla_html, mensaje_vars):
    imagen_oculta_url_base = 'https://usuarios.augc.org/access_mail.php?'  # URL base de la imagen oculta
    archivo_registro = 'registro_envios.csv'  # Nuevo archivo para el registro
    contenido = lee_datos(archivo_csv)    
    counter = 1
    limite = os.getenv("LIMIT")
    num_usuarios = len(USUARIOS)
    usuario_idx = 0    
    for row in contenido:        
        nombre = row[1]
        genero = row[3]
        email_ = row[6]
        print (row)
        if email_ and email_ != 'mail' and nombre != 'Nombre':
            remitente = USUARIOS[usuario_idx]
            clave = CLAVES[usuario_idx]
            usuario_idx = (usuario_idx + 1) % num_usuarios

            token = generar_token()
            # Genera una URL única para la imagen oculta con el token
            imagen_oculta_url = f"{imagen_oculta_url_base}correo_id={token}"
            inclusivo = "Estimado" if genero == "Masculino" else "Estimada"
            mensaje_html = plantilla_html.format(
                title=mensaje_vars['title'],
                subtitle=mensaje_vars['subtitle'],
                content=mensaje_vars['content'].replace('{inclusivo}', inclusivo).replace('{nombre}', nombre),
                enlace_url=mensaje_vars['enlace_url'],
                enlace_text=mensaje_vars['enlace_text'],
                image_logo=f'<img src="cid:image1" alt="Logo_AUGC" class="logo" width="411" height="80">',
                image_content=f'<img src="cid:image2" alt="content" class="image" width="600" height="315">',
                firma=mensaje_vars['firma'],
                imagen_oculta_url=imagen_oculta_url,
                idMessage=token
            )
            if enviar_email(email_, mensaje_html, imagen_oculta_url, f'¿{nombre}, qué Guardia Civil crees que merecemos?', remitente, clave, 'banner2.png'):
                print(f"{counter} Correo enviado a {email_}")
                fecha_hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                registrar_envio(archivo_registro, token, email_, fecha_hora, counter, remitente)
                counter += 1
            else:
                print(f"Error al enviar a {email_}")
            time.sleep(3)  # Espera 3 segundos entre cada envío
        else:
            print(f"Correo no válido o fila de encabezado: {email_}")
            
        
        if counter > int(limite):
            break        


if __name__ == "__main__":
    archivo_csv = 'export_user_2025_09_17_19_06_26.csv'
    plantilla_html = leer_plantilla_html('template2.html')
    mensaje_vars = leer_variables_mensaje_yaml('mensaje2.yaml')
    render_template(archivo_csv, plantilla_html, mensaje_vars)