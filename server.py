from flask import Flask, jsonify, render_template_string
import serial, threading, json, time

app = Flask(__name__)

# ← Change this to your port
PORT = "/dev/cu.usbmodem146201"
BAUD = 9600

latest = {"temp": 0, "hum": 0, "status": "NORMAL"}
history = []

def read_serial():
    global latest, history
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(2)
        while True:
            line = ser.readline().decode("utf-8").strip()
            if line.startswith("{"):
                data = json.loads(line)
                latest = data
                history.append(data["temp"])
                if len(history) > 20:
                    history.pop(0)
    except Exception as e:
        print("Serial error:", e)

thread = threading.Thread(target=read_serial, daemon=True)
thread.start()

@app.route("/data")
def data():
    return jsonify({**latest, "history": history})

@app.route("/")
def index():
    return render_template_string(HTML)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Arduino Dashboard</title>
  <meta charset="UTF-8">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#17252A; font-family:Calibri,sans-serif; color:white; padding:20px; }
    h1 { color:#00979D; text-align:center; margin-bottom:20px; font-size:28px; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; max-width:800px; margin:0 auto 20px; }
    .card { background:#1E3040; border-radius:10px; padding:24px; text-align:center; border-top:4px solid #00979D; }
    .card.warn { border-color:#E5A013; }
    .card.alert { border-color:#CC0000; animation:pulse 0.5s infinite alternate; }
    @keyframes pulse { from{opacity:1} to{opacity:0.6} }
    .val { font-size:48px; font-weight:bold; color:white; }
    .label { font-size:13px; color:#7799AA; margin-top:8px; }
    .sub { font-size:12px; margin-top:4px; }
    .sub.green { color:#00979D; }
    .sub.yellow { color:#E5A013; }
    .sub.red { color:#CC0000; }
    #status-card { grid-column: span 2; border-top:4px solid #00AA44; }
    #status-card.warn { border-color:#E5A013; }
    #status-card.alert { border-color:#CC0000; }
    #status-val { font-size:36px; font-weight:bold; }
    .chart-box { max-width:800px; margin:0 auto; background:#1E3040; border-radius:10px; padding:20px; }
    canvas { width:100% !important; }
    .log { max-width:800px; margin:16px auto; background:#0C1520; border-radius:10px; padding:16px; font-family:monospace; font-size:13px; height:160px; overflow-y:auto; }
    .log p { margin:2px 0; }
    .log .n { color:#00CC66; }
    .log .w { color:#E5A013; }
    .log .a { color:#FF4444; }
    .monitor-bar { max-width:800px; margin:0 auto 8px; background:#1C1C1C; border-radius:8px 8px 0 0; padding:8px 16px; font-family:monospace; font-size:12px; color:#666; display:flex; justify-content:space-between; }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <h1>🌡 Arduino Temperature Dashboard</h1>

  <div class="grid">
    <div class="card" id="temp-card">
      <div class="val" id="temp-val">--</div>
      <div class="label">Current Temperature</div>
      <div class="sub green" id="temp-sub">Reading...</div>
    </div>
    <div class="card" id="hum-card">
      <div class="val" id="hum-val">--</div>
      <div class="label">Humidity</div>
      <div class="sub green">Normal range</div>
    </div>
    <div class="card" id="status-card">
      <div id="status-val">--</div>
      <div class="label">System Status</div>
    </div>
  </div>

  <div class="chart-box">
    <canvas id="myChart" height="80"></canvas>
  </div>

  <div class="monitor-bar">
    <span>⬤ ⬤ ⬤ &nbsp; Serial Monitor</span>
    <span>9600 baud</span>
  </div>
  <div class="log" id="log"></div>

  <script>
    const ctx = document.getElementById('myChart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Temperature °C',
          data: [],
          borderColor: '#00979D',
          backgroundColor: 'rgba(0,151,157,0.1)',
          borderWidth: 2.5,
          pointRadius: 4,
          tension: 0.4,
          fill: true
        },{
          label: 'Threshold 31°C',
          data: [],
          borderColor: '#CC0000',
          borderWidth: 1.5,
          borderDash: [6,3],
          pointRadius: 0,
          fill: false
        }]
      },
      options: {
        animation: false,
        scales: {
          y: { min:15, max:45, grid:{color:'#1E3040'}, ticks:{color:'#7799AA'} },
          x: { grid:{color:'#1E3040'}, ticks:{color:'#7799AA'} }
        },
        plugins: { legend:{ labels:{ color:'#AAAAAA' } } }
      }
    });

    let tick = 0;
    const log = document.getElementById('log');

    function addLog(msg, cls) {
      const p = document.createElement('p');
      p.className = cls;
      p.textContent = new Date().toLocaleTimeString() + '  ' + msg;
      log.appendChild(p);
      log.scrollTop = log.scrollHeight;
      if (log.children.length > 50) log.removeChild(log.firstChild);
    }

    function update() {
      fetch('/data').then(r => r.json()).then(d => {
        // Temp card
        document.getElementById('temp-val').textContent = d.temp + '°C';
        const ts = document.getElementById('temp-sub');
        const tc = document.getElementById('temp-card');
        const sc = document.getElementById('status-card');
        const sv = document.getElementById('status-val');

        if (d.status === 'NORMAL') {
          tc.className = 'card'; ts.className = 'sub green'; ts.textContent = 'Below threshold';
          sc.className = 'card'; sc.style.borderColor = '#00AA44'; sv.style.color = '#00AA44';
        } else if (d.status === 'WARM') {
          tc.className = 'card warn'; ts.className = 'sub yellow'; ts.textContent = 'Getting warm!';
          sc.className = 'card warn'; sv.style.color = '#E5A013';
        } else {
          tc.className = 'card alert'; ts.className = 'sub red'; ts.textContent = '⚠ Above threshold!';
          sc.className = 'card alert'; sv.style.color = '#FF4444';
        }

        document.getElementById('hum-val').textContent = d.hum + '%';
        sv.textContent = d.status;

        // Chart
        const label = tick + 's';
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(d.temp);
        chart.data.datasets[1].data.push(31);
        if (chart.data.labels.length > 20) {
          chart.data.labels.shift();
          chart.data.datasets[0].data.shift();
          chart.data.datasets[1].data.shift();
        }
        chart.update();
        tick += 2;

        // Log
        const cls = d.status === 'NORMAL' ? 'n' : d.status === 'WARM' ? 'w' : 'a';
        addLog('Temp: ' + d.temp + '°C  |  Hum: ' + d.hum + '%  |  ' + d.status, cls);
      });
    }

    update();
    setInterval(update, 2000);
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("Dashboard running → open http://localhost:5000")
    app.run(debug=False)