from flask import Flask, request, jsonify
from dotenv import load_dotenv
import boto3
import base64
import os

app = Flask(__name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# Configurar el cliente de Rekognition
rekognition_client = boto3.client('rekognition', 
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

@app.route('/tarea3-201314439', methods=['POST'])
def procesar_imagen():
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    # Guardar la imagen en el servidor
    filename = file.filename
    file_path = os.path.join('./uploads', filename)
    file.save(file_path)

    # Leer la imagen en formato base64
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # Eliminar la imagen del servidor
    os.remove(file_path)

    # Enviar la imagen a Rekognition
    response = rekognition_client.detect_labels(
        Image={'Bytes': base64.b64decode(encoded_string)}
    )

    # Obtener las etiquetas
    relevant_data = []
    for label in response['Labels']:
        label_data = {
            'Nombre': label['Name'],
            'Confianza': label['Confidence'],
            'Detalles': label['Instances'],
            'Textos': label.get('TextInstances', [])
        }
        relevant_data.append(label_data)

    return jsonify({'imagen': filename, 'datos_relevantes': relevant_data}), 200

if __name__ == '__main__':
    app.run(debug=True)
