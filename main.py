import wx
import os
import threading
from pdfminer.high_level import extract_text

class PDFConverterFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='PDF to TXT Converter', size=(600, 400))
        
        self.panel = wx.Panel(self)
        self.init_ui()
        self.Center()
        self.Show()

    def init_ui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # File selection area
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.file_picker_btn = wx.Button(self.panel, label='Select PDF File')
        self.file_picker_btn.Bind(wx.EVT_BUTTON, self.on_select_file)
        
        self.file_path_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        
        hbox1.Add(self.file_path_text, proportion=1, flag=wx.RIGHT | wx.EXPAND, border=10)
        hbox1.Add(self.file_picker_btn, flag=wx.EXPAND)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=20)

        # Convert Button
        self.convert_btn = wx.Button(self.panel, label='Convert to TXT')
        self.convert_btn.Bind(wx.EVT_BUTTON, self.on_convert)
        self.convert_btn.Disable()  # Disabled until file is selected
        
        vbox.Add(self.convert_btn, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)

        # Log area
        self.log_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(self.log_text, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=20)

        self.panel.SetSizer(vbox)
        self.selected_file = None

    def on_select_file(self, event):
        with wx.FileDialog(self, "Open PDF file", wildcard="PDF files (*.pdf)|*.pdf",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.selected_file = fileDialog.GetPath()
            self.file_path_text.SetValue(self.selected_file)
            self.convert_btn.Enable()
            self.log_message(f"Selected file: {self.selected_file}")

    def on_convert(self, event):
        if not self.selected_file:
            return
        
        self.convert_btn.Disable()
        self.file_picker_btn.Disable()
        self.log_message("Starting conversion... Please wait.")
        
        # Run conversion in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self.run_conversion, args=(self.selected_file,))
        thread.start()

    def run_conversion(self, pdf_path):
        try:
            output_path = os.path.splitext(pdf_path)[0] + ".txt"
            
            text = extract_text(pdf_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
                
            wx.CallAfter(self.conversion_complete, output_path)
            
        except Exception as e:
            wx.CallAfter(self.conversion_error, str(e))

    def conversion_complete(self, output_path):
        self.log_message(f"Success! Saved to:\n{output_path}")
        wx.MessageBox(f"Conversion completed successfully!\nSaved to: {output_path}", "Success", wx.OK | wx.ICON_INFORMATION)
        self.enable_controls()

    def conversion_error(self, error_msg):
        self.log_message(f"Error: {error_msg}")
        wx.MessageBox(f"An error occurred:\n{error_msg}", "Error", wx.OK | wx.ICON_ERROR)
        self.enable_controls()

    def enable_controls(self):
        self.convert_btn.Enable()
        self.file_picker_btn.Enable()

    def log_message(self, message):
        self.log_text.AppendText(message + "\n")

if __name__ == '__main__':
    app = wx.App()
    frame = PDFConverterFrame()
    app.MainLoop()
