import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from time import strftime
import random
import mysql.connector
import pandas as pd
from PIL import Image, ImageTk  # REQUIRES PILLOW: pip install Pillow
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",        
            password="faiza2426,./",        
            database="hospital_management"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"MySQL Connection Failed: {err}")
        return None

def initialize_database():
    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(50) PRIMARY KEY,
        password VARCHAR(100) NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(50)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50),
        dob DATE,
        gender VARCHAR(20),
        medical_history TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        provider_id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50),
        specialty VARCHAR(100),
        fee DECIMAL(10,2),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appt_id VARCHAR(50) PRIMARY KEY,
        patient_id VARCHAR(50),
        provider_id VARCHAR(50),
        appt_date DATE,
        appt_time TIME,
        status VARCHAR(50) DEFAULT 'Scheduled',
        priority VARCHAR(20) DEFAULT 'Normal',
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        staff_id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50),
        role VARCHAR(100),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        shift_id VARCHAR(50) PRIMARY KEY,
        staff_id VARCHAR(50),
        start_time TIME,
        end_time TIME,
        FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE
    )""")
        
    conn.commit()
    cursor.close()
    conn.close()

# ==========================================
# 2. MAIN APPLICATION CORE ENGINE
# ==========================================
class ModernMedicalSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AURA - Redesigned Dashboard & New High-Quality Celebration Engine")
        self.geometry("1350x850")
        self.state('zoomed') 
        
        self.themes = {
            "Aura Rose ✨": {"bg": "#FFF5F7", "panel": "#FFFFFF", "accent": "#FF007F", "text": "#1A1A2E", "card1": "#FFEBEE", "card2": "#E0F2F1", "card3": "#E3F2FD"},
            "Neon Cyberpunk 🌌": {"bg": "#0D1117", "panel": "#161B22", "accent": "#00FFFF", "text": "#C9D1D9", "card1": "#21262D", "card2": "#30363D", "card3": "#1F2937"},
            "Classic Dark Mode 🌙": {"bg": "#1F232A", "panel": "#2A303C", "accent": "#A6ADBB", "text": "#F8F9FA", "card1": "#384152", "card2": "#2D3748", "card3": "#1A202C"},
            "Mint Fresh 🌿": {"bg": "#E8F5E9", "panel": "#FFFFFF", "accent": "#2E7D32", "text": "#1B5E20", "card1": "#C8E6C9", "card2": "#E8F5E9", "card3": "#D1E7DD"}
        }
        
        self.current_theme = "Aura Rose ✨"
        self.bg_base_clean = self.themes[self.current_theme]["bg"]
        self.text_dark = self.themes[self.current_theme]["text"]
        
        self.neon_glows = ["#FF007F", "#00FFFF", "#39FF14", "#FF00FF", "#FFD700", "#FF4500"]
        self.flower_pool = ["🌸", "💖", "✨", "🌻", "🌹", "🌷", "🍃", "🦋", "💘", "🎉", "🌈", "⭐", "💎", "💥", "🎈"]
        self.input_colors = ["#FFC0CB", "#E0FFFF", "#EAFAF1", "#FEF9E7", "#F3E5F5", "#EBF5FB", "#FADBD8"]
        self.matrix_row_colors = ["#FFEBEE", "#E0F2F1", "#E8F5E9", "#FFFDE7", "#F3E5F5", "#E3F2FD"]

        self.configure(bg=self.bg_base_clean)
        
        if not os.path.exists("bills"):
            os.makedirs("bills")
            
        initialize_database()
        self.setup_styles()
        self.create_layout()
        self.time_now() 
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TNotebook", background=self.bg_base_clean, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#eaeaea", foreground="#1A1A2E", 
                             padding=[18, 8], font=("Segoe UI Semibold", 10), borderwidth=0)
        self.style.map("TNotebook.Tab", background=[("selected", "#FF007F")], foreground=[("selected", "#FFFFFF")])
        
        self.style.configure("Treeview", background="#FFFFFF", foreground="#1A1A2E", 
                             fieldbackground="#FFFFFF", rowheight=36, font=("Segoe UI Semibold", 9), borderwidth=0)
        self.style.configure("Treeview.Heading", background="#1A1A2E", foreground="#FFFFFF", 
                             font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
        self.style.map("Treeview", background=[("selected", "#FFC0CB")], foreground=[("selected", "#1A1A2E")])

    def change_theme_engine(self, selected_theme):
        self.current_theme = selected_theme
        t = self.themes[selected_theme]
        self.bg_base_clean = t["bg"]
        self.text_dark = t["text"]
        
        self.configure(bg=t["bg"])
        self.header_frame.config(bg=t["panel"], highlightbackground=t["accent"])
        self.header_title.config(fg=t["accent"], bg=t["panel"])
        self.clock_label.config(fg=t["text"], bg=t["panel"])
        self.style.configure("TNotebook", background=t["bg"])
        self.style.configure("Treeview.Heading", background=t["accent"])
        self.style.map("TNotebook.Tab", background=[("selected", t["accent"])])
        
        self.refresh_analytics()
        messagebox.showinfo("Theme Synced", f"System successfully morphed into {selected_theme} mode!")

    def apply_background_emojis(self, widget, density=15):
        widget.update_idletasks()
        w = widget.winfo_width() if widget.winfo_width() > 100 else 500
        h = widget.winfo_height() if widget.winfo_height() > 100 else 400
        
        for _ in range(density):
            rx = random.randint(15, w - 45)
            ry = random.randint(15, h - 45)
            emoji = random.choice(self.flower_pool)
            color = random.choice(["#FFB6C1", "#FF69B4", "#FF1493", "#9370DB", "#40E0D0"])
            
            lbl = tk.Label(widget, text=emoji, fg=color, bg=widget.cget("bg"), font=("Segoe UI", random.randint(12, 22)))
            lbl.place(x=rx, y=ry)
            lbl.lower()

    def apply_neon_glow(self, widget, normal_bg, active_glow):
        widget.config(highlightbackground="#BDC3C7", highlightthickness=1, bd=0)
        widget.bind("<FocusIn>", lambda e: widget.config(bg="#FFFFFF", highlightthickness=2, highlightcolor=active_glow))
        widget.bind("<FocusOut>", lambda e: widget.config(bg=normal_bg, highlightthickness=1, highlightcolor="#BDC3C7"))

    def register_button_transition(self, btn, click_bg, reset_bg):
        def on_click(event):
            btn.config(bg=click_bg, fg="#FFFFFF", relief=tk.SUNKEN)
            self.update_idletasks()
        def on_release(event):
            btn.config(bg=reset_bg, fg="white" if reset_bg != "#00FFFF" else "#1A1A2E", relief=tk.FLAT)
        btn.bind("<Button-1>", on_click)
        btn.bind("<ButtonRelease-1>", on_release)

    # --------------------------------------
    # HIGH-QUALITY CELEBRATION ENGINE v2
    # --------------------------------------
    def trigger_grand_celebration(self, success_msg="Operation Successful!"):
        celebration_win = tk.Toplevel(self)
        celebration_win.overrideredirect(True)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        celebration_win.geometry(f"{sw}x{sh}+0+0")
        celebration_win.configure(bg="#0B0C10")  # Cinematic dark backdrop
        celebration_win.attributes("-alpha", 0.0) # Start transparent for smooth fade-in
        celebration_win.lift()

        # Smooth Fade-In effect
        def fade_in(alpha=0.0):
            if alpha < 0.95:
                alpha += 0.08
                celebration_win.attributes("-alpha", alpha)
                self.after(20, lambda: fade_in(alpha))
        fade_in()

        # Premium Glassmorphism Centered Card Frame
        msg_frame = tk.Frame(celebration_win, bg="#1F2833", highlightbackground="#00FFFF", highlightthickness=2, bd=0)
        msg_frame.place(relx=0.5, rely=0.45, anchor=tk.CENTER, width=600, height=260)
        
        title_lbl = tk.Label(msg_frame, text="✨ TRANSACTION MARGIN SECURED ✨", font=("Segoe UI", 14, "bold"), fg="#00FFFF", bg="#1F2833")
        title_lbl.pack(pady=(25, 10))
        
        # Color Shifting Alert Text Protocol
        def cycle_text_glow():
            if celebration_win.winfo_exists():
                title_lbl.config(fg=random.choice(self.neon_glows))
                self.after(350, cycle_text_glow)
        cycle_text_glow()

        tk.Label(msg_frame, text=success_msg, font=("Segoe UI Semibold", 11), fg="#C9D1D9", bg="#1F2833", wraplength=520, justify="center").pack(pady=10)
        
        # Smooth Fade Out Dismissal Button
        def smooth_exit():
            def fade_out(alpha=celebration_win.attributes("-alpha")):
                if alpha > 0.05:
                    alpha -= 0.08
                    celebration_win.attributes("-alpha", alpha)
                    self.after(15, fade_out)
                else:
                    celebration_win.destroy()
            fade_out()

        close_btn = tk.Button(msg_frame, text="⚡ Dismiss Operational Layer", bg="#FF007F", fg="white", font=("Segoe UI", 10, "bold"),
                             command=smooth_exit, relief=tk.FLAT, bd=0, cursor="hand2", padx=25, pady=8)
        close_btn.pack(pady=20)
        self.register_button_transition(close_btn, "#FF00FF", "#FF007F")

        # Deploy Advanced Floating Particle Rain Stream
        for _ in range(120):
            sx = random.randint(0, sw)
            sy = random.randint(-400, 0)
            lbl = tk.Label(celebration_win, text=random.choice(self.flower_pool), font=("Segoe UI", random.randint(18, 45)), fg=random.choice(self.neon_glows), bg="#0B0C10")
            lbl.place(x=sx, y=sy)
            # Added unique horizontal velocity bounds for high dynamic fluid animation looks
            self.animate_celebration_drop(lbl, random.randint(5, 14), random.randint(-4, 4), sh, celebration_win)

    def animate_celebration_drop(self, label, speed_y, speed_x, max_h, container):
        if not container.winfo_exists(): return
        ny = label.winfo_y() + speed_y
        nx = label.winfo_x() + speed_x
        
        # Dynamic boundaries check to cycle falling items smoothly
        if ny > max_h:
            ny = random.randint(-150, -20)
            nx = random.randint(0, container.winfo_width())
        label.place(x=nx, y=ny)
        self.after(20, lambda: self.animate_celebration_drop(label, speed_y, speed_x, max_h, container))

    def create_layout(self):
        self.header_frame = tk.Frame(self, bg="#FFFFFF", height=85, bd=0, highlightbackground="#FF007F", highlightthickness=1)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_frame.pack_propagate(False)
        
        self.header_title = tk.Label(self.header_frame, text="🌸 AURA ADVANCED MEDICAL MANAGEMENT NODE", 
                 fg="#FF007F", bg="#FFFFFF", font=("Segoe UI", 15, "bold"))
        self.header_title.pack(side=tk.LEFT, padx=30, pady=25)
        
        theme_bar = tk.Frame(self.header_frame, bg="#FFFFFF")
        theme_bar.pack(side=tk.RIGHT, padx=15, pady=25)
        tk.Label(theme_bar, text="Theme:", font=("Segoe UI Semibold", 9), bg="#FFFFFF", fg="#555555").pack(side=tk.LEFT, padx=5)
        self.theme_menu = ttk.Combobox(theme_bar, values=list(self.themes.keys()), state="readonly", width=16)
        self.theme_menu.set(self.current_theme)
        self.theme_menu.bind("<<ComboboxSelected>>", lambda e: self.change_theme_engine(self.theme_menu.get()))
        self.theme_menu.pack(side=tk.LEFT)
        
        self.clock_label = tk.Label(self.header_frame, text="", font=("Segoe UI", 11, "bold"), fg="#1A1A2E", bg="#FFFFFF")
        self.clock_label.pack(side=tk.RIGHT, padx=20, pady=25)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.build_analytics_tab()
        self.build_appointment_tab()
        self.build_patient_tab()
        self.build_provider_tab()
        self.build_staff_tab()

    def time_now(self):
        current = strftime('%I:%M:%S %p | %A, %B %d, %Y')
        self.clock_label.configure(text=current)
        self.clock_label.after(1000, self.time_now)

    # --------------------------------------
    # TAB 1: UNIQUE DESIGN DASHBOARD OVERVIEW
    # --------------------------------------
    def build_analytics_tab(self):
        self.tab_analytics = tk.Frame(self.notebook, bg="#FFF5F5")
        self.notebook.add(self.tab_analytics, text="   Dashboard Overview   ")
        
        top_monitor_bar = tk.Frame(self.tab_analytics, bg="#FFFFFF", height=50, highlightbackground="#EBF5FB", highlightthickness=1)
        top_monitor_bar.pack(fill=tk.X, padx=25, pady=(20, 5))
        
        tk.Label(top_monitor_bar, text="⚙️ SYSTEM ARCHITECTURE STATUS:", font=("Segoe UI", 9, "bold"), fg="#7F8C8D", bg="#FFFFFF").pack(side=tk.LEFT, padx=15, pady=15)
        self.lbl_db_status = tk.Label(top_monitor_bar, text="● ONLINE STATUS SECURE", font=("Segoe UI", 10, "bold"), fg="#39FF14", bg="#FFFFFF")
        self.lbl_db_status.pack(side=tk.LEFT, padx=5)

        middle_split_frame = tk.Frame(self.tab_analytics, bg="#FFF5F5")
        middle_split_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)
        
        left_cards_container = tk.LabelFrame(middle_split_frame, text=" Live Operations Flow Counters ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        left_cards_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.c1 = tk.Frame(left_cards_container, bg="#FFEBEE", height=90, highlightbackground="#FF007F", highlightthickness=1)
        self.c1.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(self.c1, text="TOTAL ACCOUNT REVENUE", bg="#FFEBEE", fg="#C2185B", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(8, 2))
        self.lbl_revenue = tk.Label(self.c1, text="PKR 0.00", bg="#FFEBEE", font=("Segoe UI", 16, "bold"), fg="#1A1A2E")
        self.lbl_revenue.pack(anchor="w", padx=15, pady=(0, 8))
        
        self.c2 = tk.Frame(left_cards_container, bg="#E0F2F1", height=90, highlightbackground="#00FFFF", highlightthickness=1)
        self.c2.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(self.c2, text="COMPLETED CLINICAL SESSIONS", bg="#E0F2F1", fg="#004D40", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(8, 2))
        self.lbl_count = tk.Label(self.c2, text="0 Sessions", bg="#E0F2F1", font=("Segoe UI", 16, "bold"), fg="#1A1A2E")
        self.lbl_count.pack(anchor="w", padx=15, pady=(0, 8))

        self.c3 = tk.Frame(left_cards_container, bg="#E3F2FD", height=90, highlightbackground="#39FF14", highlightthickness=1)
        self.c3.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(self.c3, text="SYNCHRONIZED CLIENT PROFILES", bg="#E3F2FD", fg="#0D47A1", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(8, 2))
        self.lbl_patients_total = tk.Label(self.c3, text="0 Files", bg="#E3F2FD", font=("Segoe UI", 16, "bold"), fg="#1A1A2E")
        self.lbl_patients_total.pack(anchor="w", padx=15, pady=(0, 8))

        # --- ADVANCED FEATURE: METRICS VISUALIZER PROGRESS BARS ---
        self.visualizer_frame = tk.LabelFrame(middle_split_frame, text=" 📊 Live Resource Load Visualizer ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        self.visualizer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(self.visualizer_frame, text="Patient Admission Capacity Load:", font=("Segoe UI", 9), bg="#FFFFFF").pack(anchor="w", padx=15, pady=(15,2))
        self.progress_pats = ttk.Progressbar(self.visualizer_frame, orient="horizontal", length=220, mode="determinate")
        self.progress_pats.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(self.visualizer_frame, text="Consultation Targets Completed:", font=("Segoe UI", 9), bg="#FFFFFF").pack(anchor="w", padx=15, pady=(15,2))
        self.progress_rev = ttk.Progressbar(self.visualizer_frame, orient="horizontal", length=220, mode="determinate")
        self.progress_rev.pack(fill=tk.X, padx=15, pady=5)

        action_center_frame = tk.LabelFrame(self.tab_analytics, text=" ⚡ Quick Action Shortcut Center ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        action_center_frame.pack(fill=tk.X, padx=25, pady=(5, 25))
        
        sync_btn = tk.Button(action_center_frame, text="🔮 Synchronize System Core Ledger", bg="#FF007F", fg="white", font=("Segoe UI", 9, "bold"), 
                  command=lambda: [self.refresh_analytics(), self.trigger_grand_celebration("System Core Architecture Resynced with Live MySQL Schema Engine!")], relief=tk.FLAT, bd=0, cursor="hand2", width=30, height=2)
        sync_btn.pack(side=tk.LEFT, padx=20, pady=15)
        self.register_button_transition(sync_btn, "#FF00FF", "#FF007F")
        
        backup_btn = tk.Button(action_center_frame, text="💾 Deploy Cloud Database Backup", bg="#39FF14", fg="#1A1A2E", font=("Segoe UI", 9, "bold"), 
                  command=lambda: self.trigger_grand_celebration("Transaction Ledger safely deployed to remote cloud mirroring infrastructure."), relief=tk.FLAT, bd=0, cursor="hand2", width=30, height=2)
        backup_btn.pack(side=tk.LEFT, padx=10, pady=15)
        self.register_button_transition(backup_btn, "#00FFFF", "#39FF14")
                  
        self.refresh_analytics()
        self.after(200, lambda: [self.apply_background_emojis(self.tab_analytics, 20), self.apply_background_emojis(left_cards_container, 8), self.apply_background_emojis(self.visualizer_frame, 8)])

    def refresh_analytics(self):
        conn = get_db_connection()
        if not conn: 
            self.lbl_db_status.config(text="● OFFLINE", fg="#FF4500")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(p.fee) FROM appointments a JOIN providers p ON a.provider_id = p.provider_id WHERE a.status = 'Completed'")
        res = cursor.fetchone()
        count = res[0] if res[0] else 0
        rev = res[1] if res[1] else 0.0
        
        cursor.execute("SELECT COUNT(*) FROM patients")
        tot_pats = cursor.fetchone()[0]
        
        self.lbl_revenue.config(text=f"PKR {rev:,.2f}")
        self.lbl_count.config(text=f"{count} Actions Completed")
        self.lbl_patients_total.config(text=f"{tot_pats} Active Profiles")
        
        # Dynamic Progress Tracking updates
        self.progress_pats['value'] = min((tot_pats / 50) * 100, 100) # Target baseline 50 profiles
        self.progress_rev['value'] = min((count / 30) * 100, 100) # Target baseline 30 operations
        
        cursor.close()
        conn.close()

    # --------------------------------------
    # TAB 2: APPOINTMENTS DESK
    # --------------------------------------
    def build_appointment_tab(self):
        tab = tk.Frame(self.notebook, bg="#E0FFFF")
        self.notebook.add(tab, text="   Appointments Core Desk   ")

        form_frame = tk.LabelFrame(tab, text=" Scheduling Form Panel ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        tk.Label(form_frame, text="Select Target Patient:", bg="#FFFFFF", fg="#1A1A2E").grid(row=0, column=0, sticky=tk.W, padx=15, pady=8)
        self.cb_patients = ttk.Combobox(form_frame, width=22, font=("Segoe UI", 10), state="readonly")
        self.cb_patients.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(form_frame, text="Assign Doctor Expert:", bg="#FFFFFF", fg="#1A1A2E").grid(row=1, column=0, sticky=tk.W, padx=15, pady=8)
        self.cb_providers = ttk.Combobox(form_frame, width=22, font=("Segoe UI", 10), state="readonly")
        self.cb_providers.grid(row=1, column=1, padx=15, pady=8)

        tk.Label(form_frame, text="Date Entry (YYYY-MM-DD):", bg="#FFFFFF", fg="#1A1A2E").grid(row=2, column=0, sticky=tk.W, padx=15, pady=8)
        self.ent_appt_date = tk.Entry(form_frame, font=("Segoe UI", 10, "bold"), width=24, bg=self.input_colors[0], fg="#1A1A2E")
        self.ent_appt_date.grid(row=2, column=1, padx=15, pady=8)
        self.apply_neon_glow(self.ent_appt_date, self.input_colors[0], "#FF007F")

        tk.Label(form_frame, text="Time Entry (HH:MM):", bg="#FFFFFF", fg="#1A1A2E").grid(row=3, column=0, sticky=tk.W, padx=15, pady=8)
        self.ent_appt_time = tk.Entry(form_frame, font=("Segoe UI", 10, "bold"), width=24, bg=self.input_colors[1], fg="#1A1A2E")
        self.ent_appt_time.grid(row=3, column=1, padx=15, pady=8)
        self.apply_neon_glow(self.ent_appt_time, self.input_colors[1], "#00FFFF")

        tk.Label(form_frame, text="Priority Level Index:", bg="#FFFFFF", fg="#1A1A2E").grid(row=4, column=0, sticky=tk.W, padx=15, pady=8)
        self.cb_priority = ttk.Combobox(form_frame, values=["Normal", "Emergency"], width=22, font=("Segoe UI", 10), state="readonly")
        self.cb_priority.set("Normal")
        self.cb_priority.grid(row=4, column=1, padx=15, pady=8)

        book_btn = tk.Button(form_frame, text="💘 Commit Booking Route", bg="#FF007F", fg="white", font=("Segoe UI", 10, "bold"), 
                  command=self.book_appointment, relief=tk.FLAT, bd=0, width=22, height=2, cursor="hand2")
        book_btn.grid(row=5, column=0, columnspan=2, pady=25)
        self.register_button_transition(book_btn, "#FF00FF", "#FF007F")

        list_frame = tk.LabelFrame(tab, text=" Live Operations Flow Grid Matrix ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ADVANCED FEATURE: Live Filter Search Box
        search_bar = tk.Frame(list_frame, bg="#FFFFFF")
        search_bar.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(search_bar, text="🔍 Search Matrix Logs:", bg="#FFFFFF", font=("Segoe UI Semibold", 9)).pack(side=tk.LEFT, padx=5)
        self.search_appt_ent = tk.Entry(search_bar, width=30, bg="#FFF5F7")
        self.search_appt_ent.pack(side=tk.LEFT, padx=5)
        self.search_appt_ent.bind("<KeyRelease>", lambda e: self.refresh_appointment_table(filter_text=self.search_appt_ent.get().strip()))

        cols = ("id", "p_name", "d_name", "date", "time", "priority", "status")
        self.appt_table = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols: self.appt_table.heading(c, text=c.upper())
        self.appt_table.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        bill_btn = tk.Button(list_frame, text="✨ Complete Session & Export Receipt", bg="#00FFFF", fg="#1A1A2E", font=("Segoe UI", 10, "bold"), 
                  command=self.complete_and_bill, relief=tk.FLAT, bd=0, height=2, padx=15, cursor="hand2")
        bill_btn.pack(anchor=tk.E, padx=15, pady=10)
        self.register_button_transition(bill_btn, "#FFD700", "#00FFFF")
        
        self.populate_dropdowns()
        self.refresh_appointment_table()
        self.after(200, lambda: [self.apply_background_emojis(tab, 25), self.apply_background_emojis(form_frame, 12)])

    def populate_dropdowns(self):
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT p.patient_id, u.name FROM patients p JOIN users u ON p.user_id = u.user_id")
        self.cb_patients['values'] = [f"{row[0]} | {row[1]}" for row in cursor.fetchall()]
        
        cursor.execute("SELECT pr.provider_id, u.name FROM providers pr JOIN users u ON pr.user_id = u.user_id")
        self.cb_providers['values'] = [f"{row[0]} | {row[1]}" for row in cursor.fetchall()]
        cursor.close()
        conn.close()

    def book_appointment(self):
        p_sel = self.cb_patients.get()
        d_sel = self.cb_providers.get()
        dt = self.ent_appt_date.get().strip()
        tm = self.ent_appt_time.get().strip()
        prio = self.cb_priority.get()

        if not (p_sel and d_sel and dt and tm):
            messagebox.showerror("Error", "Please populate all key parameters."); return

        pid = p_sel.split(" | ")[0]
        did = d_sel.split(" | ")[0]
        appt_id = f"APT-{int(datetime.now().timestamp()) % 100000}"

        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO appointments (appt_id, patient_id, provider_id, appt_date, appt_time, priority) VALUES (%s, %s, %s, %s, %s, %s)",
                           (appt_id, pid, did, dt, tm, prio))
            conn.commit()
            self.refresh_appointment_table()
            self.refresh_analytics()
            self.trigger_grand_celebration(f"Appointment Slot {appt_id} Successfully Formatted & Reserved inside Live MySQL Matrix Logs!")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Transaction Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def refresh_appointment_table(self, filter_text=""):
        for i in self.appt_table.get_children(): self.appt_table.delete(i)
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.appt_id, up.name, ud.name, a.appt_date, a.appt_time, a.priority, a.status 
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users up ON p.user_id = up.user_id
            JOIN providers d ON a.provider_id = d.provider_id
            JOIN users ud ON d.user_id = ud.user_id
            ORDER BY a.appt_date DESC
        """)
        
        # Applying Multi-Color alternating range tags for table output rows cells
        for idx, row in enumerate(cursor.fetchall()):
            if filter_text and (filter_text.lower() not in row[1].lower() and filter_text.lower() not in row[0].lower()):
                continue
            color_choice = self.matrix_row_colors[idx % len(self.matrix_row_colors)]
            tag_name = f"row_rainbow_{idx}"
            self.appt_table.tag_configure(tag_name, background=color_choice)
            
            # Decorating individual text parameters inside cells with flower emojis
            modified_row = (f"🌸 {row[0]}", row[1], row[2], row[3], row[4], f"💖 {row[5]}", row[6])
            self.appt_table.insert("", tk.END, values=modified_row, tags=(tag_name,))
            
        cursor.close()
        conn.close()

    def complete_and_bill(self):
        selected = self.appt_table.selection()
        if not selected:
            messagebox.showwarning("Notice", "Select an element row from matrix system block."); return
        
        raw_val = self.appt_table.item(selected, 'values')[0]
        appt_id = raw_val.replace("🌸 ", "").strip()
        
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = 'Completed' WHERE appt_id = %s", (appt_id,))
        conn.commit()
        
        query = """
            SELECT a.appt_id, up.name, p.patient_id, p.gender, p.medical_history, ud.name, d.provider_id, d.specialty, d.fee, a.appt_date, a.appt_time
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users up ON p.user_id = up.user_id
            JOIN providers d ON a.provider_id = d.provider_id
            JOIN users ud ON d.user_id = ud.user_id
            WHERE a.appt_id = %s
        """
        cursor.execute(query, (appt_id,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        self.refresh_appointment_table()
        self.refresh_analytics()
        if data: 
            self.popup_token_card(data) # ADVANCED FEATURE CALL
            self.compile_invoice_pdf(data)

    # --- ADVANCED FEATURE: LIVE ROOM TOKEN PREVIEW PROTOCOL ---
    def popup_token_card(self, info):
        token_win = tk.Toplevel(self)
        token_win.title("AURA - Room Token Slip Generator")
        token_win.geometry("380x300")
        token_win.configure(bg="#1A1A2E")
        token_win.resizable(False, False)
        
        tk.Label(token_win, text="✨ AURA HEALTHCARE MEDICAL SUITE ✨", font=("Segoe UI", 10, "bold"), fg="#FF007F", bg="#1A1A2E").pack(pady=10)
        
        f = tk.Frame(token_win, bg="#FFFFFF", highlightbackground="#00FFFF", highlightthickness=2)
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(f, text=f"TOKEN ID: TKN-{random.randint(100,999)}", font=("Courier New", 16, "bold"), fg="#1A1A2E", bg="#FFFFFF").pack(pady=10)
        tk.Label(f, text=f"PATIENT: {info[1]}", font=("Segoe UI Semibold", 10), bg="#FFFFFF", fg="#555555").pack()
        tk.Label(f, text=f"ROUTED EXPERT: {info[5]}", font=("Segoe UI Semibold", 11, "bold"), bg="#FFFFFF", fg="#FF007F").pack(pady=5)
        tk.Label(f, text=f"DEPT: {info[7]}", font=("Segoe UI", 9, "italic"), bg="#FFFFFF", fg="#7F8C8D").pack()
        tk.Label(f, text=f"TIMING SLOT: {info[10]}", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2E7D32").pack(pady=5)

    def compile_invoice_pdf(self, info):
        default_name = f"bills/Bill_{info[2]}_{info[0]}.pdf"
        filename = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")], title="Save PDF Receipt Ledger")
        if not filename: return
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            ts = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor("#FF007F"))
            ms = ParagraphStyle('Meta', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
            
            story = [
                Paragraph("CITY CARE CLINICAL SERVICE INVOICE", ts),
                Spacer(1, 15),
                Paragraph(f"<b>Transaction ID:</b> TXN-{info[0]}<br/><b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", ms),
                Spacer(1, 15),
                Paragraph(f"<b>Patient Name:</b> {info[1]} (ID: {info[2]})<br/><b>History:</b> {info[4]}", ms),
                Spacer(1, 10),
                Paragraph(f"<b>Doctor Name:</b> {info[5]} ({info[7]})", ms),
                Spacer(1, 20)
            ]
            
            table_rows = [
                [Paragraph("<b>Service Description</b>", ms), Paragraph("<b>Consultation Fee</b>", ms)],
                [Paragraph(f"Clinical Diagnostic Consultation - Session {info[0]}", ms), Paragraph(f"PKR {float(info[8]):,.2f}", ms)]
            ]
            t = Table(table_rows, colWidths=[350, 150])
            t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFEBEE")), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('PADDING', (0,0), (-1,-1), 8)]))
            story.append(t)
            
            doc.build(story)
            self.trigger_grand_celebration(f"Invoice PDF Ledger compiled and deployed securely to your host directory at:\n{filename}")
        except Exception as e:
            messagebox.showerror("PDF Engine Failure", str(e))

    # --------------------------------------
    # TAB 3: PATIENT RECORDS PORTAL
    # --------------------------------------
    def build_patient_tab(self):
        tab = tk.Frame(self.notebook, bg="#FCE4EC")
        self.notebook.add(tab, text="   Patients Management Records   ")

        form_frame = tk.LabelFrame(tab, text=" Registration Node Configuration ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        fields = ["User ID Name:", "Full Identity Name:", "Email Domain:", "Contact Number:", "DOB (YYYY-MM-DD):", "Gender Configuration:", "History Notes:"]
        self.pat_entries = {}
        for i, f in enumerate(fields):
            tk.Label(form_frame, text=f, bg="#FFFFFF", fg="#1A1A2E").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            allocated_color = self.input_colors[i % len(self.input_colors)]
            glow_color = self.neon_glows[i % len(self.neon_glows)]
            
            e = tk.Entry(form_frame, font=("Segoe UI Semibold", 10, "bold"), width=18, bg=allocated_color, fg="#1A1A2E")
            e.grid(row=i, column=1, padx=10, pady=5)
            self.apply_neon_glow(e, allocated_color, glow_color)
            self.pat_entries[f] = e

        save_btn = tk.Button(form_frame, text="🌻 Save Active Profile", bg="#39FF14", fg="#1A1A2E", font=("Segoe UI", 10, "bold"), 
                  command=self.add_patient, relief=tk.FLAT, bd=0, width=18, height=2, cursor="hand2")
        save_btn.grid(row=7, column=0, columnspan=2, pady=15)
        self.register_button_transition(save_btn, "#FF00FF", "#39FF14")

        list_frame = tk.LabelFrame(tab, text=" Global Database Records Logs ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        controls_bar = tk.Frame(list_frame, bg="#FFFFFF")
        controls_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # ADVANCED FEATURE: Live Search filter for Patients
        tk.Label(controls_bar, text="🔍 Search Active Patient Name:", bg="#FFFFFF").pack(side=tk.LEFT, padx=5)
        self.search_pat_ent = tk.Entry(controls_bar, width=25, bg="#E8F5E9")
        self.search_pat_ent.pack(side=tk.LEFT, padx=5)
        self.search_pat_ent.bind("<KeyRelease>", lambda e: self.refresh_patient_table(filter_text=self.search_pat_ent.get().strip()))

        export_btn = tk.Button(controls_bar, text="📊 Export Pattern Sheet to CSV", bg="#FF00FF", fg="white", font=("Segoe UI", 9, "bold"),
                  command=self.export_patients, relief=tk.FLAT, bd=0, padx=10, pady=5, cursor="hand2")
        export_btn.pack(side=tk.RIGHT)
        self.register_button_transition(export_btn, "#00FFFF", "#FF00FF")

        cols = ("id", "name", "email", "phone", "dob", "gender", "history")
        self.pat_table = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols: self.pat_table.heading(c, text=c.upper())
        self.pat_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.refresh_patient_table()
        self.after(200, lambda: [self.apply_background_emojis(tab, 25), self.apply_background_emojis(list_frame, 15)])

    def export_patients(self):
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT p.patient_id, u.name, u.email, u.phone, p.dob, p.gender, p.medical_history FROM patients p JOIN users u ON p.user_id = u.user_id")
        rows = cursor.fetchall()
        
        df = pd.DataFrame(rows, columns=["Patient ID", "Full Name", "Email Address", "Phone Number", "DOB", "Gender", "Medical History"])
        target_file = "patients_export.csv"
        df.to_csv(target_file, index=False)
        self.trigger_grand_celebration(f"Data Sheet matrix successfully compiled and parsed safely to path root location as:\n[{target_file}]")
        cursor.close()
        conn.close()

    def add_patient(self):
        v = {k: ent.get().strip() for k, ent in self.pat_entries.items()}
        if not (v["User ID Name:"] and v["Full Identity Name:"]):
            messagebox.showerror("Validation Error", "Key attributes cannot be left empty."); return

        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            # 1. User table mein data insert karein
            cursor.execute("INSERT INTO users (user_id, password, name, email, phone) VALUES (%s, 'p123', %s, %s, %s)",
                           (v["User ID Name:"], v["Full Identity Name:"], v["Email Domain:"], v["Contact Number:"]))
            
            # 2. Patient ID generate karein
            p_id = f"PAT-{int(datetime.now().timestamp()) % 100000}"
            
            # 3. Patient table mein data insert karein
            cursor.execute("INSERT INTO patients (patient_id, user_id, dob, gender, medical_history) VALUES (%s, %s, %s, %s, %s)",
                           (p_id, v["User ID Name:"], v["DOB (YYYY-MM-DD):"], v["Gender Configuration:"], v["History Notes:"]))
            
            # 4. Changes save karein
            conn.commit()
            
            # 5. UI Refresh karein
            self.populate_dropdowns()
            self.refresh_patient_table()
            self.refresh_analytics()
            
            # 6. Success message show karein (Bracket use karein, '=' nahi)
            msg = f"New Patient Root Protocol assigned for {v['Full Identity Name:']} mapped on ID: {p_id}"
            self.trigger_grand_celebration(msg)

        except Exception as e:
            # Agar koi error aaye to yahan catch karein
            print(f"Error a gaya hai: {e}")



import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from time import strftime
import random
import mysql.connector
import pandas as pd
from PIL import Image, ImageTk  # REQUIRES PILLOW: pip install Pillow
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",        
            password="faiza2426,./",        
            database="hospital_management"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"MySQL Connection Failed: {err}")
        return None

def initialize_database():
    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(50) PRIMARY KEY,
        password VARCHAR(100) NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(50)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50),
        dob DATE,
        gender VARCHAR(20),
        medical_history TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        provider_id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50),
        specialty VARCHAR(100),
        fee DECIMAL(10,2),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appt_id VARCHAR(50) PRIMARY KEY,
        patient_id VARCHAR(50),
        provider_id VARCHAR(50),
        appt_date DATE,
        appt_time TIME,
        status VARCHAR(50) DEFAULT 'Scheduled',
        priority VARCHAR(20) DEFAULT 'Normal',
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        staff_id VARCHAR(50) PRIMARY KEY,
        user_id VARCHAR(50),
        role VARCHAR(100),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        shift_id VARCHAR(50) PRIMARY KEY,
        staff_id VARCHAR(50),
        start_time TIME,
        end_time TIME,
        FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE
    )""")
        
    conn.commit()
    cursor.close()
    conn.close()

# ==========================================
# 2. MAIN APPLICATION CORE ENGINE
# ==========================================
class ModernMedicalSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AURA - Redesigned Dashboard & New High-Quality Celebration Engine")
        self.geometry("1350x850")
        self.state('zoomed') 
        
        self.themes = {
            "Aura Rose ✨": {"bg": "#FFF5F7", "panel": "#FFFFFF", "accent": "#FF007F", "text": "#1A1A2E", "card1": "#FFEBEE", "card2": "#E0F2F1", "card3": "#E3F2FD"},
            "Neon Cyberpunk 🌌": {"bg": "#0D1117", "panel": "#161B22", "accent": "#00FFFF", "text": "#C9D1D9", "card1": "#21262D", "card2": "#30363D", "card3": "#1F2937"},
            "Classic Dark Mode 🌙": {"bg": "#1F232A", "panel": "#2A303C", "accent": "#A6ADBB", "text": "#F8F9FA", "card1": "#384152", "card2": "#2D3748", "card3": "#1A202C"},
            "Mint Fresh 🌿": {"bg": "#E8F5E9", "panel": "#FFFFFF", "accent": "#2E7D32", "text": "#1B5E20", "card1": "#C8E6C9", "card2": "#E8F5E9", "card3": "#D1E7DD"}
        }
        
        self.current_theme = "Aura Rose ✨"
        self.bg_base_clean = self.themes[self.current_theme]["bg"]
        self.text_dark = self.themes[self.current_theme]["text"]
        
        self.neon_glows = ["#FF007F", "#00FFFF", "#39FF14", "#FF00FF", "#FFD700", "#FF4500"]
        self.flower_pool = ["🌸", "💖", "✨", "🌻", "🌹", "🌷", "🍃", "🦋", "💘", "🎉", "🌈", "⭐", "💎", "💥", "🎈"]
        self.input_colors = ["#FFC0CB", "#E0FFFF", "#EAFAF1", "#FEF9E7", "#F3E5F5", "#EBF5FB", "#FADBD8"]
        self.matrix_row_colors = ["#FFEBEE", "#E0F2F1", "#E8F5E9", "#FFFDE7", "#F3E5F5", "#E3F2FD"]

        self.configure(bg=self.bg_base_clean)
        
        if not os.path.exists("bills"):
            os.makedirs("bills")
            
        initialize_database()
        self.setup_styles()
        self.create_layout()
        self.time_now() 
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TNotebook", background=self.bg_base_clean, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#eaeaea", foreground="#1A1A2E", 
                             padding=[18, 8], font=("Segoe UI Semibold", 10), borderwidth=0)
        self.style.map("TNotebook.Tab", background=[("selected", "#FF007F")], foreground=[("selected", "#FFFFFF")])
        
        self.style.configure("Treeview", background="#FFFFFF", foreground="#1A1A2E", 
                             fieldbackground="#FFFFFF", rowheight=36, font=("Segoe UI Semibold", 9), borderwidth=0)
        self.style.configure("Treeview.Heading", background="#1A1A2E", foreground="#FFFFFF", 
                             font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
        self.style.map("Treeview", background=[("selected", "#FFC0CB")], foreground=[("selected", "#1A1A2E")])

    def change_theme_engine(self, selected_theme):
        self.current_theme = selected_theme
        t = self.themes[selected_theme]
        self.bg_base_clean = t["bg"]
        self.text_dark = t["text"]
        
        self.configure(bg=t["bg"])
        self.header_frame.config(bg=t["panel"], highlightbackground=t["accent"])
        self.header_title.config(fg=t["accent"], bg=t["panel"])
        self.clock_label.config(fg=t["text"], bg=t["panel"])
        self.style.configure("TNotebook", background=t["bg"])
        self.style.configure("Treeview.Heading", background=t["accent"])
        self.style.map("TNotebook.Tab", background=[("selected", t["accent"])])
        
        self.refresh_analytics()
        messagebox.showinfo("Theme Synced", f"System successfully morphed into {selected_theme} mode!")

    def apply_background_emojis(self, widget, density=15):
        widget.update_idletasks()
        w = widget.winfo_width() if widget.winfo_width() > 100 else 500
        h = widget.winfo_height() if widget.winfo_height() > 100 else 400
        
        for _ in range(density):
            rx = random.randint(15, w - 45)
            ry = random.randint(15, h - 45)
            emoji = random.choice(self.flower_pool)
            color = random.choice(["#FFB6C1", "#FF69B4", "#FF1493", "#9370DB", "#40E0D0"])
            
            lbl = tk.Label(widget, text=emoji, fg=color, bg=widget.cget("bg"), font=("Segoe UI", random.randint(12, 22)))
            lbl.place(x=rx, y=ry)
            lbl.lower()

    def apply_neon_glow(self, widget, normal_bg, active_glow):
        widget.config(highlightbackground="#BDC3C7", highlightthickness=1, bd=0)
        widget.bind("<FocusIn>", lambda e: widget.config(bg="#FFFFFF", highlightthickness=2, highlightcolor=active_glow))
        widget.bind("<FocusOut>", lambda e: widget.config(bg=normal_bg, highlightthickness=1, highlightcolor="#BDC3C7"))

    def register_button_transition(self, btn, click_bg, reset_bg):
        def on_click(event):
            btn.config(bg=click_bg, fg="#FFFFFF", relief=tk.SUNKEN)
            self.update_idletasks()
        def on_release(event):
            btn.config(bg=reset_bg, fg="white" if reset_bg != "#00FFFF" else "#1A1A2E", relief=tk.FLAT)
        btn.bind("<Button-1>", on_click)
        btn.bind("<ButtonRelease-1>", on_release)

    # --------------------------------------
    # HIGH-QUALITY CELEBRATION ENGINE v2
    # --------------------------------------
    def trigger_grand_celebration(self, success_msg="Operation Successful!"):
        celebration_win = tk.Toplevel(self)
        celebration_win.overrideredirect(True)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        celebration_win.geometry(f"{sw}x{sh}+0+0")
        celebration_win.configure(bg="#0B0C10")  # Cinematic dark backdrop
        celebration_win.attributes("-alpha", 0.0) # Start transparent for smooth fade-in
        celebration_win.lift()

        # Smooth Fade-In effect
        def fade_in(alpha=0.0):
            if alpha < 0.95:
                alpha += 0.08
                celebration_win.attributes("-alpha", alpha)
                self.after(20, lambda: fade_in(alpha))
        fade_in()

        # Premium Glassmorphism Centered Card Frame
        msg_frame = tk.Frame(celebration_win, bg="#1F2833", highlightbackground="#00FFFF", highlightthickness=2, bd=0)
        msg_frame.place(relx=0.5, rely=0.45, anchor=tk.CENTER, width=600, height=260)
        
        title_lbl = tk.Label(msg_frame, text="✨ TRANSACTION MARGIN SECURED ✨", font=("Segoe UI", 14, "bold"), fg="#00FFFF", bg="#1F2833")
        title_lbl.pack(pady=(25, 10))
        
        # Color Shifting Alert Text Protocol
        def cycle_text_glow():
            if celebration_win.winfo_exists():
                title_lbl.config(fg=random.choice(self.neon_glows))
                self.after(350, cycle_text_glow)
        cycle_text_glow()

        tk.Label(msg_frame, text=success_msg, font=("Segoe UI Semibold", 11), fg="#C9D1D9", bg="#1F2833", wraplength=520, justify="center").pack(pady=10)
        
        # Smooth Fade Out Dismissal Button
        def smooth_exit():
            def fade_out(alpha=celebration_win.attributes("-alpha")):
                if alpha > 0.05:
                    alpha -= 0.08
                    celebration_win.attributes("-alpha", alpha)
                    self.after(15, fade_out)
                else:
                    celebration_win.destroy()
            fade_out()

        close_btn = tk.Button(msg_frame, text="⚡ Dismiss Operational Layer", bg="#FF007F", fg="white", font=("Segoe UI", 10, "bold"),
                             command=smooth_exit, relief=tk.FLAT, bd=0, cursor="hand2", padx=25, pady=8)
        close_btn.pack(pady=20)
        self.register_button_transition(close_btn, "#FF00FF", "#FF007F")

        # Deploy Advanced Floating Particle Rain Stream
        for _ in range(120):
            sx = random.randint(0, sw)
            sy = random.randint(-400, 0)
            lbl = tk.Label(celebration_win, text=random.choice(self.flower_pool), font=("Segoe UI", random.randint(18, 45)), fg=random.choice(self.neon_glows), bg="#0B0C10")
            lbl.place(x=sx, y=sy)
            # Added unique horizontal velocity bounds for high dynamic fluid animation looks
            self.animate_celebration_drop(lbl, random.randint(5, 14), random.randint(-4, 4), sh, celebration_win)

    def animate_celebration_drop(self, label, speed_y, speed_x, max_h, container):
        if not container.winfo_exists(): return
        ny = label.winfo_y() + speed_y
        nx = label.winfo_x() + speed_x
        
        # Dynamic boundaries check to cycle falling items smoothly
        if ny > max_h:
            ny = random.randint(-150, -20)
            nx = random.randint(0, container.winfo_width())
        label.place(x=nx, y=ny)
        self.after(20, lambda: self.animate_celebration_drop(label, speed_y, speed_x, max_h, container))

    def create_layout(self):
        self.header_frame = tk.Frame(self, bg="#FFFFFF", height=85, bd=0, highlightbackground="#FF007F", highlightthickness=1)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_frame.pack_propagate(False)
        
        self.header_title = tk.Label(self.header_frame, text="🌸 AURA ADVANCED MEDICAL MANAGEMENT NODE", 
                 fg="#FF007F", bg="#FFFFFF", font=("Segoe UI", 15, "bold"))
        self.header_title.pack(side=tk.LEFT, padx=30, pady=25)
        
        theme_bar = tk.Frame(self.header_frame, bg="#FFFFFF")
        theme_bar.pack(side=tk.RIGHT, padx=15, pady=25)
        tk.Label(theme_bar, text="Theme:", font=("Segoe UI Semibold", 9), bg="#FFFFFF", fg="#555555").pack(side=tk.LEFT, padx=5)
        self.theme_menu = ttk.Combobox(theme_bar, values=list(self.themes.keys()), state="readonly", width=16)
        self.theme_menu.set(self.current_theme)
        self.theme_menu.bind("<<ComboboxSelected>>", lambda e: self.change_theme_engine(self.theme_menu.get()))
        self.theme_menu.pack(side=tk.LEFT)
        
        self.clock_label = tk.Label(self.header_frame, text="", font=("Segoe UI", 11, "bold"), fg="#1A1A2E", bg="#FFFFFF")
        self.clock_label.pack(side=tk.RIGHT, padx=20, pady=25)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.build_analytics_tab()
        self.build_appointment_tab()
        self.build_patient_tab()
        self.build_provider_tab()
        self.build_staff_tab()

    def time_now(self):
        current = strftime('%I:%M:%S %p | %A, %B %d, %Y')
        self.clock_label.configure(text=current)
        self.clock_label.after(1000, self.time_now)

    # --------------------------------------
    # TAB 1: UNIQUE DESIGN DASHBOARD OVERVIEW
    # --------------------------------------
    def build_analytics_tab(self):
        self.tab_analytics = tk.Frame(self.notebook, bg="#FFF5F5")
        self.notebook.add(self.tab_analytics, text="   Dashboard Overview   ")
        
        top_monitor_bar = tk.Frame(self.tab_analytics, bg="#FFFFFF", height=50, highlightbackground="#EBF5FB", highlightthickness=1)
        top_monitor_bar.pack(fill=tk.X, padx=25, pady=(20, 5))
        
        tk.Label(top_monitor_bar, text="⚙️ SYSTEM ARCHITECTURE STATUS:", font=("Segoe UI", 9, "bold"), fg="#7F8C8D", bg="#FFFFFF").pack(side=tk.LEFT, padx=15, pady=15)
        self.lbl_db_status = tk.Label(top_monitor_bar, text="● ONLINE STATUS SECURE", font=("Segoe UI", 10, "bold"), fg="#39FF14", bg="#FFFFFF")
        self.lbl_db_status.pack(side=tk.LEFT, padx=5)

        middle_split_frame = tk.Frame(self.tab_analytics, bg="#FFF5F5")
        middle_split_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)
        
        left_cards_container = tk.LabelFrame(middle_split_frame, text=" Live Operations Flow Counters ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        left_cards_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.c1 = tk.Frame(left_cards_container, bg="#FFEBEE", height=90, highlightbackground="#FF007F", highlightthickness=1)
        self.c1.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(self.c1, text="TOTAL ACCOUNT REVENUE", bg="#FFEBEE", fg="#C2185B", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(8, 2))
        self.lbl_revenue = tk.Label(self.c1, text="PKR 0.00", bg="#FFEBEE", font=("Segoe UI", 16, "bold"), fg="#1A1A2E")
        self.lbl_revenue.pack(anchor="w", padx=15, pady=(0, 8))
        
        self.c2 = tk.Frame(left_cards_container, bg="#E0F2F1", height=90, highlightbackground="#00FFFF", highlightthickness=1)
        self.c2.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(self.c2, text="COMPLETED CLINICAL SESSIONS", bg="#E0F2F1", fg="#004D40", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(8, 2))
        self.lbl_count = tk.Label(self.c2, text="0 Sessions", bg="#E0F2F1", font=("Segoe UI", 16, "bold"), fg="#1A1A2E")
        self.lbl_count.pack(anchor="w", padx=15, pady=(0, 8))

        self.c3 = tk.Frame(left_cards_container, bg="#E3F2FD", height=90, highlightbackground="#39FF14", highlightthickness=1)
        self.c3.pack(fill=tk.X, padx=20, pady=8)
        tk.Label(self.c3, text="SYNCHRONIZED CLIENT PROFILES", bg="#E3F2FD", fg="#0D47A1", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(8, 2))
        self.lbl_patients_total = tk.Label(self.c3, text="0 Files", bg="#E3F2FD", font=("Segoe UI", 16, "bold"), fg="#1A1A2E")
        self.lbl_patients_total.pack(anchor="w", padx=15, pady=(0, 8))

        # --- ADVANCED FEATURE: METRICS VISUALIZER PROGRESS BARS ---
        self.visualizer_frame = tk.LabelFrame(middle_split_frame, text=" 📊 Live Resource Load Visualizer ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        self.visualizer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(self.visualizer_frame, text="Patient Admission Capacity Load:", font=("Segoe UI", 9), bg="#FFFFFF").pack(anchor="w", padx=15, pady=(15,2))
        self.progress_pats = ttk.Progressbar(self.visualizer_frame, orient="horizontal", length=220, mode="determinate")
        self.progress_pats.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(self.visualizer_frame, text="Consultation Targets Completed:", font=("Segoe UI", 9), bg="#FFFFFF").pack(anchor="w", padx=15, pady=(15,2))
        self.progress_rev = ttk.Progressbar(self.visualizer_frame, orient="horizontal", length=220, mode="determinate")
        self.progress_rev.pack(fill=tk.X, padx=15, pady=5)

        action_center_frame = tk.LabelFrame(self.tab_analytics, text=" ⚡ Quick Action Shortcut Center ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        action_center_frame.pack(fill=tk.X, padx=25, pady=(5, 25))
        
        sync_btn = tk.Button(action_center_frame, text="🔮 Synchronize System Core Ledger", bg="#FF007F", fg="white", font=("Segoe UI", 9, "bold"), 
                  command=lambda: [self.refresh_analytics(), self.trigger_grand_celebration("System Core Architecture Resynced with Live MySQL Schema Engine!")], relief=tk.FLAT, bd=0, cursor="hand2", width=30, height=2)
        sync_btn.pack(side=tk.LEFT, padx=20, pady=15)
        self.register_button_transition(sync_btn, "#FF00FF", "#FF007F")
        
        backup_btn = tk.Button(action_center_frame, text="💾 Deploy Cloud Database Backup", bg="#39FF14", fg="#1A1A2E", font=("Segoe UI", 9, "bold"), 
                  command=lambda: self.trigger_grand_celebration("Transaction Ledger safely deployed to remote cloud mirroring infrastructure."), relief=tk.FLAT, bd=0, cursor="hand2", width=30, height=2)
        backup_btn.pack(side=tk.LEFT, padx=10, pady=15)
        self.register_button_transition(backup_btn, "#00FFFF", "#39FF14")
                  
        self.refresh_analytics()
        self.after(200, lambda: [self.apply_background_emojis(self.tab_analytics, 20), self.apply_background_emojis(left_cards_container, 8), self.apply_background_emojis(self.visualizer_frame, 8)])

    def refresh_analytics(self):
        conn = get_db_connection()
        if not conn: 
            self.lbl_db_status.config(text="● OFFLINE", fg="#FF4500")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(p.fee) FROM appointments a JOIN providers p ON a.provider_id = p.provider_id WHERE a.status = 'Completed'")
        res = cursor.fetchone()
        count = res[0] if res[0] else 0
        rev = res[1] if res[1] else 0.0
        
        cursor.execute("SELECT COUNT(*) FROM patients")
        tot_pats = cursor.fetchone()[0]
        
        self.lbl_revenue.config(text=f"PKR {rev:,.2f}")
        self.lbl_count.config(text=f"{count} Actions Completed")
        self.lbl_patients_total.config(text=f"{tot_pats} Active Profiles")
        
        # Dynamic Progress Tracking updates
        self.progress_pats['value'] = min((tot_pats / 50) * 100, 100) # Target baseline 50 profiles
        self.progress_rev['value'] = min((count / 30) * 100, 100) # Target baseline 30 operations
        
        cursor.close()
        conn.close()

    # --------------------------------------
    # TAB 2: APPOINTMENTS DESK
    # --------------------------------------
    def build_appointment_tab(self):
        tab = tk.Frame(self.notebook, bg="#E0FFFF")
        self.notebook.add(tab, text="   Appointments Core Desk   ")

        form_frame = tk.LabelFrame(tab, text=" Scheduling Form Panel ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        tk.Label(form_frame, text="Select Target Patient:", bg="#FFFFFF", fg="#1A1A2E").grid(row=0, column=0, sticky=tk.W, padx=15, pady=8)
        self.cb_patients = ttk.Combobox(form_frame, width=22, font=("Segoe UI", 10), state="readonly")
        self.cb_patients.grid(row=0, column=1, padx=15, pady=8)

        tk.Label(form_frame, text="Assign Doctor Expert:", bg="#FFFFFF", fg="#1A1A2E").grid(row=1, column=0, sticky=tk.W, padx=15, pady=8)
        self.cb_providers = ttk.Combobox(form_frame, width=22, font=("Segoe UI", 10), state="readonly")
        self.cb_providers.grid(row=1, column=1, padx=15, pady=8)

        tk.Label(form_frame, text="Date Entry (YYYY-MM-DD):", bg="#FFFFFF", fg="#1A1A2E").grid(row=2, column=0, sticky=tk.W, padx=15, pady=8)
        self.ent_appt_date = tk.Entry(form_frame, font=("Segoe UI", 10, "bold"), width=24, bg=self.input_colors[0], fg="#1A1A2E")
        self.ent_appt_date.grid(row=2, column=1, padx=15, pady=8)
        self.apply_neon_glow(self.ent_appt_date, self.input_colors[0], "#FF007F")

        tk.Label(form_frame, text="Time Entry (HH:MM):", bg="#FFFFFF", fg="#1A1A2E").grid(row=3, column=0, sticky=tk.W, padx=15, pady=8)
        self.ent_appt_time = tk.Entry(form_frame, font=("Segoe UI", 10, "bold"), width=24, bg=self.input_colors[1], fg="#1A1A2E")
        self.ent_appt_time.grid(row=3, column=1, padx=15, pady=8)
        self.apply_neon_glow(self.ent_appt_time, self.input_colors[1], "#00FFFF")

        tk.Label(form_frame, text="Priority Level Index:", bg="#FFFFFF", fg="#1A1A2E").grid(row=4, column=0, sticky=tk.W, padx=15, pady=8)
        self.cb_priority = ttk.Combobox(form_frame, values=["Normal", "Emergency"], width=22, font=("Segoe UI", 10), state="readonly")
        self.cb_priority.set("Normal")
        self.cb_priority.grid(row=4, column=1, padx=15, pady=8)

        book_btn = tk.Button(form_frame, text="💘 Commit Booking Route", bg="#FF007F", fg="white", font=("Segoe UI", 10, "bold"), 
                  command=self.book_appointment, relief=tk.FLAT, bd=0, width=22, height=2, cursor="hand2")
        book_btn.grid(row=5, column=0, columnspan=2, pady=25)
        self.register_button_transition(book_btn, "#FF00FF", "#FF007F")

        list_frame = tk.LabelFrame(tab, text=" Live Operations Flow Grid Matrix ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ADVANCED FEATURE: Live Filter Search Box
        search_bar = tk.Frame(list_frame, bg="#FFFFFF")
        search_bar.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(search_bar, text="🔍 Search Matrix Logs:", bg="#FFFFFF", font=("Segoe UI Semibold", 9)).pack(side=tk.LEFT, padx=5)
        self.search_appt_ent = tk.Entry(search_bar, width=30, bg="#FFF5F7")
        self.search_appt_ent.pack(side=tk.LEFT, padx=5)
        self.search_appt_ent.bind("<KeyRelease>", lambda e: self.refresh_appointment_table(filter_text=self.search_appt_ent.get().strip()))

        cols = ("id", "p_name", "d_name", "date", "time", "priority", "status")
        self.appt_table = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols: self.appt_table.heading(c, text=c.upper())
        self.appt_table.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        bill_btn = tk.Button(list_frame, text="✨ Complete Session & Export Receipt", bg="#00FFFF", fg="#1A1A2E", font=("Segoe UI", 10, "bold"), 
                  command=self.complete_and_bill, relief=tk.FLAT, bd=0, height=2, padx=15, cursor="hand2")
        bill_btn.pack(anchor=tk.E, padx=15, pady=10)
        self.register_button_transition(bill_btn, "#FFD700", "#00FFFF")
        
        self.populate_dropdowns()
        self.refresh_appointment_table()
        self.after(200, lambda: [self.apply_background_emojis(tab, 25), self.apply_background_emojis(form_frame, 12)])

    def populate_dropdowns(self):
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT p.patient_id, u.name FROM patients p JOIN users u ON p.user_id = u.user_id")
        self.cb_patients['values'] = [f"{row[0]} | {row[1]}" for row in cursor.fetchall()]
        
        cursor.execute("SELECT pr.provider_id, u.name FROM providers pr JOIN users u ON pr.user_id = u.user_id")
        self.cb_providers['values'] = [f"{row[0]} | {row[1]}" for row in cursor.fetchall()]
        cursor.close()
        conn.close()

    def book_appointment(self):
        p_sel = self.cb_patients.get()
        d_sel = self.cb_providers.get()
        dt = self.ent_appt_date.get().strip()
        tm = self.ent_appt_time.get().strip()
        prio = self.cb_priority.get()

        if not (p_sel and d_sel and dt and tm):
            messagebox.showerror("Error", "Please populate all key parameters."); return

        pid = p_sel.split(" | ")[0]
        did = d_sel.split(" | ")[0]
        appt_id = f"APT-{int(datetime.now().timestamp()) % 100000}"

        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO appointments (appt_id, patient_id, provider_id, appt_date, appt_time, priority) VALUES (%s, %s, %s, %s, %s, %s)",
                           (appt_id, pid, did, dt, tm, prio))
            conn.commit()
            self.refresh_appointment_table()
            self.refresh_analytics()
            self.trigger_grand_celebration(f"Appointment Slot {appt_id} Successfully Formatted & Reserved inside Live MySQL Matrix Logs!")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Transaction Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def refresh_appointment_table(self, filter_text=""):
        for i in self.appt_table.get_children(): self.appt_table.delete(i)
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.appt_id, up.name, ud.name, a.appt_date, a.appt_time, a.priority, a.status 
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users up ON p.user_id = up.user_id
            JOIN providers d ON a.provider_id = d.provider_id
            JOIN users ud ON d.user_id = ud.user_id
            ORDER BY a.appt_date DESC
        """)
        
        # Applying Multi-Color alternating range tags for table output rows cells
        for idx, row in enumerate(cursor.fetchall()):
            if filter_text and (filter_text.lower() not in row[1].lower() and filter_text.lower() not in row[0].lower()):
                continue
            color_choice = self.matrix_row_colors[idx % len(self.matrix_row_colors)]
            tag_name = f"row_rainbow_{idx}"
            self.appt_table.tag_configure(tag_name, background=color_choice)
            
            # Decorating individual text parameters inside cells with flower emojis
            modified_row = (f"🌸 {row[0]}", row[1], row[2], row[3], row[4], f"💖 {row[5]}", row[6])
            self.appt_table.insert("", tk.END, values=modified_row, tags=(tag_name,))
            
        cursor.close()
        conn.close()

    def complete_and_bill(self):
        selected = self.appt_table.selection()
        if not selected:
            messagebox.showwarning("Notice", "Select an element row from matrix system block."); return
        
        raw_val = self.appt_table.item(selected, 'values')[0]
        appt_id = raw_val.replace("🌸 ", "").strip()
        
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = 'Completed' WHERE appt_id = %s", (appt_id,))
        conn.commit()
        
        query = """
            SELECT a.appt_id, up.name, p.patient_id, p.gender, p.medical_history, ud.name, d.provider_id, d.specialty, d.fee, a.appt_date, a.appt_time
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users up ON p.user_id = up.user_id
            JOIN providers d ON a.provider_id = d.provider_id
            JOIN users ud ON d.user_id = ud.user_id
            WHERE a.appt_id = %s
        """
        cursor.execute(query, (appt_id,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        self.refresh_appointment_table()
        self.refresh_analytics()
        if data: 
            self.popup_token_card(data) # ADVANCED FEATURE CALL
            self.compile_invoice_pdf(data)

    # --- ADVANCED FEATURE: LIVE ROOM TOKEN PREVIEW PROTOCOL ---
    def popup_token_card(self, info):
        token_win = tk.Toplevel(self)
        token_win.title("AURA - Room Token Slip Generator")
        token_win.geometry("380x300")
        token_win.configure(bg="#1A1A2E")
        token_win.resizable(False, False)
        
        tk.Label(token_win, text="✨ AURA HEALTHCARE MEDICAL SUITE ✨", font=("Segoe UI", 10, "bold"), fg="#FF007F", bg="#1A1A2E").pack(pady=10)
        
        f = tk.Frame(token_win, bg="#FFFFFF", highlightbackground="#00FFFF", highlightthickness=2)
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(f, text=f"TOKEN ID: TKN-{random.randint(100,999)}", font=("Courier New", 16, "bold"), fg="#1A1A2E", bg="#FFFFFF").pack(pady=10)
        tk.Label(f, text=f"PATIENT: {info[1]}", font=("Segoe UI Semibold", 10), bg="#FFFFFF", fg="#555555").pack()
        tk.Label(f, text=f"ROUTED EXPERT: {info[5]}", font=("Segoe UI Semibold", 11, "bold"), bg="#FFFFFF", fg="#FF007F").pack(pady=5)
        tk.Label(f, text=f"DEPT: {info[7]}", font=("Segoe UI", 9, "italic"), bg="#FFFFFF", fg="#7F8C8D").pack()
        tk.Label(f, text=f"TIMING SLOT: {info[10]}", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#2E7D32").pack(pady=5)

    def compile_invoice_pdf(self, info):
        default_name = f"bills/Bill_{info[2]}_{info[0]}.pdf"
        filename = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")], title="Save PDF Receipt Ledger")
        if not filename: return
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            ts = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor("#FF007F"))
            ms = ParagraphStyle('Meta', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
            
            story = [
                Paragraph("CITY CARE CLINICAL SERVICE INVOICE", ts),
                Spacer(1, 15),
                Paragraph(f"<b>Transaction ID:</b> TXN-{info[0]}<br/><b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", ms),
                Spacer(1, 15),
                Paragraph(f"<b>Patient Name:</b> {info[1]} (ID: {info[2]})<br/><b>History:</b> {info[4]}", ms),
                Spacer(1, 10),
                Paragraph(f"<b>Doctor Name:</b> {info[5]} ({info[7]})", ms),
                Spacer(1, 20)
            ]
            
            table_rows = [
                [Paragraph("<b>Service Description</b>", ms), Paragraph("<b>Consultation Fee</b>", ms)],
                [Paragraph(f"Clinical Diagnostic Consultation - Session {info[0]}", ms), Paragraph(f"PKR {float(info[8]):,.2f}", ms)]
            ]
            t = Table(table_rows, colWidths=[350, 150])
            t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFEBEE")), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('PADDING', (0,0), (-1,-1), 8)]))
            story.append(t)
            
            doc.build(story)
            self.trigger_grand_celebration(f"Invoice PDF Ledger compiled and deployed securely to your host directory at:\n{filename}")
        except Exception as e:
            messagebox.showerror("PDF Engine Failure", str(e))

    # --------------------------------------
    # TAB 3: PATIENT RECORDS PORTAL
    # --------------------------------------
    def build_patient_tab(self):
        tab = tk.Frame(self.notebook, bg="#FCE4EC")
        self.notebook.add(tab, text="   Patients Management Records   ")

        form_frame = tk.LabelFrame(tab, text=" Registration Node Configuration ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        fields = ["User ID Name:", "Full Identity Name:", "Email Domain:", "Contact Number:", "DOB (YYYY-MM-DD):", "Gender Configuration:", "History Notes:"]
        self.pat_entries = {}
        for i, f in enumerate(fields):
            tk.Label(form_frame, text=f, bg="#FFFFFF", fg="#1A1A2E").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            allocated_color = self.input_colors[i % len(self.input_colors)]
            glow_color = self.neon_glows[i % len(self.neon_glows)]
            
            e = tk.Entry(form_frame, font=("Segoe UI Semibold", 10, "bold"), width=18, bg=allocated_color, fg="#1A1A2E")
            e.grid(row=i, column=1, padx=10, pady=5)
            self.apply_neon_glow(e, allocated_color, glow_color)
            self.pat_entries[f] = e

        save_btn = tk.Button(form_frame, text="🌻 Save Active Profile", bg="#39FF14", fg="#1A1A2E", font=("Segoe UI", 10, "bold"), 
                  command=self.add_patient, relief=tk.FLAT, bd=0, width=18, height=2, cursor="hand2")
        save_btn.grid(row=7, column=0, columnspan=2, pady=15)
        self.register_button_transition(save_btn, "#FF00FF", "#39FF14")

        list_frame = tk.LabelFrame(tab, text=" Global Database Records Logs ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        controls_bar = tk.Frame(list_frame, bg="#FFFFFF")
        controls_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # ADVANCED FEATURE: Live Search filter for Patients
        tk.Label(controls_bar, text="🔍 Search Active Patient Name:", bg="#FFFFFF").pack(side=tk.LEFT, padx=5)
        self.search_pat_ent = tk.Entry(controls_bar, width=25, bg="#E8F5E9")
        self.search_pat_ent.pack(side=tk.LEFT, padx=5)
        self.search_pat_ent.bind("<KeyRelease>", lambda e: self.refresh_patient_table(filter_text=self.search_pat_ent.get().strip()))

        export_btn = tk.Button(controls_bar, text="📊 Export Pattern Sheet to CSV", bg="#FF00FF", fg="white", font=("Segoe UI", 9, "bold"),
                  command=self.export_patients, relief=tk.FLAT, bd=0, padx=10, pady=5, cursor="hand2")
        export_btn.pack(side=tk.RIGHT)
        self.register_button_transition(export_btn, "#00FFFF", "#FF00FF")

        cols = ("id", "name", "email", "phone", "dob", "gender", "history")
        self.pat_table = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols: self.pat_table.heading(c, text=c.upper())
        self.pat_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.refresh_patient_table()
        self.after(200, lambda: [self.apply_background_emojis(tab, 25), self.apply_background_emojis(list_frame, 15)])

    def export_patients(self):
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT p.patient_id, u.name, u.email, u.phone, p.dob, p.gender, p.medical_history FROM patients p JOIN users u ON p.user_id = u.user_id")
        rows = cursor.fetchall()
        
        df = pd.DataFrame(rows, columns=["Patient ID", "Full Name", "Email Address", "Phone Number", "DOB", "Gender", "Medical History"])
        target_file = "patients_export.csv"
        df.to_csv(target_file, index=False)
        self.trigger_grand_celebration(f"Data Sheet matrix successfully compiled and parsed safely to path root location as:\n[{target_file}]")
        cursor.close()
        conn.close()

    def add_patient(self):
        v = {k: ent.get().strip() for k, ent in self.pat_entries.items()}
        if not (v["User ID Name:"] and v["Full Identity Name:"]):
            messagebox.showerror("Validation Error", "Key attributes cannot be left empty."); return

        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (user_id, password, name, email, phone) VALUES (%s, 'p123', %s, %s, %s)",
                           (v["User ID Name:"], v["Full Identity Name:"], v["Email Domain:"], v["Contact Number:"]))
            p_id = f"PAT-{int(datetime.now().timestamp()) % 100000}"
            cursor.execute("INSERT INTO patients (patient_id, user_id, dob, gender, medical_history) VALUES (%s, %s, %s, %s, %s)",
                           (p_id, v["User ID Name:"], v["DOB (YYYY-MM-DD):"], v["Gender Configuration:"], v["History Notes:"]))
            conn.commit()
            self.populate_dropdowns()
            self.refresh_patient_table()
            self.refresh_analytics()
            self.trigger_grand_celebration(f"New Patient Root Protocol assigned for [{v['Full Identity Name:']}] mapped on ID: {p_id}")
        except mysql.connector.Error as e: messagebox.showerror("SQL Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def refresh_patient_table(self, filter_text=""):
        for i in self.pat_table.get_children(): self.pat_table.delete(i)
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT p.patient_id, u.name, u.email, u.phone, p.dob, p.gender, p.medical_history FROM patients p JOIN users u ON p.user_id = u.user_id")
        
        for idx, row in enumerate(cursor.fetchall()):
            if filter_text and filter_text.lower() not in row[1].lower():
                continue
            color_choice = self.matrix_row_colors[idx % len(self.matrix_row_colors)]
            tag_name = f"pat_row_{idx}"
            self.pat_table.tag_configure(tag_name, background=color_choice)
            modified_row = (f"🌻 {row[0]}", row[1], row[2], row[3], row[4], row[5], f"✨ {row[6]}")
            self.pat_table.insert("", tk.END, values=modified_row, tags=(tag_name,))
            
        cursor.close()
        conn.close()

    # --------------------------------------
    # TAB 4: MEDICAL EXPERTS
    # --------------------------------------
    def build_provider_tab(self):
        tab = tk.Frame(self.notebook, bg="#EBF5FB")
        self.notebook.add(tab, text="   Medical Experts Panel   ")

        form_frame = tk.LabelFrame(tab, text=" Specialist Registry Portal ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        fields = ["User ID Name:", "Doctor Name:", "Email:", "Phone:", "Specialty:", "Fee Amount (PKR):"]
        self.prov_entries = {}
        for i, f in enumerate(fields):
            tk.Label(form_frame, text=f, bg="#FFFFFF", fg="#1A1A2E").grid(row=i, column=0, sticky=tk.W, padx=10, pady=6)
            allocated_color = self.input_colors[(i+2) % len(self.input_colors)]
            glow_color = self.neon_glows[(i+2) % len(self.neon_glows)]
            
            e = tk.Entry(form_frame, font=("Segoe UI Semibold", 10, "bold"), width=18, bg=allocated_color, fg="#1A1A2E")
            e.grid(row=i, column=1, padx=10, pady=6)
            self.apply_neon_glow(e, allocated_color, glow_color)
            self.prov_entries[f] = e

        doc_btn = tk.Button(form_frame, text="🌹 Add Doctor Matrix Panel", bg="#FFD700", fg="#1A1A2E", font=("Segoe UI", 10, "bold"), 
                  command=self.add_provider, relief=tk.FLAT, bd=0, width=22, height=2, cursor="hand2")
        doc_btn.grid(row=6, column=0, columnspan=2, pady=15)
        self.register_button_transition(doc_btn, "#FF007F", "#FFD700")

        list_frame = tk.LabelFrame(tab, text=" Active Clinical Specialist Allocation Networks ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        cols = ("id", "name", "email", "specialty", "fee")
        self.prov_table = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols: self.prov_table.heading(c, text=c.upper())
        self.prov_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.refresh_provider_table()
        self.after(200, lambda: [self.apply_background_emojis(tab, 25), self.apply_background_emojis(list_frame, 15)])

    def add_provider(self):
        v = {k: ent.get().strip() for k, ent in self.prov_entries.items()}
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (user_id, password, name, email, phone) VALUES (%s, 'dpass', %s, %s, %s)",
                           (v["User ID Name:"], v["Doctor Name:"], v["Email:"], v["Phone:"]))
            d_id = f"DOC-{int(datetime.now().timestamp()) % 100000}"
            cursor.execute("INSERT INTO providers (provider_id, user_id, specialty, fee) VALUES (%s, %s, %s, %s)",
                           (d_id, v["User ID Name:"], v["Specialty:"], v["Fee Amount (PKR):"]))
            conn.commit()
            self.populate_dropdowns()
            self.refresh_provider_table()
            self.trigger_grand_celebration(f"Specialist profile assigned completely into registry layers under Dr. {v['Doctor Name:']}.")
        except mysql.connector.Error as e: messagebox.showerror("Database error", str(e))
        finally:
            cursor.close()
            conn.close()

    def refresh_provider_table(self):
        for i in self.prov_table.get_children(): self.prov_table.delete(i)
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT pr.provider_id, u.name, u.email, pr.specialty, pr.fee FROM providers pr JOIN users u ON pr.user_id = u.user_id")
        
        for idx, row in enumerate(cursor.fetchall()):
            color_choice = self.matrix_row_colors[idx % len(self.matrix_row_colors)]
            tag_name = f"prov_row_{idx}"
            self.prov_table.tag_configure(tag_name, background=color_choice)
            modified_row = (f"🦋 {row[0]}", row[1], row[2], row[3], f"PKR {row[4]}")
            self.prov_table.insert("", tk.END, values=modified_row, tags=(tag_name,))
            
        cursor.close()
        conn.close()

    # --------------------------------------
    # TAB 5: STAFF & DUTY SHIFTS LOG
    # --------------------------------------
    def build_staff_tab(self):
        tab = tk.Frame(self.notebook, bg="#FFF8DC")
        self.notebook.add(tab, text="   Human Resource Duty Logs   ")

        form_frame = tk.LabelFrame(tab, text=" Deployment Entry Setup ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        fields = ["User ID Name:", "Staff Name:", "Role / Title:", "Shift Start (HH:MM):", "Shift End (HH:MM):"]
        self.staff_entries = {}
        for i, f in enumerate(fields):
            tk.Label(form_frame, text=f, bg="#FFFFFF", fg="#1A1A2E").grid(row=i, column=0, sticky=tk.W, padx=10, pady=8)
            allocated_color = self.input_colors[(i+4) % len(self.input_colors)]
            glow_color = self.neon_glows[(i+4) % len(self.neon_glows)]
            
            e = tk.Entry(form_frame, font=("Segoe UI Semibold", 10, "bold"), width=18, bg=allocated_color, fg="#1A1A2E")
            e.grid(row=i, column=1, padx=10, pady=8)
            self.apply_neon_glow(e, allocated_color, glow_color)
            self.staff_entries[f] = e

        staff_btn = tk.Button(form_frame, text="🦋 Commit Deployment Matrix", bg="#00FFFF", fg="#1A1A2E", font=("Segoe UI", 10, "bold"), 
                  command=self.add_staff_shift, relief=tk.FLAT, bd=0, width=24, height=2, cursor="hand2")
        staff_btn.grid(row=5, column=0, columnspan=2, pady=15)
        self.register_button_transition(staff_btn, "#FF007F", "#00FFFF")

        list_frame = tk.LabelFrame(tab, text=" HR Employee Schedule Rotation Panel ", bg="#FFFFFF", fg="#1A1A2E", font=("Segoe UI", 11, "bold"), bd=0)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        cols = ("staff_id", "name", "role", "start", "end")
        self.staff_table = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols: self.staff_table.heading(c, text=c.upper())
        self.staff_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.refresh_staff_table()
        self.after(200, lambda: [self.apply_background_emojis(tab, 25), self.apply_background_emojis(list_frame, 15)])

    def add_staff_shift(self):
        v = {k: ent.get().strip() for k, ent in self.staff_entries.items()}
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (user_id, password, name, email, phone) VALUES (%s, 'spass', %s, 'staff@hms.com', 'N/A')",
                           (v["User ID Name:"], v["Staff Name:"]))
            st_id = f"STF-{int(datetime.now().timestamp()) % 100000}"
            cursor.execute("INSERT INTO staff (staff_id, user_id, role) VALUES (%s, %s, %s)", (st_id, v["User ID Name:"], v["Role / Title:"]))
            
            sh_id = f"SHF-{int(datetime.now().timestamp()) % 100000}"
            cursor.execute("INSERT INTO shifts (shift_id, staff_id, start_time, end_time) VALUES (%s, %s, %s, %s)",
                           (sh_id, st_id, v["Shift Start (HH:MM):"], v["Shift End (HH:MM):"]))
            conn.commit()
            self.refresh_staff_table()
            self.trigger_grand_celebration(f"Human Resource roster deployment matrix securely committed for {v['Staff Name:']}.")
        except mysql.connector.Error as e: messagebox.showerror("Database error", str(e))
        finally:
            cursor.close()
            conn.close()

    def refresh_staff_table(self):
        for i in self.staff_table.get_children(): self.staff_table.delete(i)
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        query = """
            SELECT s.staff_id, u.name, s.role, sh.start_time, sh.end_time 
            FROM shifts sh 
            JOIN staff s ON sh.staff_id = s.staff_id 
            JOIN users u ON s.user_id = u.user_id
        """
        cursor.execute(query)
        
        for idx, row in enumerate(cursor.fetchall()):
            color_choice = self.matrix_row_colors[idx % len(self.matrix_row_colors)]
            tag_name = f"staff_row_{idx}"
            self.staff_table.tag_configure(tag_name, background=color_choice)
            modified_row = (f"🔮 {row[0]}", row[1], row[2], row[3], row[4])
            # FIX 2: Double reference 'self.staff_table.staff_table.insert' corrected to direct single object pointer
            self.staff_table.insert("", tk.END, values=modified_row, tags=(tag_name,))
            
        cursor.close()
        conn.close()

# ==========================================
# 3. INTERFACE ENGINE ENGINE STARTUP
# ==========================================
if __name__ == "__main__":
    app = ModernMedicalSystem()
    app.mainloop()

    