import csv
from dotenv import load_dotenv
import os
import smtplib
import time
import uuid
import locale
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Leer variables de entorno
load_dotenv()
# Set locale
locale.setlocale(locale.LC_ALL, 'es_ES')

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

    # Construye el mensaje MIME
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = subject

    # Adjunta el cuerpo del mensaje en formato HTML
    mensaje.attach(MIMEText(mensaje_html, 'html'))
    # Adjunta el cuerpo del mensaje en formato TXT
    # mensaje.attach(MIMEText(mensaje_txt, 'plain'))
    
    # Añade la imagen oculta con el token en la URL
    imagen_oculta_html = f'<img src="{imagen_oculta_url}" width="1" height="1" style="display:none">'
    mensaje.attach(MIMEText(imagen_oculta_html, 'html'))

    # Añade imagen <image1>
    image = MIMEImage(open('mainlogo.jpg', 'rb').read())
    image.add_header('Content-ID', '<image1>')
    mensaje.attach(image)

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


def escribe_datos(archivo_csv, content):
    # escribir
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer_ = csv.writer(csvfile)
        for fila in content:
            writer_.writerow(fila)
            #print("Escribiendo", fila)


def leer_plantilla_html(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        return archivo.read()
    

def render_template(archivo_csv):
    imagen_oculta_url_base = 'https://usuarios.augc.org/access_mail.php?'  # URL base de la imagen oculta
    contenido = lee_datos(archivo_csv)
    plantilla_html = leer_plantilla_html('plantilla.html')
    nombre = '1'
    while(nombre!=''):
        nombre = ''
        for row in contenido:
            if(row[12]==''):
                print (row)
                nombre = row[1]
                curso_pf = row[7]
                wellington = row[10]
                delegacion = row[6]
                email_ = row[5]
                tokenTPV = row[11]
                token = generar_token()
                # Genera una URL única para la imagen oculta con el token
                imagen_oculta_url = f"{imagen_oculta_url_base}correo_id={token}"
                # Actualiza el archivo CSV con el token generado
                row[12] = token
                break
        if(nombre!='' and email_!='EMAIL'):
            cursos = ''
            if(curso_pf!=''):
                cursos = f'<ul><li>{curso_pf}</li>'
            if(wellington!=''):
                cursos += f'<li>{wellington}</li>'
            cursos += '</ul>'
            mensaje_html = plantilla_html.format(
                title='Felicidades, ya tienes tu curso',
                article=f'<p>Hola {nombre},<br><br>Has sido admitido/a para la realización de los cursos del Plan de Formación de 2025 que \
                    elegiste:<p/>{cursos}<p>Como recordarás en el proceso de solicitud, el acceso al curso requiere el pago de una fianza de 20,00€, que \
                    te será devuelta íntegramente al finalizar el curso. El abono de la fianza se realizará a través de la pasarela de pago seguro de \
                    AUGC</p></p><p><b>Tienes hasta el 23 de marzo para efectuar el pago</b></p> \
                    <p>A partir de ese día, comenzaremos a enviar por email las instrucciones de acceso a los cursos</p><p>Un saludo.</p>',
                delegacion=delegacion,
                enlace='https://tpv.augc.org/index.php?token=' + tokenTPV,
                imagen_oculta_url=imagen_oculta_url,
                idMessage=token
            )
            # mensaje_txt = f"Hola {nombre},\n\nHas sido admitido/a para la realización de los cursos del Plan de Formación de 2025 que \
            #        elegiste:\n·{curso_pf}\n·{wellington}\n\nComo recordarás en el proceso de solicitud, el acceso al curso requiere el pago de una fianza de 20,00€, que \
            #        te será devuelta íntegramente al finalizar el curso. El abono de la fianza se realizará a través de la pasarela de pago seguro de \
            #        AUGC\n\nTienes hasta el 23 de marzo para efectuar el pago\nA partir de ese día, comenzaremos a enviar por email las instrucciones de acceso a los cursos \
            #        Copia y pega la siguiente URL en tu navegador para realizar el pago: https://tpv.augc.org/index.php?token={tokenTPV}\n\nUn saludo."
            # Solo curso_pf
            if(curso_pf!=''):
                if (enviar_email(email_, mensaje_html, imagen_oculta_url, 'Enhorabuena ' + nombre + ', has sido admitido/a en los cursos de AUGC')):
                    print(f"Correo enviado a {email_}")
                else:
                    row[12] = 'ERROR'

            # reescribimos archivo
            escribe_datos(archivo_csv, contenido)
        time.sleep(15)  # Espera 15 segundos entre cada envío


if __name__ == "__main__":
    archivo_csv = 'FILTRADAS.csv'
    # archivo_csv = 'Pruebas.csv'
    render_template(archivo_csv)