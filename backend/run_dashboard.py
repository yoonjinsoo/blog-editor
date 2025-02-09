#!/usr/bin/env python3
import os
import sys
import logging
import traceback

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.dashboard import create_app

def main():
    try:
        logger.info('Starting Flask application...')
        app = create_app()
        logger.info('Visit http://127.0.0.1:5000 to access the dashboard')
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
