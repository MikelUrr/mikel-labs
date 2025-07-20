import nmap
import os
import json
from datetime import datetime

def escanear_red_nmap(method_args, target_range="192.168.1.0/24"):
    nm = nmap.PortScanner()
    print(f"Ejecutando: nmap {method_args} {target_range}")
    try:
        nm.scan(hosts=target_range, arguments=method_args)
    except Exception as e:
        print(f"Error en escaneo con {method_args}: {e}")
        return []

    resultados = []
    for host in nm.all_hosts():
        host_info = {
            "ip": host,
            "estado": nm[host].state(),
            "hostname": nm[host].hostname(),
            "mac": None,
            "vendor": None,
            "puertos": [],
            "detectado": datetime.now().isoformat()
        }

        if 'addresses' in nm[host] and 'mac' in nm[host]['addresses']:
            host_info["mac"] = nm[host]['addresses']['mac']
        if 'vendor' in nm[host] and nm[host]['vendor']:
            host_info["vendor"] = list(nm[host]['vendor'].values())[0]

        if 'tcp' in nm[host]:
            for port, portdata in nm[host]['tcp'].items():
                host_info["puertos"].append({
                    "puerto": port,
                    "estado": portdata["state"],
                    "servicio": portdata.get("name"),
                    "producto": portdata.get("product")
                })

        # FILTRO: incluir solo si hay evidencia real de uso
        tiene_puertos = bool(host_info["puertos"])
        tiene_hostname = bool(host_info["hostname"])
        tiene_mac = bool(host_info["mac"])

        if tiene_puertos or tiene_hostname or tiene_mac:
            resultados.append(host_info)

    return resultados

def guardar_resultados_por_ip(resultados, carpeta="resultados_scan"):
    os.makedirs(carpeta, exist_ok=True)
    resumen = []

    for host_info in resultados:
        resumen.append(host_info)
        ip = host_info["ip"]
        ruta = os.path.join(carpeta, f"{ip}.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(host_info, f, indent=2, ensure_ascii=False)

    with open(os.path.join(carpeta, "resumen_general.json"), "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    metodos = [
        "-sn",
        "-sS -Pn",
        "-Pn -sP"
    ]

    resultados_totales = []
    for metodo in metodos:
        resultado = escanear_red_nmap(metodo)
        resultados_totales.extend(resultado)

    # Eliminar duplicados por IP
    vistos = {}
    for r in resultados_totales:
        vistos[r["ip"]] = r
    resultados_finales = list(vistos.values())

    guardar_resultados_por_ip(resultados_finales)
    print(f"Escaneo completo. {len(resultados_finales)} dispositivos activos detectados.")
