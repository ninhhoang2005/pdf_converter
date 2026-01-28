import sys
import traceback

try:
    print("Attempting imports...")
    import wx
    print("wx imported")
    import fitz
    print("fitz imported")
    import pdf2docx
    print("pdf2docx imported")
    from modules import ui
    print("modules.ui imported")
    
    # Try to initialize classes to check for internal import errors
    print("Initializing logic...")
    logic = ui.ConverterLogic()
    print("Logic initialized")
    
    print("Check complete. No import errors found.")
except Exception:
    traceback.print_exc()
