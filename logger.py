import logging
import yaml

def setup_logger():
    # Load config
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Configure logger
    logging.basicConfig(
        level=config['logging']['level'],
        filename=config['logging']['file'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger(__name__)

logger = setup_logger() 