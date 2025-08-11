import os
from app import app

if __name__ == '__main__':
    # Obtener el puerto de la variable de entorno PORT, por defecto 8080 si no está definida
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
