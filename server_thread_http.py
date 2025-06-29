# server.py (Tidak ada perubahan)
import socket
import threading
import logging
import os

from http import HttpServer

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

GAMES = {}
GAMES_LOCK = threading.Lock()
DICTIONARY = set()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address, http_handler):
        self.connection = connection
        self.address = address
        self.http_handler = http_handler
        threading.Thread.__init__(self)
        self.setName(f"Client-{address[0]}:{address[1]}")

    def run(self):
        try:
            request_text = self.connection.recv(4096).decode('utf-8')
            if not request_text: return
            response_bytes = self.http_handler.proses(request_text)
            self.connection.sendall(response_bytes)
        except Exception as e:
            logging.error(f"Error pada thread client {self.address}: {e}", exc_info=True)
        finally:
            self.connection.close()
            logging.info(f"Koneksi dengan {self.address} ditutup.")

class Server(threading.Thread):
    def __init__(self, port):
        self.port = port
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.http_handler = HttpServer(GAMES, GAMES_LOCK, DICTIONARY)
        threading.Thread.__init__(self)
        self.setName("ServerThread")

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(10)
        logging.info(f"Server socket berjalan di http://localhost:{self.port}/")
        try:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.info(f"Koneksi diterima dari {client_address}")
                clt = ProcessTheClient(connection, client_address, self.http_handler)
                clt.start()
        except KeyboardInterrupt:
            logging.info("Server diminta berhenti.")
        finally:
            self.my_socket.close()
            logging.info("Socket server ditutup.")

def setup_dictionary():
    try:
        dictionary_path = os.path.join(os.path.dirname(__file__), 'static', 'dictionary.txt')
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            DICTIONARY.update(line.strip().upper() for line in f)
        logging.info(f"Kamus berhasil dimuat: {len(DICTIONARY)} kata.")
    except FileNotFoundError:
        logging.warning(f"File dictionary.txt tidak ditemukan. Menggunakan kamus fallback.")
        DICTIONARY.update({"KULIT", "RUMAH", "KOTA", "MATA", "HATI", "BUKU", "PENA", "PINTAR", "AKAN"})

def main():
    setup_dictionary()
    server = Server(8000)
    server.start()
    server.join()
    logging.info("Server dihentikan sepenuhnya.")

if __name__=="__main__":
    main()