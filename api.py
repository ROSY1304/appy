from flask import Flask, jsonify, request, send_from_directory
import os
import nbformat
from flask_cors import CORS

app = Flask(__name__, static_folder='static')

# Habilitar CORS para la aplicación completa
CORS(app)

# Directorio donde están los documentos .ipynb
DOCUMENTS_FOLDER = 'documentos'
app.config['DOCUMENTS_FOLDER'] = DOCUMENTS_FOLDER

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

# Endpoint para listar los documentos disponibles
@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    """
    Lista todos los archivos .ipynb disponibles en la carpeta DOCUMENTS_FOLDER.
    """
    try:
        # Obtener la lista de archivos .ipynb en la carpeta documentos
        archivos = [f for f in os.listdir(DOCUMENTS_FOLDER) if f.endswith('.ipynb')]

        if not archivos:
            return jsonify({"mensaje": "No hay archivos .ipynb en el directorio."}), 404

        # Retornar la lista de archivos
        return jsonify(archivos), 200
    except FileNotFoundError:
        return jsonify({"mensaje": "No se encontró el directorio de documentos"}), 404
    except Exception as e:
        return jsonify({"mensaje": str(e)}), 500

@app.route('/documentos/contenido/<nombre>', methods=['GET'])
def ver_contenido_documento(nombre):
    try:
        notebook_path = os.path.join(DOCUMENTS_FOLDER, nombre)

        if os.path.exists(notebook_path) and nombre.endswith('.ipynb'):
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = nbformat.read(f, as_version=4)

            contenido = []

            if nombre == 'REGRESION-Copy1.ipynb':
                # Extraer solo la última celda
                ultima_celda = notebook_content.cells[-1]
                if ultima_celda.cell_type == 'code':
                    cell_data = procesar_celda_codigo(ultima_celda)
                    contenido.append(cell_data)

            elif nombre == 'Arboles de decision.ipynb':
                # Extraer las dos últimas celdas
                for celda in notebook_content.cells[-2:]:
                    if celda.cell_type == 'code':
                        cell_data = procesar_celda_codigo(celda)
                        contenido.append(cell_data)

            else:
                return jsonify({'mensaje': 'Este archivo no está permitido para visualización'}), 403

            return jsonify(contenido), 200
        else:
            return jsonify({'mensaje': 'Archivo no encontrado o formato incorrecto'}), 404
    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500


def procesar_celda_codigo(celda):
    """
    Procesa una celda de código y sus salidas para devolver un formato JSON.
    """
    cell_data = {
        'tipo': 'código',
        'contenido': celda.source,
        'salidas': []
    }

    for output in celda.outputs:
        if 'text' in output:
            cell_data['salidas'].append({
                'tipo': 'texto',
                'contenido': output['text']
            })
        elif 'data' in output:
            if 'image/png' in output['data']:
                cell_data['salidas'].append({
                    'tipo': 'imagen',
                    'contenido': output['data']['image/png']
                })
            elif 'application/json' in output['data']:
                cell_data['salidas'].append({
                    'tipo': 'json',
                    'contenido': output['data']['application/json']
                })
            elif 'text/html' in output['data']:
                cell_data['salidas'].append({
                    'tipo': 'html',
                    'contenido': output['data']['text/html']
                })
    return cell_data


# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
