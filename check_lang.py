import sys
import os
import json
import configparser

# Adjust path to find modules
sys.path.append(os.getcwd())

print("--- Diagnostic Start ---")
print(f"CWD: {os.getcwd()}")

# 1. Check Config
try:
    from modules import config
    config_path = config.get_config_path()
    print(f"Config Path: {config_path}")
    if os.path.exists(config_path):
        print("Config file exists.")
        conf = config.load_config()
        lang = conf['General'].get('language', 'unknown')
        print(f"Current Configured Language: '{lang}'")
    else:
        print("Config file missing!")
        lang = 'en'
except Exception as e:
    print(f"Error checking config: {e}")
    lang = 'en'

# 2. Check JSON file
if lang != 'en':
    file_path = os.path.join("lang", f"{lang}.json")
    print(f"Checking language file: {file_path}")
    
    if os.path.exists(file_path):
        print("File found.")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("JSON is VALID.")
            print(f"Key count: {len(data)}")
            # Check a sample key
            print(f"Sample 'File': {data.get('&File', 'MISSING')}")
        except json.JSONDecodeError as e:
            print("!!! JSON ERROR !!!")
            print(f"ErrorMessage: {e}")
            print("The translation file is invalid. Please check for trailing commas or missing quotes.")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("Language file NOT FOUND.")
else:
    print("Language is 'en'. Using internal defaults/template.")

print("--- Diagnostic End ---")
input("Press Enter to close window...")
