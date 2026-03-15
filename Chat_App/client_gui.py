import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, Canvas
import random
import time
import math

HOST = '127.0.0.1'
PORT = 55555

# --- MISSION CONTROL PALETTE ---
C_BG = "#050505"       # Void Black
C_PANEL = "#111111"    # Dark Panel
C_BORDER = "#333333"   # Grey Border
C_ACCENT = "#00FF41"   # Radar Green
C_TEXT = "#E0E0E0"     # White/Grey Text
C_ALERT = "#FF3333"    # Red Alert

class MissionControl:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root = tk.Tk()
        self.root.withdraw()

        # Login
        self.nickname = simpledialog.askstring("LOGIN", "ENTER OPERATOR CALLSIGN:", parent=self.root)
        if not self.nickname: return

        self.gui_done = False
        self.running = True

        try:
            self.client.connect((HOST, PORT))
            self.build_gui()
            
            # Start Threads
            threading.Thread(target=self.receive, daemon=True).start()
            self.animate_radar() 
            
            self.root.mainloop()
        except:
            messagebox.showerror("ERROR", "SERVER OFFLINE")

    def build_gui(self):
        self.root.deiconify()
        self.root.title("/// MISSION CONTROL ///")
        self.root.geometry("900x600")
        self.root.configure(bg=C_BG)

        # --- MAIN CONTAINER (3 COLUMNS) ---
        # 1. LEFT SIDEBAR (RADAR)
        self.frame_left = tk.Frame(self.root, bg=C_PANEL, width=250, bd=1, relief="solid")
        self.frame_left.pack(side="left", fill="y", padx=5, pady=5)
        self.frame_left.pack_propagate(False) # Force width

        # 2. CENTER (CHAT)
        self.frame_center = tk.Frame(self.root, bg=C_BG, bd=1, relief="solid")
        self.frame_center.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # 3. RIGHT SIDEBAR (STATUS)
        self.frame_right = tk.Frame(self.root, bg=C_PANEL, width=200, bd=1, relief="solid")
        self.frame_right.pack(side="right", fill="y", padx=5, pady=5)
        self.frame_right.pack_propagate(False)

        # --- LEFT SIDEBAR CONTENT ---
        tk.Label(self.frame_left, text="SECTOR SCAN", bg=C_PANEL, fg=C_ACCENT, font=("Impact", 12)).pack(pady=10)
        
        # RADAR CANVAS
        self.radar = Canvas(self.frame_left, width=200, height=200, bg="black", highlightthickness=0)
        self.radar.pack(pady=10)
        self.draw_grid()

        # SIGNAL BARS
        tk.Label(self.frame_left, text="UPLINK STRENGTH", bg=C_PANEL, fg=C_ACCENT, font=("Consolas", 10)).pack(pady=(20,5))
        self.signal_lbl = tk.Label(self.frame_left, text="|||||||||||| 100%", bg=C_PANEL, fg=C_ACCENT, font=("Consolas", 10))
        self.signal_lbl.pack()

        # --- CENTER CONTENT ---
        # Header
        tk.Label(self.frame_center, text=f"COMMUNICATION LINK :: {self.nickname.upper()}", 
                 bg=C_BG, fg=C_ACCENT, font=("Consolas", 14, "bold")).pack(pady=10)

        # Chat Area
        self.chat_area = scrolledtext.ScrolledText(self.frame_center, bg="black", fg=C_TEXT, 
                                                   font=("Consolas", 10), insertbackground=C_ACCENT)
        self.chat_area.pack(fill="both", expand=True, padx=10, pady=5)
        self.chat_area.config(state='disabled')

        # Input Area
        input_frame = tk.Frame(self.frame_center, bg=C_BG)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(input_frame, text="CMD >", bg=C_BG, fg=C_ACCENT, font=("Consolas", 12)).pack(side="left")
        
        self.input_area = tk.Entry(input_frame, bg="#111", fg="white", font=("Consolas", 12), insertbackground=C_ACCENT)
        self.input_area.pack(side="left", fill="x", expand=True, padx=5)
        self.input_area.bind("<Return>", self.send_sequence)

        # --- RIGHT SIDEBAR CONTENT ---
        tk.Label(self.frame_right, text="STATUS LOG", bg=C_PANEL, fg=C_ACCENT, font=("Impact", 12)).pack(pady=10)
        self.log_lbl = tk.Label(self.frame_right, text="Sys_Boot...OK\nNet_Init...OK", 
                                bg=C_PANEL, fg="#555", font=("Courier", 8), justify="left")
        self.log_lbl.pack(pady=10, anchor="w", padx=10)

        self.gui_done = True
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    # --- RADAR ANIMATION ---
    def draw_grid(self):
        # Static Grid
        self.radar.create_oval(10, 10, 190, 190, outline="#333") # Outer Ring
        self.radar.create_oval(50, 50, 150, 150, outline="#333") # Inner Ring
        self.radar.create_line(100, 10, 100, 190, fill="#333")   # Vertical
        self.radar.create_line(10, 100, 190, 100, fill="#333")   # Horizontal
        
        # Random "Planet" Lines
        for _ in range(3):
            x1, y1 = random.randint(40, 160), random.randint(40, 160)
            x2, y2 = random.randint(40, 160), random.randint(40, 160)
            self.radar.create_line(x1, y1, x2, y2, fill=C_ACCENT, tags="planet")

    def animate_radar(self):
        if not self.running: return
        # Rotating Scan Line
        angle = (time.time() * 2) % (2 * math.pi)
        x = 100 + 90 * math.cos(angle)
        y = 100 + 90 * math.sin(angle)
        
        self.radar.delete("scan")
        self.radar.create_line(100, 100, x, y, fill="green", width=2, tags="scan")
        
        # Random Signal Flicker
        bars = "|" * random.randint(5, 15)
        self.signal_lbl.config(text=f"{bars} {len(bars)*6}%")
        
        self.root.after(50, self.animate_radar)

    # --- MESSAGE SENDING SEQUENCE ---
    def send_sequence(self, event=None):
        msg = self.input_area.get()
        if not msg: return
        self.input_area.delete(0, tk.END)

        # 1. QUEUED
        self.log_to_chat(f"🟡 QUEUED: {msg}", "yellow")
        
        # 2. TRANSMITTING (Delay 0.5s)
        self.root.after(500, lambda: self.log_to_chat(f"🔵 TRANSMITTING...", "cyan"))
        
        # 3. DELIVERED (Delay 1.0s)
        self.root.after(1000, lambda: self.finalize_send(msg))

    def finalize_send(self, msg):
        try:
            full_msg = f"{self.nickname}: {msg}"
            self.client.send(full_msg.encode('ascii'))
            self.log_to_chat(f"🟣 ACKNOWLEDGED: {msg}", "magenta")
        except:
            self.client.close()

    def log_to_chat(self, text, color):
        self.chat_area.config(state='normal')
        self.chat_area.insert('end', text + "\n", color)
        self.chat_area.tag_config(color, foreground=color)
        self.chat_area.see('end')
        self.chat_area.config(state='disabled')

    # --- RECEIVING ---
    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    if self.gui_done:
                        if not message.startswith(f"{self.nickname}:"):
                            self.log_to_chat(f"🟢 INCOMING: {message}", "green")
            except:
                break

    def stop(self):
        self.running = False
        self.root.destroy()
        self.client.close()
        exit(0)

if __name__ == "__main__":
    MissionControl()