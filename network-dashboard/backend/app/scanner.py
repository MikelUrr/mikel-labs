"""Network scanner module using Nmap.

Performs multi-method scans and updates/inserts results into the database.

Author: Mikel Urrestarazu
Julio 2025
"""

from datetime import datetime
from typing import Dict, List

import nmap

from app.database import insertar_o_actualizar_dispositivo


def escanear_red_nmap(method_args: str, target_range: str = "192.168.1.0/24") -> List[Dict]:
    """Runs a network scan using Nmap with given arguments.

    Args:
        method_args (str): Nmap arguments (e.g. "-sS -Pn").
        target_range (str): Target IP range to scan.

    Returns:
        List[Dict]: List of discovered hosts with relevant data.
    """
    nm = nmap.PortScanner()
    print(f"Ejecutando: nmap {method_args} {target_range}")

    try:
        nm.scan(hosts=target_range, arguments=method_args)
    except nmap.PortScannerError as exc:
        print(f"Error en escaneo con {method_args}: {exc}")
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

        if "addresses" in nm[host] and "mac" in nm[host]["addresses"]:
            host_info["mac"] = nm[host]["addresses"]["mac"]
        if "vendor" in nm[host] and nm[host]["vendor"]:
            host_info["vendor"] = list(nm[host]["vendor"].values())[0]

        if "tcp" in nm[host]:
            for port, portdata in nm[host]["tcp"].items():
                host_info["puertos"].append({
                    "puerto": port,
                    "estado": portdata["state"],
                    "servicio": portdata.get("name"),
                    "producto": portdata.get("product", "")
                })

        tiene_puertos = bool(host_info["puertos"])
        tiene_hostname = bool(host_info["hostname"])
        tiene_mac = bool(host_info["mac"])

        if tiene_puertos or tiene_hostname or tiene_mac:
            resultados.append(host_info)

    return resultados


def escaneo_completo() -> None:
    """Performs a full network scan using multiple Nmap techniques and updates the database."""
    metodos = [
        "-sn",
        "-sS -Pn",
        "-Pn -sP"
    ]

    resultados_totales: List[Dict] = []
    for metodo in metodos:
        resultado = escanear_red_nmap(metodo)
        resultados_totales.extend(resultado)

    # Eliminar duplicados por IP (última coincidencia prevalece)
    vistos: Dict[str, Dict] = {}
    for r in resultados_totales:
        vistos[r["ip"]] = r

    resultados_finales = list(vistos.values())

    for dispositivo in resultados_finales:
        insertar_o_actualizar_dispositivo(dispositivo)

    print(f"Escaneo completo. {len(resultados_finales)} dispositivos activos detectados.")
