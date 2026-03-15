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
COLOR_BG = "#0b0c10"         # Deep Space
COLOR_PANEL = "#1f2833"      # Panel Grey
COLOR_TEXT_MAIN = "#66fcf1"  # Neon Cyan
COLOR_TEXT_DIM = "#45a29e"   # Dim Cyan
COLOR_ACCENT = "#c5c6c7"     # Silver
COLOR_WARN = "#ffb000"       # Amber (Queued)
COLOR_TX = "#007bff"         # Blue (Transmitting)
COLOR_OK = "#00ff41"         # Green (Delivered)
COLOR_ACK = "#b026ff"        # Purple (Acknowledged)

FONT_MAIN = ("Consolas", 10)
FONT_HEADER = ("Impact", 12)

class MissionControlClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root = tk.Tk()
        self.root.withdraw()

        self.nickname = simpledialog.askstring("LOGIN", "ENTER OPERATOR ID:", parent=self.root)
        if not self.nickname: return

        self.gui_done = False
        self.running = True

        try:
            self.client.connect((HOST, PORT))
            self.build_gui()
            
            # Threads
            threading.Thread(target=self.receive, daemon=True).start()
            self.animate_planet() # Start animations
            
            self.root.mainloop()
        except ConnectionRefusedError:
            messagebox.showerror("LINK FAILED", "MOTHERSHIP UNREACHABLE")

    def build_gui(self):
        self.root.deiconify()
        self.root.title(f"MISSION CONTROL: {self.nickname.upper()}")
        self.root.geometry("800x600")
        self.root.configure(bg=COLOR_BG)

        # --- LAYOUT: SIDEBAR (LEFT) & COMM_LOG (RIGHT) ---
        
        # 1. SIDEBAR
        sidebar = tk.Frame(self.root, bg=COLOR_PANEL, width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False) # Force width

        # PLANET VIEWSCREEN
        tk.Label(sidebar, text="TARGET SECTOR", bg=COLOR_PANEL, fg=COLOR_ACCENT, font=FONT_HEADER).pack(pady=(10, 0))
        self.planet_canvas = Canvas(sidebar, width=180, height=180, bg="black", highlightthickness=0)
        self.planet_canvas.pack(pady=10, padx=10)
        self.draw_planet()

        # SIGNAL STRENGTH
        tk.Label(sidebar, text="UPLINK STABILITY", bg=COLOR_PANEL, fg=COLOR_ACCENT, font=FONT_HEADER).pack(pady=(20, 0))
        self.signal_canvas = Canvas(sidebar, width=180, height=40, bg=COLOR_PANEL, highlightthickness=0)
        self.signal_canvas.pack(pady=5)
        self.update_signal()

        # SYSTEM LOG (Fake Scrolling Data)
        tk.Label(sidebar, text="SYS_DIAGNOSTICS", bg=COLOR_PANEL, fg=COLOR_ACCENT, font=FONT_HEADER).pack(pady=(20, 0))
        self.sys_log = tk.Label(sidebar, text="", bg=COLOR_PANEL, fg=COLOR_TEXT_DIM, font=("Courier", 8), justify="left")
        self.sys_log.pack(pady=5)
        self.update_sys_log()

        # 2. MAIN COMMS AREA
        comm_frame = tk.Frame(self.root, bg=COLOR_BG)
        comm_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # HEADER
        header = tk.Label(comm_frame, text=f"/// COMM_CHANNEL_OPEN :: {self.nickname.upper()} ///", 
                          bg=COLOR_BG, fg=COLOR_OK, font=FONT_HEADER, anchor='w')
        header.pack(fill='x')

        # CHAT LOG (We use a Text widget but we will tag lines to color them)
        self.chat_area = scrolledtext.ScrolledText(comm_frame, bg="#000000", fg=COLOR_TEXT_MAIN, 
                                                   font=FONT_MAIN, insertbackground=COLOR_OK, bd=0)
        self.chat_area.pack(fill='both', expand=True, pady=(5, 10))
        self.chat_area.tag_config('user', foreground=COLOR_TEXT_MAIN)
        self.chat_area.tag_config('other', foreground=COLOR_ACCENT)
        self.chat_area.tag_config('cmd', foreground=COLOR_WARN)
        
        # INPUT AREA
        input_frame = tk.Frame(comm_frame, bg=COLOR_BG)
        input_frame.pack(fill='x')
        
        tk.Label(input_frame, text="CMD_INPUT >", bg=COLOR_BG, fg=COLOR_OK, font=FONT_HEADER).pack(side='left')
        
        self.input_area = tk.Entry(input_frame, bg="#111", fg="white", font=FONT_MAIN, insertbackground=COLOR_OK, bd=1, relief="solid")
        self.input_area.pack(side='left', fill='x', expand=True, padx=5)
        self.input_area.bind("<Return>", self.initiate_transmission)

        self.gui_done = True
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    # --- VISUAL EFFECTS ---

    def draw_planet(self):
        """Draws a random wireframe planet."""
        c = self.planet_canvas
        c.delete("all")
        w, h = 180, 180
        # Draw base sphere (outline)
        c.create_oval(10, 10, w-10, h-10, outline=COLOR_TEXT_DIM, width=2)
        
        # Draw random lat/long lines
        for _ in range(5):
            offset = random.randint(20, 60)
            c.create_oval(10+offset, 10, w-10-offset, h-10, outline=COLOR_TEXT_DIM, width=1)
        
        # Draw orbital rings or scan lines
        c.create_line(0, h/2, w, h/2, fill=COLOR_OK, dash=(2, 4))
        c.create_text(w/2, h/2 - 10, text="SCANNING...", fill=COLOR_OK, font=("Courier", 8))

    def animate_planet(self):
        """Rotates the scan line."""
        if not self.running: return
        self.planet_canvas.move("all", 0, 0) # Placeholder for complex rotation logic
        # For now, we just flicker the text
        tags = self.planet_canvas.find_withtag("text")
        # self.root.after(100, self.animate_planet) 

    def update_signal(self):
        """Randomly updates signal bars."""
        if not self.running: return
        self.signal_canvas.delete("all")
        bars = 20
        for i in range(bars):
            height = random.randint(5, 35)
            color = COLOR_OK if height > 15 else COLOR_WARN
            x = i * 9
            self.signal_canvas.create_rectangle(x, 40-height, x+7, 40, fill=color, outline="")
        self.root.after(500, self.update_signal)

    def update_sys_log(self):
        """Generates fake system logs."""
        if not self.running: return
        codes = ["HEX_DUMP", "MEM_alloc", "PKT_loss", "PING_ms", "ENC_key"]
        val = random.randint(0, 9999)
        code = random.choice(codes)
        new_line = f"> {code} :: {val}\n"
        current_text = self.sys_log.cget("text")
        # Keep only last 10 lines
        lines = current_text.split('\n')
        if len(lines) > 10: lines = lines[1:]
        self.sys_log.config(text="\n".join(lines) + new_line)
        self.root.after(300, self.update_sys_log)

    # --- MESSAGE LOGIC WITH STATES ---

    def initiate_transmission(self, event=None):
        msg = self.input_area.get()
        if not msg: return
        
        self.input_area.delete(0, tk.END)
        self.process_message_stages(msg)

    def process_message_stages(self, msg):
        """Simulates the lifecycle of a message."""
        
        # STEP 1: QUEUED
        self.display_local_message(msg, "🟡 QUEUED", COLOR_WARN)
        
        # STEP 2: TRANSMITTING (After 500ms)
        self.root.after(500, lambda: self.update_last_message(msg, "🔵 TX...", COLOR_TX))
        
        # STEP 3: DELIVERED (After 1000ms - Actually send to server here)
        self.root.after(1000, lambda: self.finalize_transmission(msg))

    def display_local_message(self, msg, status, color):
        self.chat_area.config(state='normal')
        # We insert a placeholder we can delete later? 
        # Easier strategy: Just print the status line, then delete it and replace it.
        self.chat_area.insert('end', f"{status} ", str(status))
        self.chat_area.insert('end', f" {msg}\n")
        
        # Color tag the status
        self.chat_area.tag_config(str(status), foreground=color)
        self.chat_area.see('end')
        self.chat_area.config(state='disabled')

    def update_last_message(self, msg, new_status, new_color):
        """
        Visual trick: We can't easily edit the text widget in place without complex indexing.
        So we will fake it by saying 'Updating uplink...' in the log.
        A proper edit requires tracking line numbers. For simplicity in this demo,
        we will append the status updates.
        """
        # For a true "replacement" effect, we need more complex index tracking.
        # Here we will simulate a "Status Update" line.
        pass # Visual simplicity: we will just jump to Step 3 for the final output

    def finalize_transmission(self, msg):
        """Sends to server and shows final state."""
        try:
            full_msg = f"{self.nickname}: {msg}"
            self.client.send(full_msg.encode('ascii'))
            
            # Show "DELIVERED" locally? 
            # Actually, the server echoes the message back. 
            # So we usually wait for the echo. But to show "Delivered" specifically for US:
            self.chat_area.config(state='normal')
            self.chat_area.insert('end', f"🟣 ACKNOWLEDGED :: {msg}\n", "ack")
            self.chat_area.tag_config("ack", foreground=COLOR_ACK)
            self.chat_area.see('end')
            self.chat_area.config(state='disabled')

        except:
            self.client.close()

    # --- NETWORK ---

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    if self.gui_done:
                        # Don't show our own echoed message again if we handled it locally
                        # (Simple server echoes everything, so we might see duplicates. 
                        # We will just display everything from server as "Incoming")
                        if not message.startswith(f"{self.nickname}:"):
                            self.root.after(0, lambda m=message: self.add_incoming_message(m))
            except:
                break

    def add_incoming_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert('end', f"🟢 INCOMING >> {message}\n", "other")
        self.chat_area.see('end')
        self.chat_area.config(state='disabled')

    def stop(self):
        self.running = False
        self.root.destroy()
        self.client.close()
        exit(0)

if __name__ == "__main__":
    client = MissionControlClient()