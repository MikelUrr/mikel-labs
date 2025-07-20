import subprocess
import json
import re
import socket
from datetime import datetime

import socket

def obtener_rango_automatico():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No se conecta realmente, solo fuerza la detección de IP local real
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
    except Exception:
        ip_local = "127.0.0.1"
    finally:
        s.close()

    partes = ip_local.split(".")
    return f"{partes[0]}.{partes[1]}.{partes[2]}.0/24"

def escanear_red(con_rango=None):
    if not con_rango:
        con_rango = obtener_rango_automatico()

    try:
        print(f"Escaneando red en rango: {con_rango}")
        resultado = subprocess.check_output(["nmap", "-sn", con_rango], text=True)
    except subprocess.CalledProcessError as e:
        print("Error ejecutando nmap:", e)
        return []

    dispositivos = []
    ip = mac = hostname = vendor = None

    for linea in resultado.splitlines():
        if linea.startswith("Nmap scan report for"):
            mac = vendor = hostname = None
            partes = linea.split("for")[-1].strip()
            if "(" in partes and ")" in partes:
                try:
                    hostname, ip = re.match(r"(.+)\s+\(([\d.]+)\)", partes).groups()
                except:
                    hostname = None
                    ip = partes
            else:
                hostname = None
                ip = partes
        elif "MAC Address:" in linea:
            mac_info = re.search(r"MAC Address: ([\w:]+) \((.*?)\)", linea)
            if mac_info:
                mac = mac_info.group(1)
                vendor = mac_info.group(2)

        if ip and (mac or "MAC Address:" not in linea):
            dispositivos.append({
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
                "hostname": hostname,
                "detectado": datetime.now().isoformat()
            })
            ip = mac = hostname = vendor = None

    return dispositivos

if __name__ == "__main__":
    dispositivos = escanear_red()

    print(json.dumps(dispositivos, indent=2, ensure_ascii=False))

    with open("dispositivos_nmap.json", "w", encoding="utf-8") as f:
        json.dump(dispositivos, f, indent=2, ensure_ascii=False)
