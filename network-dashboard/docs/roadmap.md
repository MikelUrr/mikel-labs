# 🗺️ Roadmap: Network Dashboard

Este archivo define las fases principales del proyecto, organizadas para poder desarrollarlo en bloques semanales y modulares.

---

## ✅ Fase 1 - Escaneo de dispositivos

- [ ] Detectar dispositivos conectados usando `nmap` o `arp`
- [ ] Extraer IP, MAC y nombre de host si es posible
- [ ] Guardar resultados en SQLite o JSON
- [ ] Comando para escaneo manual
- [ ] API REST para exponer el listado

---

## 🟡 Fase 2 - Monitorización periódica

- [ ] Hacer ping cada X segundos/minutos a IPs conocidas
- [ ] Detectar desconexiones/reconexiones
- [ ] Guardar histórico en la base de datos
- [ ] API para acceder a los estados

---

## 🟠 Fase 3 - Interfaz web

- [ ] Crear proyecto Vue 3 con Vite (mobile-first)
- [ ] Listado de dispositivos con estado en tiempo real (🟢🔴)
- [ ] Filtros por nombre, estado o IP
- [ ] Indicadores de tiempo desde última actividad

---

## 🔴 Fase 4 - Funcionalidades extra

- [ ] Gráficas horarias de actividad por dispositivo
- [ ] Botón de escaneo manual
- [ ] Exportar datos (CSV / JSON)
- [ ] Modo oscuro

---

## 💡 Ideas futuras

- [ ] Notificaciones por correo/Telegram ante desconexiones prolongadas
- [ ] Reconocimiento de dispositivos (vendor lookup por MAC)
- [ ] Test de velocidad y estado general de la red

---