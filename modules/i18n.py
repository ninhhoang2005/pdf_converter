import json
import os
import glob
from . import config

_current_lang = {}
_default_lang = {}

def load_language():
    """Loads the language specified in the config."""
    global _current_lang, _default_lang
    
    lang_code = config.get_language()
    
    # Load default English (template) first to ensure we always have a fallback
    default_path = os.path.join("lang", "en.json")
    if os.path.exists(default_path):
        with open(default_path, 'r', encoding='utf-8') as f:
            _default_lang = json.load(f)
    
    # If using English, just use default
    if lang_code == 'en':
        _current_lang = _default_lang
        return

    # Load target language
    lang_path = os.path.join("lang", f"{lang_code}.json")
    if os.path.exists(lang_path):
        try:
            with open(lang_path, 'r', encoding='utf-8') as f:
                _current_lang = json.load(f)
        except Exception as e:
            print(f"Error loading language {lang_code}: {e}")
            _current_lang = _default_lang
    else:
        _current_lang = _default_lang

def _(text):
    """Translates the text using the loaded language dictionary."""
    # Try current language
    if text in _current_lang:
        return _current_lang[text]
    
    # Fallback to default (English) explicitly if loaded, though normally we expect the key IS the English text
    # But if we used keys like "MENU_OPEN" instead of English text, we'd need this.
    # User strings are likely keys themselves.
    
    return text

def get_available_languages():
    """Returns a list of available language codes found in the lang folder."""
    langs = []
    
    # Always include English
    langs.append("en")
    
    if not os.path.exists("lang"):
        return langs
        
    for file in glob.glob("lang/*.json"):
        filename = os.path.basename(file)
        code = os.path.splitext(filename)[0]
        if code != "en":
            langs.append(code)
    
    return sorted(langs)

# Initialize on import
if not os.path.exists("lang"):
    try:
        os.makedirs("lang")
    except:
        pass

load_language()
