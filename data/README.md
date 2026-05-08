# Carpeta `data/` — Datos del Proyecto

Esta carpeta contiene **todos los datos del proyecto**, tanto los descargados de fuentes externas como los generados por los notebooks de procesamiento.

> **Importante:** ninguno de los ficheros de esta carpeta se sube al repositorio Git. Están excluidos vía `.gitignore` por dos motivos: el tamaño (la carpeta supera los 700 MB) y los términos de uso de Inside Airbnb que prohíben redistribuir sus datos.

---

## Estructura

```
data/
├── raw/                            # Datos originales descargados de fuentes externas
│   ├── listings.csv                ← Inside Airbnb (descarga manual)
│   ├── calendar.csv                ← Inside Airbnb (descarga manual)
│   ├── clima_barcelona.csv         ← Open-Meteo API (genera notebook 01)
│   └── eventos_barcelona.csv       ← Ticketmaster API (genera notebook 01)
│
├── processed/                      # Datos limpios e integrados (generados por notebooks)
│   ├── listings_clean.csv          ← genera notebook 03
│   ├── calendar_clean.csv          ← genera notebook 03
│   ├── clima_clean.csv             ← genera notebook 03
│   ├── eventos_clean.csv           ← genera notebook 03
│   ├── dataset_integrado.csv       ← genera notebook 04 (entrada principal del modelo)
│   ├── train.csv                   ← genera orange/preparar_dataset_orange.py
│   └── test.csv                    ← genera orange/preparar_dataset_orange.py
│
└── README.md                       # Este documento
```

---

## `data/raw/` — Datos originales (no modificar)

Son los datos sin transformar tal como vienen de las fuentes externas. **Nunca se editan a mano** para mantener trazabilidad de la cadena de procesamiento.

### `listings.csv` — Catálogo de pisos de Inside Airbnb

| Atributo | Valor |
|---|---|
| Fuente | https://insideairbnb.com/get-the-data/ → Barcelona |
| Tipo | CSV (descargado y descomprimido del `.gz` original) |
| Tamaño aproximado | 38 MB |
| Filas | 18.172 (un piso por fila) |
| Columnas | 75 |
| Fecha scrape | 14 de diciembre de 2025 |
| Cómo se obtiene | Descarga manual desde la web de Inside Airbnb |

Contiene una fila por cada apartamento turístico activo en Barcelona en el momento del scrape, con todos sus atributos públicos: ubicación (`neighbourhood_cleansed`, `latitude`, `longitude`), tipo de alojamiento (`room_type`, `property_type`), capacidad (`accommodates`, `bedrooms`, `bathrooms`, `beds`), reputación (`number_of_reviews`, `review_scores_*`) e información del anfitrión (`host_id`, `host_is_superhost`). **La columna `price` está 100 % vacía** desde finales de 2024 por restricciones legales — este hallazgo motivó el pivot del proyecto desde Predictor de Precio hacia Predictor de Ocupación.

### `calendar.csv` — Calendario de disponibilidad de Inside Airbnb

| Atributo | Valor |
|---|---|
| Fuente | https://insideairbnb.com/get-the-data/ → Barcelona |
| Tipo | CSV (descargado y descomprimido del `.gz` original) |
| Tamaño aproximado | 241 MB |
| Filas | ~5,3 millones (un piso × un día) |
| Columnas | 7 |
| Fecha scrape | 14 de diciembre de 2025 |
| Horizonte | 365 días posteriores al scrape |
| Cómo se obtiene | Descarga manual desde la web de Inside Airbnb |

Contiene una fila por cada combinación `(listing_id, date)` indicando si esa noche está disponible (`available='t'`) o no (`available='f'`). La columna `available` es la base de la **variable objetivo** del modelo (`occupied = (available == 'f')`).

### `clima_barcelona.csv` — Datos meteorológicos diarios de Barcelona

| Atributo | Valor |
|---|---|
| Fuente | https://open-meteo.com (API gratuita, licencia CC BY 4.0) |
| Tipo | CSV |
| Tamaño aproximado | 18 KB |
| Filas | ~400 (uno por día) |
| Columnas | 7 |
| Cómo se obtiene | Lo genera automáticamente el notebook `01_descarga_datos.ipynb` |

Contiene la serie diaria de temperatura máxima/mínima/media, precipitación acumulada, velocidad del viento máxima y código meteorológico WMO. Para los días futuros que no tienen datos observados (Open-Meteo solo dispone de datos hasta ~5 días atrás), el notebook 01 sustituye con la **climatología del año anterior**, marcando explícitamente el origen en la columna `fuente` (`observado` o `climatologia`).

### `eventos_barcelona.csv` — Eventos culturales y deportivos

| Atributo | Valor |
|---|---|
| Fuente | https://developer.ticketmaster.com (Discovery API v2) |
| Tipo | CSV |
| Tamaño aproximado | 100 KB |
| Filas | ~1.000 (uno por evento) |
| Columnas | 8 |
| Cómo se obtiene | Lo genera automáticamente el notebook `01_descarga_datos.ipynb` |

Contiene los eventos del área metropolitana de Barcelona. **No se integra finalmente en el dataset modelado** porque el horizonte de eventos disponibles (Abr-Jul 2026) no se solapa con el horizonte del modelo (Dic 2025-Feb 2026). Se mantiene como fichero auxiliar para referencia y posible uso futuro.

---

## `data/processed/` — Datos limpios e integrados

Son los ficheros que generan los notebooks `03_limpieza.ipynb`, `04_integracion.ipynb` y el script `orange/preparar_dataset_orange.py`. Se pueden borrar y regenerar en cualquier momento ejecutando los notebooks/scripts en orden.

### Outputs del notebook 03 — Limpieza por fuente

| Fichero | Tamaño | Filas | Columnas | Descripción |
|---|---|---|---|---|
| `listings_clean.csv` | 3 MB | 18.172 | 25 | Listings con columnas filtradas, booleanos convertidos a 1/0 e imputación de nulos por mediana de barrio. |
| `calendar_clean.csv` | 48 MB | ~1 M | 11 | Calendario filtrado al horizonte de 8 semanas (14/12/2025 → 07/02/2026) con la variable target `occupied` y features temporales (`dow`, `is_weekend`, `month`, `day`, `week`, `is_holiday`). |
| `clima_clean.csv` | 3 KB | 56 | 10 | Clima diario con `weather_cat` (categoría: soleado, nublado, lluvia, extremo) y `temp_avg`. |
| `eventos_clean.csv` | 2 KB | ~50 | 5 | Eventos agregados a nivel día. Tabla auxiliar (no se integra en el modelo). |

### Output del notebook 04 — Dataset integrado

| Fichero | Tamaño | Filas | Columnas | Descripción |
|---|---|---|---|---|
| `dataset_integrado.csv` | 227 MB | 1.012.783 | 40 | Join `calendar_clean ⟕ listings_clean ⟕ clima_clean` a granularidad **listing × día**. Cero nulos. **Es la entrada principal del notebook 05 (modelado), del script de Orange y de la subida a BigQuery.** |

### Outputs del script `orange/preparar_dataset_orange.py`

| Fichero | Tamaño | Filas | Columnas | Descripción |
|---|---|---|---|---|
| `train.csv` | 145 MB | 758.375 | 56 | Primeros 42 días del horizonte. Feature engineering ya aplicado: target encodings (`neigh_enc`, `listing_te`), one-hot, drop de columnas con leakage. Listo para Orange. |
| `test.csv` | 48 MB | 254.408 | 56 | Últimos 14 días del horizonte. Mismas columnas que `train.csv` para alineamiento. |

---

## Cómo regenerar todo desde cero

Si se borra cualquier fichero de `data/processed/` (o si se descarga un nuevo scrape de Inside Airbnb), basta con:

1. **Asegurar que existen los inputs en `data/raw/`:**
   - `listings.csv` y `calendar.csv` descargados manualmente desde Inside Airbnb.
   - `.env` configurado con `TICKETMASTER_API_KEY`.

2. **Ejecutar los notebooks en orden** (desde `notebooks/`):

   ```
   01_descarga_datos.ipynb    # ~2 min — genera clima y eventos en data/raw/
   02_exploracion.ipynb       # ~1 min — EDA, no genera ficheros nuevos
   03_limpieza.ipynb          # ~1 min — genera los 4 ficheros *_clean.csv
   04_integracion.ipynb       # ~1 min — genera dataset_integrado.csv
   05_modelado.ipynb          # ~5-10 min — entrena modelos sklearn
   ```

3. **Generar los CSV para Orange** (opcional, solo si se va a usar el flujo visual):

   ```bash
   python orange/preparar_dataset_orange.py
   ```

   Genera `train.csv` y `test.csv` en `data/processed/`.

4. **Subir a BigQuery** (opcional, solo si se va a usar Power BI):

   ```bash
   python sql/subir_dataset.py
   ```

   Carga `dataset_integrado.csv` en `price-optimizer-bcn.datos.fact_ocupacion`.

---

## Privacidad, licencias y exclusión de Git

- **Inside Airbnb**: los datos son públicos y se publican bajo licencia `CC BY 4.0`, pero los términos de uso piden **no redistribuir los CSV originales**. Por eso `data/raw/listings.csv` y `data/raw/calendar.csv` están en `.gitignore`. Cualquier persona que clone el repo debe descargarlos manualmente desde la web oficial.
- **Open-Meteo**: licencia `CC BY 4.0`, redistribución permitida con atribución.
- **Ticketmaster**: los datos descargados están sujetos a los términos de uso de la API; no se redistribuyen.
- **Datos derivados (`processed/`)**: son ficheros generados por código del repositorio. Se podrían subir desde el punto de vista legal (son agregaciones), pero se excluyen también por tamaño (~700 MB sumando todos los procesados).
s