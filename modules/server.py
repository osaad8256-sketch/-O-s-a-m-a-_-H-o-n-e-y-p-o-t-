#!/usr/bin/env python3
# modules/server.py
# Developed by: Osama

import socket
import threading
import paramiko
import time
import os
from config import HOST, PORT, SERVER_KEY_FILE
from modules.logger import OsamaLogger

class OsamaSSHServer(paramiko.ServerInterface):
    
    def __init__(self, logger):
        self.logger = logger
        self.transport = None
    
    def check_auth_password(self, username, password):
        client_ip = self.transport.getpeername()[0]
        self.logger.log_attack(client_ip, username, password)
        return paramiko.AUTH_FAILED
    
    def check_auth_publickey(self, username, key):
        client_ip = self.transport.getpeername()[0]
        self.logger.log_attack(client_ip, username, "[PUBLIC_KEY]")
        return paramiko.AUTH_FAILED
    
    def get_allowed_auths(self, username):
        return "password"

class OsamaHoneypotServer:
    
    def __init__(self):
        self.logger = OsamaLogger()
        self.host_key = self.load_or_create_key()
        
    def load_or_create_key(self):
        if os.path.exists(SERVER_KEY_FILE):
            try:
                return paramiko.RSAKey.from_private_key_file(SERVER_KEY_FILE)
            except:
                os.remove(SERVER_KEY_FILE)
                return self.create_new_key()
        else:
            return self.create_new_key()
    
    def create_new_key(self):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(SERVER_KEY_FILE)
        print(f"[+] تم إنشاء مفتاح جديد: {SERVER_KEY_FILE}")
        return key
    
    def handle_client(self, client_socket, client_address):
        try:
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(self.host_key)
            transport.local_version = "SSH-2.0-OpenSSH_8.9p1 Ubuntu"
            
            server = OsamaSSHServer(self.logger)
            server.transport = transport
            
            try:
                transport.start_server(server=server)
            except paramiko.SSHException:
                return
            
            transport.accept(20)
            
        except Exception as e:
            pass
        finally:
            client_socket.close()
    
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((HOST, PORT))
        except PermissionError:
            print(f"[!] المنفذ {PORT} محتاج صلاحيات root")
            print(f"[*] جرب تشغيل: sudo python3 OsamaHoneypot.py")
            return
        except Exception as e:
            print(f"[!] خطأ: {e}")
            return
        
        server_socket.listen(100)
        
        try:
            from config import TELEGRAM_ENABLED
            tele_status = "مفعل" if TELEGRAM_ENABLED else "معطل"
        except:
            tele_status = "معطل"
        
        print(f"""
\033[92m╔══════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ✅ السيرفر شغال بنجاح!                                             ║
║   🌐 المستمع: {HOST}:{PORT}                                           ║
║   📁 مجلد اللوجات: logs/                                             ║
║   🗺️ رابط خريطة Google Maps: مفعل                                   ║
║   🤖 إشعارات تلجرام: {tele_status}                                    ║
║   🎯 مستني الهجمات...                                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝\033[0m
        """)
        
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"\n\033[96m[+] اتصال جديد من {client_address[0]}\033[0m")
                
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                thread.daemon = True
                thread.start()
                
        except KeyboardInterrupt:
            self.shutdown()
        finally:
            server_socket.close()
    
    def shutdown(self):
        print(f"\n\033[93m")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║                    📊 الإحصائيات النهائية               ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        stats = self.logger.get_stats()
        print(f"""
   ✅ إجمالي الهجمات     : {stats['total_attacks']}
   🎯 عدد المهاجمين     : {stats['unique_attackers']}
   📁 ملف اللوج         : {stats['log_file']}
   📄 ملف JSON          : {stats['json_file']}
   📊 ملف CSV           : {stats['csv_file']}
        """)
        print(f"\n[+] شكراً لاستخدام Osama Honeypot\033[0m")
