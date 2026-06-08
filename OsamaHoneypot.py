#!/usr/bin/env python3
# OsamaHoneypot.py - SSH Honeypot Professional
# Developed by: Osama
# Version: 3.0 Pro - Ultimate Edition

import sys
import os
import subprocess
import time

os.system('clear' if os.name == 'posix' else 'cls')

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

print(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║    ██████╗ ███████╗ █████╗ ███╗   ███╗ █████╗     ██╗  ██╗ ██████╗ ███╗   ██╗███████╗║
║   ██╔═══██╗██╔════╝██╔══██╗████╗ ████║██╔══██╗    ██║  ██║██╔══██╗████╗  ██║██╔════╝║
║   ██║   ██║███████╗███████║██╔████╔██║███████║    ███████║███████║██╔██╗ ██║█████╗  ║
║   ██║   ██║╚════██║██╔══██║██║╚██╔╝██║██╔══██║    ██╔══██║██╔══██║██║╚██╗██║██╔══╝  ║
║   ╚██████╔╝███████║██║  ██║██║ ╚═╝ ██║██║  ██║    ██║  ██║██║  ██║██║ ╚████║███████╗║
║    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
{RESET}
""")

print(f"{BLUE}{BOLD}                    SSH HONEYPOT PROFESSIONAL - ULTIMATE EDITION{RESET}")
print(f"{MAGENTA}                            🍯  by: OSAMA  🍯{RESET}")
print(f"{YELLOW}                          Version: 3.0 Pro{RESET}\n")

print(f"{WHITE}[{GREEN}✦{WHITE}] تهيئة البيئة", end="", flush=True)
time.sleep(0.5)
print(f" {GREEN}✓{RESET}")

print(f"{WHITE}[{GREEN}✦{WHITE}] فحص المتطلبات", end="", flush=True)
time.sleep(0.5)
print(f" {GREEN}✓{RESET}")

def progress_bar():
    print(f"\n{WHITE}[{CYAN}⟳{WHITE}] جاري تحميل المحرك الأساسي...{RESET}")
    for i in range(101):
        bar_length = 40
        filled_length = int(bar_length * i // 100)
        bar = f"{GREEN}{'█' * filled_length}{WHITE}{'░' * (bar_length - filled_length)}{RESET}"
        print(f"\r    [{bar}] {i}%", end="", flush=True)
        time.sleep(0.01)
    print(f"\n{WHITE}[{GREEN}✓{WHITE}] تم التحميل بنجاح!{RESET}\n")

progress_bar()

def check_requirements():
    try:
        import paramiko, requests
        print(f"{WHITE}[{GREEN}✓{WHITE}] جميع المكتبات موجودة{RESET}")
    except ImportError:
        print(f"{WHITE}[{RED}✗{WHITE}] جاري تثبيت المكتبات...{RESET}")
        subprocess.run(['pip3', 'install', 'paramiko', 'requests', '--break-system-packages'])

def check_root():
    if os.geteuid() != 0:
        print(f"\n{RED}{BOLD}[!] يرجى التشغيل بصلاحيات root: sudo python3 OsamaHoneypot.py{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    check_requirements()
    check_root()
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from modules.server import OsamaHoneypotServer
    from config import TELEGRAM_ENABLED
    
    print(f"{WHITE}[{GREEN}⚡{WHITE}] تشغيل الخادم...{RESET}")
    print(f"{WHITE}[{BLUE}🌐{WHITE}] المستمع: 0.0.0.0:2222{RESET}")
    print(f"{WHITE}[{MAGENTA}🗺️{WHITE}] رابط خريطة Google Maps: مفعل{RESET}")
    print(f"{WHITE}[{YELLOW}📱{WHITE}] إشعارات تلجرام: {'مفعل' if TELEGRAM_ENABLED else 'معطل'}{RESET}\n")
    
    server = OsamaHoneypotServer()
    server.start()
