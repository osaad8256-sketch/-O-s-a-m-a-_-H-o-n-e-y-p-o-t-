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
            writer.writerow(['timestamp', 'attacker_ip', 'username', 'password', 'country', 'city', 'latitude', 'longitude', 'maps_link'])
        
        self.logger = logging.getLogger('OsamaHoneypot')
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(self.text_log)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(file_handler)
    
    def get_location_from_ip(self, ip):
        """جلب الموقع من IP باستخدام API خارجي"""
        
        if ip.startswith('127.'):
            return "Local (Your Own Device)", "Localhost", None, None
        
        if ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.')):
            return "Local Network", "Private IP", None, None
        
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            data = response.json()
            
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown')
                city = data.get('city', 'Unknown')
                lat = data.get('lat', None)
                lon = data.get('lon', None)
                return country, city, lat, lon
        except:
            pass
        
        return "Unknown", "Unknown", None, None
    
    def get_maps_link(self, lat, lon, ip):
        """توليد رابط Google Maps"""
        if ip.startswith('127.'):
            return "https://www.google.com/maps?q=Your+Own+Device"
        if ip.startswith(('192.168.', '10.', '172.')):
            return "https://www.google.com/maps?q=Your+Local+Network"
        
        if lat and lon:
            return f"https://www.google.com/maps?q={lat},{lon}"
        return "https://www.google.com/maps?q=Unknown+Location"
    
    def send_telegram(self, ip, username, password, country, city, maps_link):
        if not TELEGRAM_ENABLED:
            return
        
        message = f"""
🚨 *OSAMA HONEYPOT - هجوم جديد* 🚨

🌍 *IP:* `{ip}`
📍 *الدولة:* {country}
🏙️ *المدينة:* {city}
🗺️ *الخريطة:* {maps_link}
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
    
    def log_attack(self, ip, username, password):
        self.attack_counter += 1
        self.unique_ips.add(ip)
        
        country, city, lat, lon = self.get_location_from_ip(ip)
        maps_link = self.get_maps_link(lat, lon, ip)
        
        attack_data = {
            "id": self.attack_counter,
            "timestamp": datetime.now().isoformat(),
            "attacker_ip": ip,
            "username": username,
            "password": password,
            "country": country,
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "maps_link": maps_link
        }
        
        with open(self.json_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(attack_data, ensure_ascii=False) + '\n')
        
        with open(self.csv_log, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), ip, username, password, country, city, lat, lon, maps_link])
        
        self.logger.info(f"ATTACK | {ip} | {username} | {password} | {country} | {city}")
        
        self.send_telegram(ip, username, password, country, city, maps_link)
        
        self.display_attack(attack_data)
        
        return attack_data
    
    def display_attack(self, attack):
        print(f"""
\033[91m╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  🚨 OSAMA HONEYPOT - هجوم مكتشف! 🚨                                                              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════╣
║  📍 الوقت   : {attack['timestamp']}
║  🌍 IP المهاجم : {attack['attacker_ip']}
║  🌏 الدولة  : {attack['country']}
║  🏙️ المدينة : {attack['city']}
║  👤 اليوزر : {attack['username']}
║  🔑 الباسورد: {attack['password']}
║  📊 إجمالي الهجمات: {self.attack_counter}
║  🎯 عدد المهاجمين: {len(self.unique_ips)}""")
        
        if attack.get('maps_link'):
            print(f"\033[96m║  🗺️ خريطة الموقع: {attack['maps_link']}\033[0m")
        
        print(f"\033[91m╚══════════════════════════════════════════════════════════════════════════════════════════════╝\033[0m")
    
    def get_stats(self):
        return {
            "total_attacks": self.attack_counter,
            "unique_attackers": len(self.unique_ips),
            "log_file": self.text_log,
            "json_file": self.json_log,
            "csv_file": self.csv_log
        }
