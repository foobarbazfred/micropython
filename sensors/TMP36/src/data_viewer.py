import socket
import machine
import time
from machine import ADC, Pin


#
# TMP sensor driver
#
SENSER_PIN=26
temp_sensor = ADC(Pin(SENSER_PIN))

CONST_A = 107.14285714285715
CONST_B = -57.14285714285717

def conv_volt_to_temp(vol):
    return CONST_A * vol  + CONST_B

def get_temperature(sensor):
    vol = 3.3 * sensor.read_u16() / 65535
    return conv_volt_to_temp(vol)

#
#
#

TOP_HTML = """<!DOCTYPE html>
<html>
    <head> <title>Temperature</title> </head>
    <body>
        <h1>Temperature Measurement Service</h1>
        <table border="1"> 
            <tr><th>Time</th><th>Temperature</th></tr>
            <tr><td>%s</td><td>%s</td></tr>
        </table>
        <ur>
         <li><a href='/viewer.html'>Temperature Viewer</a>
         <li><a href='/raw_temp'>Raw Temperature</a>
        </ur>
    </body>
</html>
"""


DATA_VIEWER_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <h3>Temperature Monitor</h3>
  <canvas id="chart" width="600" height="300"></canvas>

  <script>
    const ENDPOINT = '__ENDPOINT__';

    const chart = new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels: [], datasets: [{ label: 'temp(C)', data: [] }] },
      options: { animation: false }
    });

    async function fetchTemperature() {
      try {
        const response = await fetch(ENDPOINT);
        const text = await response.text();
        const temp = parseFloat(text);
        if (isNaN(temp)) return;

        chart.data.labels.push(new Date().toLocaleTimeString());
        chart.data.datasets[0].data.push(temp);
        if (chart.data.labels.length > 100) {
          chart.data.labels.shift();
          chart.data.datasets[0].data.shift();
        }
        chart.update();
      } catch (e) {
        console.error('fetch error:', e);
      }
    }
    setInterval(fetchTemperature, 5000);
  </script>
</body>
</html>
'''

LISTEN_PORT=1880
WIFI_ADDR = sta.ifconfig()[0]     # variable sta  is set in  boot.py , that is instance of WiFi station
ACCESS_URL = f'http://{WIFI_ADDR}:{LISTEN_PORT}'
RAW_VALUE_ENDPOINT = f'{ACCESS_URL}/raw_temp'

addr = socket.getaddrinfo('0.0.0.0', LISTEN_PORT)[0][-1]



s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

def receive_request(cl):
    cl.settimeout(3.0)
    request = b''
    while b'\r\n\r\n' not in request:
        try:
            chunk = cl.recv(1024)
        except OSError:
            cl.close()
            break
        if not chunk:
            # disconnected from client
            break
        request += chunk
        if len(request) > 8192:  # for safety too large
            break
    header_part, _, rest = request.partition(b'\r\n\r\n')
    return header_part, rest 
    

def parse_path(request):
   print('parse_path', request)
   method,path,http_version = request.split(' ')
   return method, path, http_version

#
# Web Server main routine
#
while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    header_bytes, rest_bytes = receive_request(cl)
    print('--received--------------')
    print(header_bytes)
    print(rest_bytes)
    print('----------------')
    header = header_bytes.decode().split('\r\n')
    if header[0] == '':
        continue
    method, path, _ = parse_path(header[0])
    print('----parsed request-----')
    print(method,path)

    #rows = ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pins]
    temperature = get_temperature(temp_sensor)

    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n')
    cl.send('Access-Control-Allow-Origin: *\r\n')
    cl.send('\r\n')

    if  '/raw_temp' in path:
        response_body = str(temperature)

    elif  '/viewer.html' in path:
        response_body = DATA_VIEWER_HTML.replace('__ENDPOINT__',RAW_VALUE_ENDPOINT)
    else:
        response_body = TOP_HTML % ('00:00:00', '\n'.join(str(temperature)))
    cl.send(response_body)
    cl.close()


