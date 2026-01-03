P2P File Share - LAN Peer-to-Peer File Transfer
Simple desktop file sharing app for local networks. Auto-discovers peers via UDP broadcast, transfers files over TCP. No server setup required.

✨ Features
✅ Automatic Peer Discovery - Finds peers on LAN within seconds

✅ Clean Tkinter GUI - Peer list, file browser, real-time logs

✅ Reliable File Transfer - Chunked TCP transfers with error handling

✅ Zero Dependencies - Uses Python standard library only

✅ Cross-Platform - Windows/Linux/macOS


🚀 Quick Start

# Download fixed_p2p_client.py from this repo
# Run on each machine (same network)
python fixed_p2p_client.py

🖥️ How It Works

UDP Port 12345: Peer discovery broadcasts every 3s
TCP Port 12346: File transfer server (always listening)
Localhost: Works on the same machine (multiple terminals)
LAN: Auto-discovers across WiFi/Ethernet
