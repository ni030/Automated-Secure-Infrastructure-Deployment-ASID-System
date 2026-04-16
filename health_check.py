import requests
import os

TARGET_URL = "http://172.20.10.3"

def check_http():
    try:
        res = requests.get(TARGET_URL, timeout=3)
        return res.status_code == 200
    except:
        return False

def check_container():
    result = os.system("docker ps | grep myapp > /dev/null")
    return result == 0

def check_app():
    http_ok = check_http()
    container_ok = check_container()

    print(f"HTTP check: {http_ok}")
    print(f"Container check: {container_ok}")

    return http_ok and container_ok