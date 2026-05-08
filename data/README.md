# Carpeta de datos

Esta carpeta NO se sube al repositorio (ver .gitignore).
Descarga los datasets manualmente siguiendo las instrucciones del README principal.

## Estructura

```
data/
├── raw/          → Datos originales sin modificar (nunca tocar)
│   ├── listings.csv          ← Inside Airbnb (ya descargado)
│   ├── calendar.csv          ← Inside Airbnb (ya descargado)
│   ├── clima_barcelona.csv   ← Descargar via Open-Meteo API
│   └── eventos_barcelona.csv ← Descargar via Ticketmaster API
│
└── processed/    → Datos limpios generados por los notebooks
    └── dataset_integrado.csv ← Se genera en notebook 03
```

## Fuente y fecha de los datos actuales

| Fichero | Fuente | Fecha scrape |
|---|---|---|
| listings.csv | Inside Airbnb — Barcelona | 14 dic 2025 |
| calendar.csv | Inside Airbnb — Barcelona | 14 dic 2025 |
