import os
import logging
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Configureren van logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Ophalen van configuratie uit environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Starting Flask server on {host}:{port} with debug={debug_mode}")
    
    app.run(debug=debug_mode, host=host, port=port)
