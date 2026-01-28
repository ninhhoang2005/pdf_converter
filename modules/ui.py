import wx
import os
import threading
from .pdf_viewer import PDFViewer
from .converter import ConverterLogic

APP_VERSION = "2.0"
APP_TITLE = f"PDF Converter, version: {APP_VERSION}"

# Dark Theme Colors
COLOR_BG = "#2E2E2E" # Dark Grey
COLOR_FG = "#FFFFFF" # White
COLOR_ACCENT = "#007ACC" # Blue
COLOR_PANEL = "#3C3C3C" # Components BG
COLOR_BUTTON = "#505050" 

class DarkPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.SetBackgroundColour(COLOR_BG)
        self.SetForegroundColour(COLOR_FG)

class ConversionProgressDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Converting...", size=(400, 300), style=wx.CAPTION)
        self.SetBackgroundColour(COLOR_BG)
        self.SetForegroundColour(COLOR_FG)
        
        panel = wx.Panel(self)
        panel.SetBackgroundColour(COLOR_BG)
        panel.SetForegroundColour(COLOR_FG)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        lbl = wx.StaticText(panel, label="Conversion in Progress")
        lbl.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl.SetForegroundColour(COLOR_FG)
        vbox.Add(lbl, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Log Box
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.log_text.SetBackgroundColour(COLOR_PANEL)
        self.log_text.SetForegroundColour(COLOR_FG)
        vbox.Add(self.log_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        panel.SetSizer(vbox)
        self.CenterOnParent()

    def append_log(self, msg):
        wx.CallAfter(self.log_text.AppendText, msg + "\n")

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title=APP_TITLE, size=(900, 700))
        self.SetBackgroundColour(COLOR_BG)
        
        self.viewer = None
        self.logic = ConverterLogic()
        self.selected_file = None
        self.progress_dialog = None
        
        self.init_ui()
        self.Center()
        self.Show()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Top Bar ---
        top_panel = DarkPanel(self)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.path_text = wx.TextCtrl(top_panel, style=wx.TE_READONLY)
        self.path_text.SetBackgroundColour(COLOR_PANEL)
        self.path_text.SetForegroundColour(COLOR_FG)
        
        btn_select = wx.Button(top_panel, label="Select PDF")
        btn_select.Bind(wx.EVT_BUTTON, self.on_select_file)
        
        # Format Combo
        lbl_fmt = wx.StaticText(top_panel, label="Format:")
        lbl_fmt.SetForegroundColour(COLOR_FG)
        
        self.combo_format = wx.ComboBox(top_panel, choices=["TXT", "HTML", "DOCX"], style=wx.CB_READONLY)
        self.combo_format.SetSelection(0) # Default to TXT
        
        self.btn_convert = wx.Button(top_panel, label="Convert")
        self.btn_convert.Bind(wx.EVT_BUTTON, self.on_convert_click)
        self.btn_convert.Disable()
        
        top_sizer.Add(self.path_text, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        top_sizer.Add(btn_select, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        top_sizer.Add(lbl_fmt, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        top_sizer.Add(self.combo_format, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        top_sizer.Add(self.btn_convert, 0, wx.ALIGN_CENTER_VERTICAL)
        
        top_panel.SetSizer(top_sizer)
        
        # --- Preview Area ---
        self.scroll_window = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.scroll_window.SetScrollRate(20, 20)
        self.scroll_window.SetBackgroundColour(COLOR_PANEL)
        
        self.preview_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_window.SetSizer(self.preview_sizer)
        
        # --- Status Bar ---
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetBackgroundColour(COLOR_BG)
        self.status_bar.SetForegroundColour(COLOR_FG)
        self.status_bar.SetStatusText("Ready")

        # Layout
        main_sizer.Add(top_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.scroll_window, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        self.SetSizer(main_sizer)

    def on_select_file(self, event):
        with wx.FileDialog(self, "Open PDF", wildcard="PDF files (*.pdf)|*.pdf",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            
            path = dlg.GetPath()
            self.selected_file = path
            self.path_text.SetValue(path)
            self.load_preview(path)
            self.btn_convert.Enable()

    def load_preview(self, path):
        # Clear previous preview
        self.preview_sizer.Clear(True)
        self.status_bar.SetStatusText("Loading preview...")
        self.scroll_window.Refresh()
        self.Update() # Force UI update
        
        loading_text = wx.StaticText(self.scroll_window, label="Loading PDF Preview...")
        loading_text.SetForegroundColour(COLOR_FG)
        self.preview_sizer.Add(loading_text, 0, wx.ALIGN_CENTER|wx.ALL, 20)
        self.scroll_window.Layout()
        
        try:
            if self.viewer:
                self.viewer.close()
            
            self.viewer = PDFViewer(path)
            
            self.preview_sizer.Clear(True)
            
            # Limit preview to first 5 pages for performance
            pages_to_show = min(self.viewer.page_count, 5)
            
            width = self.scroll_window.GetClientSize().width - 30 
            if width < 100: width = 600
            
            for i in range(pages_to_show):
                bmp = self.viewer.get_page_bitmap(i, width=width)
                if bmp:
                    sb = wx.StaticBitmap(self.scroll_window, bitmap=bmp)
                    self.preview_sizer.Add(sb, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
            
            if self.viewer.page_count > 5:
                lbl = wx.StaticText(self.scroll_window, label=f"... {self.viewer.page_count - 5} more pages ...")
                lbl.SetForegroundColour(COLOR_FG)
                self.preview_sizer.Add(lbl, 0, wx.ALIGN_CENTER | wx.ALL, 10)

            self.scroll_window.SetVirtualSize(self.preview_sizer.GetMinSize())
            self.scroll_window.Layout()
            self.status_bar.SetStatusText(f"Loaded {path}")
            
        except Exception as e:
            self.status_bar.SetStatusText("Error loading preview")
            wx.MessageBox(f"Failed to load PDF preview: {e}", "Error", wx.ICON_ERROR)

    def on_convert_click(self, event):
        fmt = self.combo_format.GetValue().lower()
        self.start_conversion(fmt)

    def start_conversion(self, fmt):
        # Hide Main Window
        self.Hide()
        
        # Show Progress Dialog
        self.progress_dialog = ConversionProgressDialog(self)
        self.progress_dialog.Show()
        self.progress_dialog.append_log(f"Starting conversion of {os.path.basename(self.selected_file)}...")
        self.progress_dialog.append_log(f"Target format: {fmt.upper()}")
        
        # Start Thread
        thread = threading.Thread(target=self.run_conversion_thread, args=(fmt,))
        thread.start()

    def run_conversion_thread(self, fmt):
        try:
            base_path = os.path.splitext(self.selected_file)[0]
            output_path = f"{base_path}.{fmt}"
            
            if self.progress_dialog:
                self.progress_dialog.append_log("Processing file...")
            
            if fmt == "txt":
                self.logic.convert_to_txt(self.selected_file, output_path)
            elif fmt == "html":
                self.logic.convert_to_html(self.selected_file, output_path)
            elif fmt == "docx":
                self.logic.convert_to_docx(self.selected_file, output_path)
                
            wx.CallAfter(self.on_conversion_complete, output_path)
        except Exception as e:
            wx.CallAfter(self.on_conversion_error, str(e))

    def on_conversion_complete(self, output_path):
        if self.progress_dialog:
            self.progress_dialog.append_log("Conversion Finished!")
            # Small delay or just close? User logic implied dialog just shows status.
            # But normally we might want to see the "Finished" log. 
            # However, user said "then it has a dialog box notification then it shows the main interface only".
            # So I will close the progress dialog and show the MessageBox.
            self.progress_dialog.Destroy()
            self.progress_dialog = None
            
        wx.MessageBox(f"Saved successfully to:\n{output_path}", "Success", wx.ICON_INFORMATION)
        self.Show()
        self.status_bar.SetStatusText("Ready")

    def on_conversion_error(self, err_msg):
        if self.progress_dialog:
            self.progress_dialog.Destroy()
            self.progress_dialog = None
            
        wx.MessageBox(f"Conversion Error:\n{err_msg}", "Error", wx.ICON_ERROR)
        self.Show()
        self.status_bar.SetStatusText("Error")

    def __del__(self):
        if self.viewer:
            self.viewer.close()
