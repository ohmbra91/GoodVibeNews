import requests
import aiohttp
import asyncio
import tqdm  # Progress bar support
# List of proxies
proxies = [
    "http://142.93.202.130:3128",
    "http://183.240.196.53:38080",
    "http://106.42.30.243:82",
    "http://67.43.227.228:18527",
    "http://113.108.13.120:8083",
    "http://103.152.112.120:80",
    "http://123.16.38.27:8118",
    "http://87.248.129.32:80",
    "http://183.234.215.11:8443",
    "http://2.56.179.115:3128",
    "http://72.10.160.170:22485",
    "http://218.13.39.150:9091",
    "http://5.35.80.72:80",
    "http://135.181.193.128:3128",
    "http://119.3.113.152:9094",
    "http://195.200.28.26:8888",
    "http://103.152.112.186:80",
    "http://190.103.177.131:80",
    "http://135.181.154.225:80",
    "http://221.231.13.198:1080",
    "http://72.10.160.170:25001",
    "http://67.43.236.18:17791",
    "http://5.58.25.124:8080",
    "http://103.25.81.116:8080",
    "http://159.65.230.46:8888",
    "http://118.113.246.10:2324",
    "http://16.78.119.130:443",
    "http://40.129.203.4:8080",
    "http://189.22.234.37:80",
    "http://45.94.73.165:8080",
    "http://152.26.229.52:9443",
    "http://38.52.221.188:999",
    "http://203.89.8.107:80",
    "http://207.180.248.212:3000",
    "http://72.10.164.178:16199",
    "http://103.171.245.137:1080",
    "http://190.60.36.210:999",
    "http://103.247.20.106:1111",
    "http://62.33.53.248:3128",
    "http://149.86.203.217:8080",
    "http://49.70.190.251:2324",
    "http://62.84.245.79:80",
    "http://103.227.187.9:6080",
    "http://59.53.80.122:10024",
    "http://114.80.37.199:3081",
    "http://190.61.61.156:999",
    "http://72.240.9.63:80",
    "http://103.126.86.29:9090",
    "http://8.220.204.215:8080",
    "http://117.81.238.92:8089",
    "http://178.130.43.7:1023",
    "http://88.83.203.237:8080",
    "http://67.43.228.250:14541",
    "http://49.49.208.152:8080",
    "http://5.106.6.235:80",
    "http://170.84.233.10:61337",
    "http://36.64.10.162:8080",
    "http://119.95.189.247:8080",
    "http://200.233.147.14:3128",
    "http://85.214.195.118:80",
    "http://168.195.203.254:999",
    "http://89.38.129.15:3128",
    "http://103.242.106.119:8080",
    "http://201.77.98.131:999"
]

# URL to test
test_url = "http://www.google.com"

def check_proxy(proxy):
    try:
        response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            print(f"✅ Good Proxy: {proxy}")
            return proxy
        else:
            print(f"❌ Bad Proxy: {proxy} - Status Code: {response.status_code}")
    except requests.RequestException:
        print(f"❌ Failed Proxy: {proxy}")

# Check all proxies
working_proxies = [proxy for proxy in proxies if check_proxy(proxy)]

print("\n🟢 Working Proxies:", working_proxies)