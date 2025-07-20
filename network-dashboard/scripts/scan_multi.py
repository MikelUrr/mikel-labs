import subprocess
import json
import re
from datetime import datetime

def escanear_red_multiples_rangos(rangos):
    dispositivos = []

    for rango in rangos:
        try:
            print(f"🔍 Escaneando rango: {rango}")
            resultado = subprocess.check_output(["nmap", "-Pn", "-sn", rango], text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error ejecutando nmap en {rango}:", e)
            continue

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

    dispositivos_unicos = {d["ip"]: d for d in dispositivos}
    return list(dispositivos_unicos.values())


if __name__ == "__main__":
    rangos = [
        "192.168.1.0/24"
    
    ]

    dispositivos = escanear_red_multiples_rangos(rangos)

    print(json.dumps(dispositivos, indent=2, ensure_ascii=False))

    with open("dispositivos_multi_nmap.json", "w", encoding="utf-8") as f:
        json.dump(dispositivos, f, indent=2, ensure_ascii=False)
