from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# Your exclusion list
EXCLUDED = {"Adamstown", "Akron", "Columbia", "Denver", "East Petersburg", "Elizabethtown", "Ephrata", "Lititz", "Manheim", "Marietta", "Mount Joy", "Mountville", "Terre Hill", "Brecknock", "Caernarvon", "Clay", "Conoy", "Earl", "East Cocalico", "East Donegal", "East Earl", "East Hempfield", "Elizabeth", "Ephrata", "Mount Joy", "Penn", "Rapho", "Warwick", "West Cocalico", "West Donegal", "West Earl", "West Hempfield"}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>🚒 HEADS ⚠️ UP! 🚓</title>
<style>
body { background: #003087; color: #ffffff; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; line-height: 1.5; max-width: 820px; margin-left: auto; margin-right: auto; }
h1 { font-size: 1.85rem; margin: 0 0 6px 0; text-align: center; }
.refresh { color: #ffd700; font-size: 0.95rem; text-align: center; margin-bottom: 28px; }
h2 { font-size: 1.35rem; margin: 32px 0 12px 0; color: #ffffff; border-bottom: 2px solid #ffffff; padding-bottom: 8px; }
.incident { margin-bottom: 22px; padding-bottom: 8px; }
.time { color: #ffd700; font-weight: 600; font-size: 1.02rem; }
.type, .location1, .location2, .unit { color: #ffffff; }
.note { font-size: 0.85rem; color: #b0c4ff; text-align: center; margin-top: 40px; }
a { color: #ffd700; text-decoration: underline; }
</style>
</head>
<body>
<h1><a href="https://www.facebook.com/share/g/18kXZHveJh/" target="_blank">Lampeter-Strasburg & Surrounding Communities</a></h1>
<h1>🚒 HEADS ⚠️ UP! 🚓</h1>
<div class="refresh">Last refreshed time: {{ last_refreshed }}</div>

<h2>Active Fire Incidents 🔥</h2>
{% for inc in fire_incidents %}
<div class="incident">
<div class="time">{{ inc['time'] }}</div>
<div class="type">{{ inc['type'] }}</div>
<div class="location1">{{ inc['loc1'] }}</div>
<div class="location2">{{ inc['loc2'] }}</div>
{% for u in inc['units'] %}<div class="unit">{{ u }}</div>{% endfor %}
</div>
{% endfor %}

<h2>Active Traffic Incidents 🚔</h2>
{% for inc in traffic_incidents %}
<div class="incident">
<div class="time">{{ inc['time'] }}</div>
<div class="type">{{ inc['type'] }}</div>
<div class="location1">{{ inc['loc1'] }}</div>
<div class="location2">{{ inc['loc2'] }}</div>
</div>
{% endfor %}

</body>
</html>
"""

@app.route("/")
def index():
    try:
        resp = requests.get("https://www.lcwc911.us/live-incident-list", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'lxml')

        # Eastern Time (EDT)
        now_et = datetime.now(timezone.utc) - timedelta(hours=4)
        last_refreshed = now_et.strftime("%a, %b %d, %Y %H:%M")

        # Basic parsing - this is simplified for now
        fire_incidents = []
        traffic_incidents = []

        return render_template_string(HTML_TEMPLATE, last_refreshed=last_refreshed, fire_incidents=fire_incidents, traffic_incidents=traffic_incidents)

    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><p>Refresh the page.</p>", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
