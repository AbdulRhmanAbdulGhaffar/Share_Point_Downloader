import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import yt_dlp
import threading
import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess
import time
import json
import tempfile
import webbrowser
from datetime import datetime

# --- App Constants ---
APP_TITLE = "SharePoint Downloader"
APP_VER = "v1.0 Ultimate Professional"
DEV_NAME = "AbdulRhman AbdulGhaffar"
FFMPEG_URL = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_EXE = "ffmpeg.exe"
CONFIG_FILE = "settings.json"
HISTORY_FILE = "download_history.log"
TEMP_PROFILE_DIR = os.path.join(tempfile.gettempdir(), "SharePointDownloader_Profile")

# --- PROFESSIONAL THEME PALETTE ---
THEME = {
    "bg_main": "#F3F3F3",       # Modern Light Grey
    "bg_card": "#FFFFFF",       # Pure White
    "primary": "#0078D4",       # Windows Blue (Professional)
    "primary_hover": "#106EBE",
    "text_main": "#242424",     # Soft Black
    "text_dim": "#666666",      # Grey Text
    "border": "#E5E5E5",        # Soft Borders
    "success": "#107C10",       # Green
    "error": "#C50F1F",         # Red
    "warning": "#D83B01",       # Orange
    "input": "#FFFFFF",
    "log_bg": "#1E1E1E",        # Dark Background for Logs
    "log_fg": "#D4D4D4"         # Light Text for Logs
}

class UltimateApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} - {APP_VER}")
        self.geometry("1020x780")
        self.configure(bg=THEME["bg_main"])
        
        # High DPI Fix
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except: pass

        self.clean_temp_data()
        self.settings = self.load_settings()

        # --- Variables ---
        self.url_var = tk.StringVar()
        self.save_path_var = tk.StringVar(value=self.settings.get("save_path", os.path.join(os.path.expanduser("~"), "Downloads")))
        self.auth_mode = tk.StringVar(value="browser")
        self.browser_choice = tk.StringVar(value=self.settings.get("browser", "chrome"))
        self.cookie_path = tk.StringVar(value=self.settings.get("cookie_file", ""))
        self.quality_var = tk.StringVar(value=self.settings.get("quality", "Best Available"))
        self.auto_paste_var = tk.BooleanVar(value=self.settings.get("auto_paste", False))
        self.audio_only_var = tk.BooleanVar(value=False)
        self.shutdown_var = tk.BooleanVar(value=False)
        self.proxy_url = tk.StringVar(value=self.settings.get("proxy", ""))
        
        # Dashboard Vars
        self.status_txt = tk.StringVar(value="System Ready")
        self.progress_val = tk.StringVar(value="0%")
        self.speed_txt = tk.StringVar(value="--")
        self.eta_txt = tk.StringVar(value="--")
        self.size_txt = tk.StringVar(value="--")

        self.last_file = None
        self.ffmpeg_ready = False
        self.is_downloading = False
        self.stop_event = threading.Event()

        self.setup_styles()
        self.create_menu()
        self.build_ui()
        self.toggle_auth_inputs()
        
        # Background Tasks
        threading.Thread(target=self.system_check, daemon=True).start()
        self.clipboard_loop()

    def clean_temp_data(self):
        try:
            if os.path.exists(TEMP_PROFILE_DIR):
                shutil.rmtree(TEMP_PROFILE_DIR, ignore_errors=True)
        except: pass

    def load_settings(self):
        default = {
            "save_path": os.path.join(os.path.expanduser("~"), "Downloads"),
            "browser": "chrome",
            "quality": "Best Available",
            "auto_paste": False,
            "cookie_file": "",
            "proxy": ""
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return {**default, **json.load(f)}
            except: pass
        return default

    def save_settings(self):
        data = {
            "save_path": self.save_path_var.get(),
            "browser": self.browser_choice.get(),
            "quality": self.quality_var.get(),
            "auto_paste": self.auto_paste_var.get(),
            "cookie_file": self.cookie_path.get(),
            "proxy": self.proxy_url.get()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except: pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Fonts
        f_head = ("Segoe UI", 10, "bold")
        f_body = ("Segoe UI", 9)
        f_stat = ("Consolas", 10)

        # 1. Base Elements
        style.configure("TFrame", background=THEME["bg_main"])
        style.configure("Card.TFrame", background=THEME["bg_card"], relief="flat")
        style.configure("Border.TFrame", background=THEME["bg_card"], relief="solid", borderwidth=1, bordercolor=THEME["border"])
        
        # 2. Labelframes (Group Boxes)
        style.configure("TLabelframe", background=THEME["bg_main"], bordercolor=THEME["border"], borderwidth=1)
        style.configure("TLabelframe.Label", background=THEME["bg_main"], foreground=THEME["primary"], font=("Segoe UI", 9, "bold"))
        
        # 3. Labels
        style.configure("TLabel", background=THEME["bg_main"], foreground=THEME["text_main"], font=f_body)
        style.configure("Card.TLabel", background=THEME["bg_card"], foreground=THEME["text_main"], font=f_body)
        style.configure("Dim.TLabel", background=THEME["bg_main"], foreground=THEME["text_dim"], font=("Segoe UI", 8))
        style.configure("CardDim.TLabel", background=THEME["bg_card"], foreground=THEME["text_dim"], font=("Segoe UI", 8))
        style.configure("Stat.TLabel", background=THEME["bg_card"], foreground=THEME["primary"], font=f_stat)
        style.configure("StatTitle.TLabel", background=THEME["bg_card"], foreground=THEME["text_dim"], font=("Segoe UI", 8, "bold"))
        
        # 4. Inputs
        style.configure("TEntry", fieldbackground=THEME["input"], bordercolor=THEME["border"], padding=6)
        style.map("TEntry", bordercolor=[("focus", THEME["primary"])])
        
        style.configure("TCombobox", fieldbackground=THEME["input"], padding=6, arrowsize=14, bordercolor=THEME["border"])
        
        style.configure("TRadiobutton", background=THEME["bg_card"], font=("Segoe UI", 9), foreground=THEME["text_main"], indicatorcolor="white")
        style.map("TRadiobutton", indicatorcolor=[("selected", THEME["primary"])])

        style.configure("TCheckbutton", background=THEME["bg_card"], font=f_body, foreground=THEME["text_main"], indicatorcolor="white")
        style.map("TCheckbutton", indicatorcolor=[("selected", THEME["primary"])])

        # 5. Professional Buttons
        # Primary Action
        style.configure("Primary.TButton", background=THEME["primary"], foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=10)
        style.map("Primary.TButton", background=[("active", THEME["primary_hover"]), ("disabled", "#CCCCCC")])
        
        # Secondary Action
        style.configure("Secondary.TButton", background="white", foreground="#333", borderwidth=1, bordercolor=THEME["border"], font=("Segoe UI", 9), padding=6)
        style.map("Secondary.TButton", background=[("active", "#F5F5F5")], bordercolor=[("active", THEME["primary"])])
        
        # Danger Action
        style.configure("Danger.TButton", background="#FDF2F2", foreground=THEME["error"], borderwidth=0, font=("Segoe UI", 10, "bold"), padding=10)
        style.map("Danger.TButton", background=[("active", "#FDE8E8")])

        # Success Action
        style.configure("Success.TButton", background=THEME["success"], foreground="white", borderwidth=0, font=("Segoe UI", 10, "bold"), padding=10)
        style.map("Success.TButton", background=[("active", "#0B6A0B")])

        # 6. Progress Bar
        style.configure("Horizontal.TProgressbar", troughcolor="#E9E9E9", background=THEME["primary"], thickness=10, borderwidth=0)
        style.configure("Success.Horizontal.TProgressbar", troughcolor="#E9E9E9", background=THEME["success"], thickness=10, borderwidth=0)

    def create_menu(self):
        menubar = tk.Menu(self, relief="flat", bg="#FFFFFF")
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Downloads Folder", command=self.open_folder)
        file_menu.add_command(label="View Logs / History", command=self.show_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_checkbutton(label="Auto-Paste Clipboard", variable=self.auto_paste_var, command=self.save_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="Proxy Settings", command=self.open_proxy_settings)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def build_ui(self):
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # 1. Header (Minimalist)
        head_frame = ttk.Frame(main)
        head_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Branding
        logo_box = ttk.Frame(head_frame)
        logo_box.pack(side=tk.LEFT)
        ttk.Label(logo_box, text="⚡", font=("Segoe UI Emoji", 28), foreground=THEME["primary"]).pack(side=tk.LEFT, padx=(0, 15))
        
        title_box = ttk.Frame(logo_box)
        title_box.pack(side=tk.LEFT)
        ttk.Label(title_box, text=APP_TITLE, font=("Segoe UI", 22, "bold"), foreground=THEME["text_main"]).pack(anchor="w")
        ttk.Label(title_box, text=APP_VER, font=("Segoe UI", 10, "bold"), foreground=THEME["success"]).pack(anchor="w")

        # 2. Main Input Area (Card Style)
        src_frame = ttk.Frame(main, style="Border.TFrame", padding=1)
        src_frame.pack(fill=tk.X, pady=(0, 20))
        
        src_inner = ttk.Frame(src_frame, style="Card.TFrame", padding=20)
        src_inner.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(src_inner, text="MEDIA SOURCE URL", style="StatTitle.TLabel").pack(anchor="w", pady=(0, 8))
        
        inp_row = ttk.Frame(src_inner, style="Card.TFrame")
        inp_row.pack(fill=tk.X)
        
        self.ent_url = ttk.Entry(inp_row, textvariable=self.url_var, font=("Segoe UI", 12))
        self.ent_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(inp_row, text="PASTE LINK", style="Primary.TButton", width=14, cursor="hand2", command=self.paste_url).pack(side=tk.RIGHT)
        ttk.Button(inp_row, text="CLEAR", style="Secondary.TButton", width=8, cursor="hand2", command=lambda: self.url_var.set("")).pack(side=tk.RIGHT, padx=(5,0))

        # 3. Settings Grid
        grid_frame = ttk.Frame(main)
        grid_frame.pack(fill=tk.X, pady=(0, 20))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # --- LEFT: Auth ---
        auth_frame = ttk.LabelFrame(grid_frame, text=" ACCESS METHOD ", padding=(20, 15))
        auth_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        r1 = ttk.Frame(auth_frame, style="Card.TFrame")
        r1.pack(fill=tk.X, pady=(5, 10))
        ttk.Radiobutton(r1, text="Auto Browser Login", variable=self.auth_mode, value="browser", command=self.toggle_auth_inputs).pack(side=tk.LEFT)
        self.cb_browser = ttk.Combobox(r1, textvariable=self.browser_choice, values=["chrome", "edge"], state="readonly", width=14)
        self.cb_browser.pack(side=tk.RIGHT)

        r2 = ttk.Frame(auth_frame, style="Card.TFrame")
        r2.pack(fill=tk.X)
        ttk.Radiobutton(r2, text="Import Cookies File", variable=self.auth_mode, value="cookie", command=self.toggle_auth_inputs).pack(side=tk.LEFT)
        self.btn_cookie = ttk.Button(r2, text="Browse", style="Secondary.TButton", width=8, cursor="hand2", command=self.browse_cookie)
        self.btn_cookie.pack(side=tk.RIGHT)
        self.ent_cookie = ttk.Entry(r2, textvariable=self.cookie_path, width=15)
        self.ent_cookie.pack(side=tk.RIGHT, padx=(0, 5))
        
        ttk.Label(auth_frame, text="* Browser login is more stable for MFA.", style="CardDim.TLabel").pack(anchor="w", pady=(15, 0))

        # --- RIGHT: Config ---
        set_frame = ttk.LabelFrame(grid_frame, text=" CONFIGURATION ", padding=(20, 15))
        set_frame.grid(row=0, column=1, sticky="nsew")
        
        # Path
        f_path = ttk.Frame(set_frame, style="Card.TFrame")
        f_path.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(f_path, text="Save Location:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(f_path, text="Change", style="Secondary.TButton", width=8, cursor="hand2", command=self.browse_folder).pack(side=tk.RIGHT)
        ttk.Entry(f_path, textvariable=self.save_path_var, state="readonly").pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Quality
        f_fmt = ttk.Frame(set_frame, style="Card.TFrame")
        f_fmt.pack(fill=tk.X)
        ttk.Label(f_fmt, text="Quality:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.cb_qual = ttk.Combobox(f_fmt, textvariable=self.quality_var, values=["Best Available", "1080p", "720p"], state="readonly", width=18)
        self.cb_qual.pack(side=tk.LEFT)
        
        f_opt = ttk.Frame(set_frame, style="Card.TFrame")
        f_opt.pack(fill=tk.X, pady=(15, 0))
        ttk.Checkbutton(f_opt, text="Audio Only (MP3)", variable=self.audio_only_var).pack(side=tk.LEFT)
        ttk.Checkbutton(f_opt, text="Shutdown on Finish", variable=self.shutdown_var).pack(side=tk.RIGHT)

        # 4. Dashboard (Status & Progress)
        dash_frame = ttk.Frame(main, style="Border.TFrame", padding=1)
        dash_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        dash_in = ttk.Frame(dash_frame, style="Card.TFrame", padding=25)
        dash_in.pack(fill=tk.BOTH, expand=True)
        
        # Stats
        stat_row = ttk.Frame(dash_in, style="Card.TFrame")
        stat_row.pack(fill=tk.X, pady=(0, 15))
        
        def mk_stat(parent, title, var):
            f = ttk.Frame(parent, style="Card.TFrame")
            ttk.Label(f, text=title, style="StatTitle.TLabel").pack(anchor="w")
            ttk.Label(f, textvariable=var, style="Stat.TLabel").pack(anchor="w")
            return f

        mk_stat(stat_row, "STATUS", self.status_txt).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Separator(stat_row, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=20)
        mk_stat(stat_row, "SPEED", self.speed_txt).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Separator(stat_row, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=20)
        mk_stat(stat_row, "ETA", self.eta_txt).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Progress
        self.prog = ttk.Progressbar(dash_in, mode='determinate', style="Horizontal.TProgressbar")
        self.prog.pack(fill=tk.X, pady=(0, 20))

        # Action Buttons
        act_row = ttk.Frame(dash_in, style="Card.TFrame")
        act_row.pack(fill=tk.X)

        self.btn_cancel = ttk.Button(act_row, text="CANCEL OPERATION", style="Danger.TButton", cursor="hand2", command=self.cancel_download, state="disabled")
        self.btn_cancel.pack(side=tk.LEFT)
        
        self.btn_start = ttk.Button(act_row, text="START DOWNLOAD", style="Primary.TButton", width=25, cursor="hand2", command=self.start_download)
        self.btn_start.pack(side=tk.RIGHT)
        
        # Success Buttons
        self.btn_open_f = ttk.Button(act_row, text="OPEN FOLDER", style="Secondary.TButton", cursor="hand2", command=self.open_folder)
        self.btn_play = ttk.Button(act_row, text="PLAY FILE", style="Success.TButton", cursor="hand2", command=self.open_file)
        self.btn_reset = ttk.Button(act_row, text="NEW TASK", style="Primary.TButton", cursor="hand2", command=self.reset_ui)

        # 5. Professional Dark Log (The key feature)
        # ----------------------------------------------------
        log_frame = ttk.Frame(main)
        log_frame.pack(fill=tk.X)
        
        log_label = ttk.Label(log_frame, text="SYSTEM EVENT LOG", font=("Segoe UI", 8, "bold"), foreground="#666")
        log_label.pack(anchor="w", pady=(0, 5))
        
        self.log_area = scrolledtext.ScrolledText(
            log_frame, 
            height=6, 
            font=("Consolas", 9), 
            state='disabled', 
            relief="flat", 
            borderwidth=0,
            bg=THEME["log_bg"],     # Dark Background
            fg=THEME["log_fg"],     # Light Text
            selectbackground="#404040",
            insertbackground="white"
        )
        self.log_area.pack(fill=tk.X)
        # ----------------------------------------------------
        
        # 6. Footer (Credits)
        foot_frame = ttk.Frame(main)
        foot_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(foot_frame, text=f"Developed by {DEV_NAME}", font=("Segoe UI", 9), foreground="#999").pack(side=tk.RIGHT)

    # --- Feature Windows ---
    def open_proxy_settings(self):
        win = tk.Toplevel(self)
        win.title("Network Settings")
        win.geometry("450x200")
        win.configure(bg=THEME["bg_card"])
        
        ttk.Label(win, text="Proxy Configuration", font=("Segoe UI", 12, "bold"), background=THEME["bg_card"], foreground=THEME["text_main"]).pack(pady=15)
        
        f = ttk.Frame(win, style="Card.TFrame", padding=15)
        f.pack(fill=tk.X)
        
        ttk.Label(f, text="Proxy URL:", style="Card.TLabel").pack(anchor="w")
        ttk.Entry(f, textvariable=self.proxy_url, width=50).pack(fill=tk.X, pady=8)
        ttk.Label(f, text="Format: http://user:pass@host:port", style="CardDim.TLabel").pack(anchor="w")
        
        ttk.Button(win, text="Save Configuration", style="Primary.TButton", cursor="hand2", command=lambda: [self.save_settings(), win.destroy()]).pack(pady=10)

    def show_history(self):
        if not os.path.exists(HISTORY_FILE):
            messagebox.showinfo("History", "No downloads history found.")
            return
            
        win = tk.Toplevel(self)
        win.title("Download History")
        win.geometry("700x500")
        win.configure(bg=THEME["bg_main"])
        
        txt = scrolledtext.ScrolledText(win, font=("Consolas", 10), bg="#FFFFFF", fg="#333")
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            txt.insert(tk.END, f.read())
        txt.config(state='disabled')

    # --- Core Logic ---
    def log(self, msg, type="info"):
        self.after(0, lambda: self._log_main(msg, type))

    def _log_main(self, msg, type):
        self.log_area.config(state='normal')
        
        # Colors for the Dark Log
        color = "#CCCCCC" # Default Light Grey
        if type == "error": color = "#FF6B6B"   # Soft Red
        elif type == "success": color = "#51CF66" # Soft Green
        elif type == "sys": color = "#339AF0"     # Soft Blue
        elif type == "warning": color = "#FCC419" # Soft Yellow
        
        t = time.strftime("[%H:%M:%S]")
        self.log_area.tag_config(type, foreground=color)
        
        # Insert line
        self.log_area.insert(tk.END, f"{t} ", "sys")
        self.log_area.insert(tk.END, f"{msg}\n", type)
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def save_to_history(self, filename, url):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {filename}\nURL: {url}\n-----------------------------------\n")
        except: pass

    def perform_shutdown(self):
        self.log("Auto-shutdown initiated in 60 seconds...", "warning")
        try:
            if os.name == 'nt':
                os.system("shutdown /s /t 60")
            else:
                os.system("shutdown -h +1")
            messagebox.showwarning("Auto-Shutdown", "PC will shut down in 60s.\nRun 'shutdown /a' in CMD to cancel.")
        except Exception as e:
            self.log(f"Shutdown failed: {e}", "error")

    # --- Standard Methods ---
    def toggle_auth_inputs(self):
        if self.auth_mode.get() == "browser":
            self.cb_browser.config(state="readonly")
            self.ent_cookie.config(state="disabled")
            self.btn_cookie.config(state="disabled")
        else:
            self.cb_browser.config(state="disabled")
            self.ent_cookie.config(state="normal")
            self.btn_cookie.config(state="normal")

    def clipboard_loop(self):
        if self.auto_paste_var.get():
            try:
                txt = self.clipboard_get()
                curr = self.url_var.get()
                if txt != curr and ("sharepoint.com" in txt or "microsoftstream" in txt) and txt.startswith("http"):
                    self.url_var.set(txt)
                    self.log("Link detected from clipboard.", "sys")
            except: pass
        self.after(1500, self.clipboard_loop)
        
    def browse_cookie(self):
        f = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if f: self.cookie_path.set(f); self.save_settings()

    def browse_folder(self):
        d = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if d: self.save_path_var.set(d); self.save_settings()

    def paste_url(self):
        try: self.url_var.set(self.clipboard_get())
        except: pass

    def open_file(self):
        if self.last_file and os.path.exists(self.last_file): os.startfile(self.last_file)

    def open_folder(self):
        path = self.save_path_var.get()
        if os.path.exists(path): os.startfile(path)
        
    def show_about(self):
        messagebox.showinfo("About", f"{APP_TITLE}\n{APP_VER}\nDev: {DEV_NAME}")

    def system_check(self):
        self.log("Initializing System...", "sys")
        if self.check_ffmpeg():
            self.ffmpeg_ready = True
            self.status_txt.set("Ready")
            self.log("Core components loaded.", "success")
        else:
            self.status_txt.set("Installing Components...")
            self.download_ffmpeg()

    def check_ffmpeg(self):
        if not os.path.exists(FFMPEG_EXE): return False
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.check_output([FFMPEG_EXE, "-version"], stderr=subprocess.STDOUT, startupinfo=si)
            return True
        except: return False

    def download_ffmpeg(self):
        try:
            self.prog.config(mode='indeterminate')
            self.prog.start(15)
            self.log("Downloading FFmpeg components...", "warning")
            urllib.request.urlretrieve(FFMPEG_URL, "ffmpeg.zip")
            with zipfile.ZipFile("ffmpeg.zip", 'r') as z:
                for f in z.namelist():
                    if f.endswith("ffmpeg.exe"):
                        with z.open(f) as s, open(FFMPEG_EXE, "wb") as d: shutil.copyfileobj(s, d)
                        break
            os.remove("ffmpeg.zip")
            if self.check_ffmpeg():
                self.ffmpeg_ready = True
                self.status_txt.set("Ready")
                self.log("Components installed.", "success")
            else: self.status_txt.set("Component Error")
        except Exception as e: 
            self.log(f"Setup Error: {str(e)}", "error")
        finally:
            self.prog.stop()
            self.prog.config(mode='determinate')
            self.prog['value'] = 0

    def start_download(self):
        url = self.url_var.get().strip()
        if not url: return messagebox.showwarning("Required", "Please provide a valid URL.")
        if not self.ffmpeg_ready: return messagebox.showwarning("Wait", "System is initializing...")

        self.is_downloading = True
        self.stop_event.clear()
        
        self.btn_start.pack_forget()
        self.btn_cancel.config(state="normal")
        self.prog.config(style="Horizontal.TProgressbar")
        self.progress_val.set("0%")
        self.prog['value'] = 0
        self.status_txt.set("Processing...")
        
        mode = self.auth_mode.get()
        threading.Thread(target=self.process, args=(url, mode), daemon=True).start()

    def cancel_download(self):
        if self.is_downloading:
            if messagebox.askyesno("Confirm", "Cancel current operation?"):
                self.stop_event.set()
                self.status_txt.set("Stopping...")
                self.log("Operation cancelled by user.", "warning")

    def process(self, url, mode):
        self.clean_temp_data()
        save_dir = self.save_path_var.get()
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        
        is_audio = self.audio_only_var.get()
        ext = "mp3" if is_audio else "%(ext)s"
        tmpl = os.path.join(save_dir, f'%(title).100s.{ext}')
        
        q_map = {
            "Best Available": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best"
        }
        fmt = q_map.get(self.quality_var.get(), "best")

        opts = {
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'progress_hooks': [self.hook],
            'ffmpeg_location': os.getcwd(),
            'quiet': True, 'no_warnings': True,
            'outtmpl': tmpl,
            'overwrites': True,
            'proxy': self.proxy_url.get() if self.proxy_url.get() else None
        }

        if is_audio:
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
        else:
            opts['format'] = fmt
            opts['merge_output_format'] = 'mp4'

        if mode == "cookie":
            cf = self.cookie_path.get()
            if not os.path.exists(cf): return self.fail("Cookie file missing.")
            opts['cookiefile'] = cf
        else:
            brow = self.browser_choice.get()
            exe = self.find_browser(brow)
            if not exe: return self.fail(f"{brow} not installed.")
            try:
                self.launch_iso(exe, url)
                opts['cookiesfrombrowser'] = (brow, TEMP_PROFILE_DIR)
            except Exception as e: return self.fail(str(e))

        if self.stop_event.is_set(): return self.fail("Cancelled")

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                self.log("Acquiring metadata...", "sys")
                info = ydl.extract_info(url, download=False)
                self.log(f"Target: {info.get('title', 'Unknown')}", "success")
                
                fname = ydl.prepare_filename(info)
                if is_audio: fname = os.path.splitext(fname)[0] + ".mp3"
                elif fname.endswith((".webm", ".mkv")): fname = os.path.splitext(fname)[0] + ".mp4"
                self.last_file = fname
                
                if not self.stop_event.is_set():
                    self.log("Starting data transfer...", "sys")
                    ydl.download([url])
                else: return self.fail("Cancelled")
                
            self.success(fname, url)
        except Exception as e:
            if not self.stop_event.is_set(): self.fail(str(e))
        finally:
            self.clean_temp_data()

    def find_browser(self, name):
        target = "chrome.exe" if name == "chrome" else "msedge.exe"
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for p in paths:
            if os.path.exists(p) and p.lower().endswith(target): return p
        return None

    def launch_iso(self, exe, url):
        self.status_txt.set("Authentication Action Required")
        self.log(">> PLEASE LOG IN -> REFRESH -> CLOSE BROWSER <<", "warning")
        subprocess.run([exe, f"--user-data-dir={TEMP_PROFILE_DIR}", "--no-first-run", url])
        self.status_txt.set("Resuming...")
        self.log("Auth session captured.", "sys")

    def hook(self, d):
        if self.stop_event.is_set(): raise Exception("Cancelled")
        if d['status'] == 'downloading':
            try:
                p = float(d.get('_percent_str', '0%').replace('%',''))
                self.prog['value'] = p
                self.progress_val.set(f"{int(p)}%")
                self.speed_txt.set(d.get('_speed_str', '--'))
                self.eta_txt.set(d.get('_eta_str', '--'))
                self.size_txt.set(d.get('_total_bytes_str', '--'))
                self.status_txt.set("Downloading...")
            except: pass
        elif d['status'] == 'finished':
            self.status_txt.set("Finalizing...")
            self.log("Processing media streams...", "sys")
            self.prog.config(mode='indeterminate')
            self.prog.start(20)

    def fail(self, err):
        self.log(str(err), "error")
        self.after(0, lambda: messagebox.showerror("Error", str(err)))
        self.after(0, self.reset_ui)

    def success(self, fname, url):
        self.save_to_history(fname, url)
        if self.shutdown_var.get():
            self.after(0, self.perform_shutdown)
        self.after(0, self._succ_ui)

    def _succ_ui(self):
        self.status_txt.set("Task Complete")
        self.log("Download finished successfully.", "success")
        self.prog.stop()
        self.prog.config(mode='determinate', style="Success.Horizontal.TProgressbar")
        self.prog['value'] = 100
        self.progress_val.set("100%")

        self.btn_cancel.config(state="disabled")
        self.btn_open_f.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_play.pack(side=tk.LEFT)
        self.btn_reset.pack(side=tk.RIGHT)

    def reset_ui(self):
        self.is_downloading = False
        self.prog.config(style="Horizontal.TProgressbar")
        self.prog['value'] = 0
        self.progress_val.set("0%")
        self.status_txt.set("Ready")

        self.btn_open_f.pack_forget()
        self.btn_play.pack_forget()
        self.btn_reset.pack_forget()
        self.btn_cancel.config(state="disabled")
        self.btn_start.pack(side=tk.RIGHT)

if __name__ == "__main__":
    app = UltimateApp()
    app.mainloop()