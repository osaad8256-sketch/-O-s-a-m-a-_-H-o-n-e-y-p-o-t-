#!/usr/bin/env python3
# modules/logger.py
# Developed by: Osama

import logging
import json
import csv
import os
import requests
from datetime import datetime
from config import LOG_DIR, DATA_DIR, TELEGRAM_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class OsamaLogger:
    
    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.attack_counter = 0
        self.unique_ips = set()
        
    def setup_directories(self):
        for dir_path in [LOG_DIR, DATA_DIR]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
    
    def setup_logging(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.text_log = f"{LOG_DIR}/osama_honeypot_{self.timestamp}.log"
        self.json_log = f"{DATA_DIR}/attacks_{self.timestamp}.json"
        self.csv_log = f"{DATA_DIR}/attacks_{self.timestamp}.csv"
        
        with open(self.csv_log, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'attacker_ip', 'username', 'password', 'country', 'city'])
        
        self.logger = logging.getLogger('OsamaHoneypot')
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(self.text_log)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(file_handler)
    
    def send_telegram(self, ip, username, password, country, city):
        if not TELEGRAM_ENABLED:
            return
        
        message = f"""
🚨 *OSAMA HONEYPOT - هجوم جديد* 🚨

🌍 *IP:* `{ip}`
📍 *الدولة:* {country}
🏙️ *المدينة:* {city}
👤 *اليوزر:* `{username}`
🔑 *الباسورد:* `{password}`
🕐 *الوقت:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            requests.post(url, data=data, timeout=5)
        except:
            pass
    
    def log_attack(self, ip, username, password, country="Unknown", city="Unknown"):
        self.attack_counter += 1
        self.unique_ips.add(ip)
        
        attack_data = {
            "id": self.attack_counter,
            "timestamp": datetime.now().isoformat(),
            "attacker_ip": ip,
            "username": username,
            "password": password,
            "country": country,
            "city": city
        }
        
        with open(self.json_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(attack_data, ensure_ascii=False) + '\n')
        
        with open(self.csv_log, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), ip, username, password, country, city])
        
        self.logger.info(f"ATTACK | {ip} | {username} | {password} | {country} | {city}")
        
        self.send_telegram(ip, username, password, country, city)
        
        self.display_attack(attack_data)
        
        return attack_data
    
    def display_attack(self, attack):
        print(f"""
\033[91m╔════════════════════════════════════════════════════════════════════════════╗
║  🚨 OSAMA HONEYPOT - هجوم مكتشف! 🚨                                              ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  📍 الوقت   : {attack['timestamp']}
║  🌍 IP المهاجم : {attack['attacker_ip']}
║  🌏 الدولة  : {attack['country']}
║  🏙️ المدينة : {attack['city']}
║  👤 اليوزر : {attack['username']}
║  🔑 الباسورد: {attack['password']}
║  📊 إجمالي الهجمات: {self.attack_counter}
║  🎯 عدد المهاجمين: {len(self.unique_ips)}
╚════════════════════════════════════════════════════════════════════════════════╝\033[0m
        """)
    
    def get_stats(self):
        return {
            "total_attacks": self.attack_counter,
            "unique_attackers": len(self.unique_ips),
            "log_file": self.text_log,
            "json_file": self.json_log,
            "csv_file": self.csv_log
        }
