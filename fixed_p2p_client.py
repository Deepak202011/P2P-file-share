import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import json
import os
import time

class P2PClient:
    def __init__(self):
        self.username = ""
        self.peers = {}
        self.files = []
        self.server_sock = None
        self.root = tk.Tk()
        self.root.withdraw()
        self.username_window()  # Fixed call

    def username_window(self):  # Fixed: accepts implicit self
        self.username_window_obj = tk.Toplevel(self.root)  # Renamed to avoid conflict
        self.username_window_obj.title("P2P File Share")
        self.username_window_obj.geometry("300x150")
        tk.Label(self.username_window_obj, text="Enter your name:").pack(pady=20)
        self.username_entry = tk.Entry(self.username_window_obj, width=20)
        self.username_entry.pack(pady=10)
        self.username_entry.bind('<Return>', lambda e: self.start_main_app())
        tk.Button(self.username_window_obj, text="Start", command=self.start_main_app).pack()

    def start_main_app(self):
        self.username = self.username_entry.get().strip()
        if self.username:
            self.username_window_obj.destroy()
            self.root.deiconify()
            self.build_ui()
            self.start_network()
        else:
            messagebox.showerror("Error", "Username required!")

    def build_ui(self):
        self.root.title(f"P2P - {self.username}")
        self.peer_listbox = tk.Listbox(self.root, height=10)
        self.peer_listbox.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        self.file_listbox = tk.Listbox(self.root, height=10)
        self.file_listbox.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
        tk.Button(self.root, text="Add Files", command=self.add_file).pack(pady=5)
        tk.Button(self.root, text="Send File", command=self.send_file).pack(pady=5)
        self.log_text = scrolledtext.ScrolledText(self.root, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def start_network(self):
        threading.Thread(target=self.discovery_loop, daemon=True).start()
        threading.Thread(target=self.listen_for_peers, daemon=True).start()
        threading.Thread(target=self.file_server, daemon=True).start()
        self.log("Network started - waiting for peers...")

    def discovery_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                msg = json.dumps({"type": "HELLO", "user": self.username, "port": 12346})
                sock.sendto(msg.encode(), ('<broadcast>', 12345))
                time.sleep(3)
            except:
                pass

    def listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 12345))
        while True:
            try:
                data, (ip, _) = sock.recvfrom(1024)
                peer = json.loads(data.decode())
                if peer['type'] == 'HELLO' and ip != '127.0.0.1':
                    self.peers[ip] = {'name': peer['user'], 'port': peer['port']}
                    self.log(f"Peer found: {peer['user']} ({ip})")
                    self.update_peer_list()
            except:
                pass

    def update_peer_list(self):
        self.peer_listbox.delete(0, tk.END)
        for ip, info in self.peers.items():
            self.peer_listbox.insert(tk.END, f"{info['name']} ({ip})")

    def file_server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('', 12346))
        self.server_sock.listen(5)
        self.log("File server listening on 12346")
        while True:
            client, addr = self.server_sock.accept()
            threading.Thread(target=self.handle_file_req, args=(client,), daemon=True).start()

    def handle_file_req(self, client):
        try:
            filename = client.recv(1024).decode()
            filepath = next((f for f in self.files if os.path.basename(f) == filename), None)
            if filepath:
                client.send(f"OK|{os.path.getsize(filepath)}".encode())
                with open(filepath, 'rb') as f:
                    while chunk := f.read(4096):
                        client.send(chunk)
                self.log(f"Sent {filename}")
            else:
                client.send(b"ERROR")
        except:
            client.send(b"ERROR")
        client.close()

    def add_file(self):
        files = filedialog.askopenfilenames()
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))
        self.log(f"Added {len(files)} files")

    def send_file(self):
        sel = self.file_listbox.curselection()
        if not sel or not self.peers:
            self.log("Select file & ensure peers found!")
            return
        filename = self.file_listbox.get(sel[0])
        peer_ip = simpledialog.askstring("Send", "Peer IP:")
        if peer_ip and peer_ip in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((peer_ip, 12346))
                sock.send(filename.encode())
                resp = sock.recv(1024).decode()
                if resp.startswith('OK'):
                    self.log(f"Sending {filename}...")
                    with open(f"rcvd_{filename}", 'wb') as f:
                        while data := sock.recv(4096):
                            f.write(data)
                    self.log("Transfer complete!")
                sock.close()
            except Exception as e:
                self.log(f"Error: {e}")

if __name__ == "__main__":
    print("Starting P2PClient...")
    app = P2PClient()
    print("Client created, starting mainloop...")
    app.root.mainloop()  # Critical: keeps GUI alive
    print("App closed.")

