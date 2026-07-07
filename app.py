from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

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
a { color: #ffd700; }
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

        last_refreshed = datetime.now().strftime("%a, %b %d, %Y %H:%M")

        # Improved parsing
        fire_incidents = []
        traffic_incidents = []

        # Find all time lines
        time_pattern = re.compile(r'^(Sun|Mon|Tue|Wed|Thu|Fri|Sat),\s+\w+\s+\d+,\s+\d{4}\s+\d{1,2}:\d{2}$')
        time_elements = soup.find_all(string=time_pattern)

        for time_elem in time_elements:
            try:
                time_str = time_elem.strip()
                parent = time_elem.find_parent()
                lines = [line.strip() for line in parent.find_all(string=True) if line.strip() and not time_pattern.match(line.strip())]

                if len(lines) < 3:
                    continue

                inc_type = lines[0]
                loc1 = lines[1]
                loc2 = lines[2]
                units = [u.strip() for u in lines[3:] if u.strip() and not re.search(r'PENDING|None', u, re.I)]

                if loc2 in EXCLUDED:
                    continue

                inc = {
                    'time': time_str,
                    'type': inc_type,
                    'loc1': loc1,
                    'loc2': loc2,
                    'units': units
                }

                if "TRAFFIC" in inc_type.upper() or "ACCIDENT" in inc_type.upper() or "HAZARD" in inc_type.upper():
                    traffic_incidents.append(inc)
                else:
                    fire_incidents.append(inc)

            except:
                continue

        return render_template_string(HTML_TEMPLATE, last_refreshed=last_refreshed, fire_incidents=fire_incidents, traffic_incidents=traffic_incidents)

    except Exception as e:
        return f"<h1>Error loading data</h1><p>{str(e)}</p><p>Please refresh the page.</p>", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
