import gettext
import os
from . import config

_current_trans = None

def load_language():
    """Loads the language specified in the config using gettext."""
    global _current_trans
    
    lang_code = config.get_language()
    
    # Path to locales folder: d:/python code/PDF to text/locales
    # We assume 'locales' is in the root of the project, parent of 'modules'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    locales_dir = os.path.join(base_dir, 'locales')
    
    # English is usually the fallback/source, so we use NullTranslations (identity)
    if lang_code == 'en':
        _current_trans = gettext.NullTranslations()
        return

    try:
        # Tries to load locales/{lang_code}/LC_MESSAGES/messages.mo
        _current_trans = gettext.translation('messages', localedir=locales_dir, languages=[lang_code])
    except FileNotFoundError:
        # Fallback to English if .mo file not found
        # print(f"Translation file not found for {lang_code}, falling back to English.")
        _current_trans = gettext.NullTranslations()
    except Exception as e:
        print(f"Error loading translation: {e}")
        _current_trans = gettext.NullTranslations()

def _(text):
    """Translates the text using the loaded gettext object."""
    if _current_trans is None:
        load_language()
    return _current_trans.gettext(text)

def get_available_languages():
    """Returns a list of available language codes found in the locales folder."""
    langs = ["en"]
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    locales_dir = os.path.join(base_dir, 'locales')
    
    if os.path.exists(locales_dir):
        for name in os.listdir(locales_dir):
            dir_path = os.path.join(locales_dir, name)
            # Check if it has LC_MESSAGES/messages.mo
            mo_path = os.path.join(dir_path, "LC_MESSAGES", "messages.mo")
            if os.path.isdir(dir_path) and os.path.exists(mo_path):
                langs.append(name)
    
    return sorted(langs)

# Initialize
load_language()
