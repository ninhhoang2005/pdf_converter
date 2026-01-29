import os
import configparser

APP_NAME = "PDF Converter"
VENDOR_NAME = "Technology Entertainment Studio"

def get_app_data_dir():
    """Returns the path to the application data directory."""
    appdata = os.getenv('APPDATA')
    if not appdata:
        appdata = os.path.expanduser("~")
    
    path = os.path.join(appdata, VENDOR_NAME, APP_NAME)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_config_path():
    return os.path.join(get_app_data_dir(), "config.ini")

def load_config():
    """Loads the configuration from config.ini."""
    config = configparser.ConfigParser()
    config_path = get_config_path()
    
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
    
    # Set defaults if missing
    if 'General' not in config:
        config['General'] = {}
    
    if 'language' not in config['General']:
        config['General']['language'] = 'en'
        
    return config

def save_config(config):
    """Saves the configuration to config.ini."""
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def get_language():
    config = load_config()
    return config['General'].get('language', 'en')

def set_language(lang_code):
    config = load_config()
    config['General']['language'] = lang_code
    save_config(config)
