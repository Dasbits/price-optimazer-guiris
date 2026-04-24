# Predictor de Ocupación para Apartamentos Turísticos en Barcelona

**Proyecto Final de Especialidad — Big Data e IA | IFP España**

Modelo de clasificación que predice si un apartamento turístico de Barcelona estará ocupado o libre un día concreto, cruzando datos de Inside Airbnb con clima local (Open-Meteo) y eventos (Ticketmaster).

> **Nota sobre el pivot del proyecto:** el enunciado inicial era predecir el **precio** óptimo por noche. Al analizar el dataset de Inside Airbnb de 14/12/2025 descubrimos que la columna `price` está 100 % vacía (Inside Airbnb dejó de publicarla), así que la variable objetivo se cambió a **ocupación** (binaria: `occupied = 1` si el día aparece como no disponible). Todo el stack y la metodología se mantienen.

---

## Stack tecnológico

| Herramienta | Uso |
|---|---|
| Python 3.12 (pandas, matplotlib, seaborn, scikit-learn) | Descarga, limpieza, EDA, integración y modelo baseline |
| Jupyter Notebook | Pipeline reproducible paso a paso |
| Google BigQuery | Almacenamiento cloud y consultas SQL |
| Orange Data Mining | Pipeline visual de Machine Learning (entrega final) |
| Power BI | Dashboard interactivo conectado a BigQuery |

---

## Estructura del proyecto

```
price-optimazer-guiris/
│
├── data/
│   ├── raw/                        # Datos originales (NO subidos al repo)
│   │   ├── listings.csv            ← Inside Airbnb
│   │   ├── calendar.csv            ← Inside Airbnb
│   │   ├── clima_barcelona.csv     ← Genera notebook 01
│   │   └── eventos_barcelona.csv   ← Genera notebook 01
│   └── processed/                  # Datos limpios (genera notebooks 03-04)
│       ├── listings_clean.csv
│       ├── calendar_clean.csv
│       ├── clima_clean.csv
│       ├── eventos_clean.csv
│       └── dataset_integrado.csv   ← Entrada del modelo y de Power BI
│
├── notebooks/
│   ├── 01_descarga_datos.ipynb     # Open-Meteo + Ticketmaster
│   ├── 02_exploracion.ipynb        # EDA
│   ├── 03_limpieza.ipynb           # Data Preparation
│   ├── 04_integracion.ipynb        # Join final listing × día
│   └── 05_modelado.ipynb           # Baseline sklearn (pendiente)
│
├── orange/                         # Flujos .ows
├── powerbi/                        # Dashboard .pbix
├── sql/                            # Consultas BigQuery
├── docs/                           # Entregables del curso (.docx)
│
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Configuración del entorno (una sola vez)

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/price-optimazer-guiris.git
cd price-optimazer-guiris
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Variables de entorno

Copia la plantilla y rellena las claves:

```bash
cp .env.example .env
```

Edita `.env` y ajusta los valores:

```
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
BIGQUERY_PROJECT_ID=price-optimizer-bcn
TICKETMASTER_API_KEY=tu_consumer_key_aqui
```

El fichero `.env` está en `.gitignore` y nunca se sube al repo.

---

## Obtención de datos y credenciales

### A — Datos de Inside Airbnb (manual)

Inside Airbnb ya no permite URLs directas a sus CSVs. Tienes que bajarlos desde la propia web:

1. Abre https://insideairbnb.com/get-the-data/
2. Busca la sección **Barcelona, Catalonia, Spain**.
3. Descarga los dos ficheros:
   - `listings.csv.gz` (detallado, no el "summary")
   - `calendar.csv.gz`
4. Descomprímelos (`.gz`) y colócalos en `data/raw/` con los nombres:
   - `data/raw/listings.csv`
   - `data/raw/calendar.csv`

Referencia de versión usada en este proyecto: **scrape del 14/12/2025**. Si bajas uno más nuevo funcionará igual; solo tendrás que actualizar `SCRAPE_DATE` en el notebook 03.

### B — Ticketmaster API Key (gratuita)

1. Entra en https://developer-acct.ticketmaster.com/user/login y crea una cuenta.
2. Ve a **My Apps → Create App** y rellena el formulario (nombre, descripción breve del proyecto académico).
3. En la pantalla de la app, copia el valor de **Consumer Key**.
4. Pégalo en tu `.env` como valor de `TICKETMASTER_API_KEY`.

Plan gratuito: 5000 llamadas/día, máx 200 eventos por página, máx 5 páginas por query. Suficiente de sobra para este proyecto.

### C — Google Cloud / BigQuery (gratuito dentro del free tier)

1. Entra en https://console.cloud.google.com con tu cuenta Google.
2. Crea un proyecto nuevo llamado `price-optimizer-bcn` (o el nombre que prefieras, ajusta después el `.env`).
3. En el buscador, busca **BigQuery API** y pulsa **Habilitar**.
4. Crea una cuenta de servicio:
   - Menú lateral → **IAM y administración → Cuentas de servicio → Crear cuenta de servicio**.
   - Nombre: `bigquery-client`.
   - Rol: **BigQuery Data Editor** + **BigQuery Job User**.
5. En la cuenta de servicio creada → pestaña **Claves → Añadir clave → Crear clave → JSON**.
6. Se descarga un fichero `.json`. Renómbralo a `credentials.json` y colócalo en la raíz del proyecto.

El free tier de BigQuery cubre 1 TB de queries/mes y 10 GB de almacenamiento; el dataset completo ocupa <500 MB.

### D — Open-Meteo

No necesita clave. La API es pública bajo licencia CC BY 4.0 y la consume el notebook 01 automáticamente.

---

## Orden de ejecución de los notebooks

Todos los notebooks se ejecutan desde la carpeta `notebooks/` en VS Code o Jupyter Lab. Ejecuta *Run All* en cada uno y espera a que termine antes de pasar al siguiente.

Cada sección lista los ficheros de **entrada** que el notebook espera encontrar y los de **salida** que genera. Si un input no existe o está en otra ruta, el notebook fallará en la primera celda de carga.

### 1. `01_descarga_datos.ipynb` · ~2 min

Descarga Open-Meteo y Ticketmaster y guarda los CSVs en `data/raw/`.

- **Inputs:**
  - `.env` en la raíz del repo con `TICKETMASTER_API_KEY` rellenada.
  - `data/raw/listings.csv` (Inside Airbnb, descarga manual — ver sección A).
  - `data/raw/calendar.csv` (Inside Airbnb, descarga manual — ver sección A).
- **Outputs:**
  - `data/raw/clima_barcelona.csv` (~400 filas × 7 columnas, con columna `fuente` = `observado` o `climatologia`).
  - `data/raw/eventos_barcelona.csv` (hasta 1000 filas × 8 columnas).

### 2. `02_exploracion.ipynb` · ~1 min

EDA completo (fase *Data Understanding* de CRISP-DM). No modifica los datos, solo genera gráficos y observaciones.

- **Inputs:**
  - `data/raw/listings.csv`
  - `data/raw/calendar.csv`
  - `data/raw/clima_barcelona.csv` (generado por el notebook 01).
  - `data/raw/eventos_barcelona.csv` (generado por el notebook 01).
- **Outputs:** ninguno en disco. Solo prints con volumen/nulos de cada dataset, histogramas, series temporales y correlaciones diarias.
- **Hallazgo clave a leer en la sección 2:** `available='f'` en Inside Airbnb mezcla *reservado* y *bloqueado por el anfitrión*. Por eso el modelo se limita a las primeras 8 semanas post-scrape (ver notebook 03).

### 3. `03_limpieza.ipynb` · ~1 min

Fase *Data Preparation*. Aplica limpieza, imputación y filtrado temporal.

- **Inputs:**
  - `data/raw/listings.csv`
  - `data/raw/calendar.csv`
  - `data/raw/clima_barcelona.csv`
  - `data/raw/eventos_barcelona.csv`
- **Outputs en `data/processed/`:**
  - `listings_clean.csv` — 18.172 × 25, 0 nulos.
  - `calendar_clean.csv` — ~1 M filas × 11, filtrado a 8 semanas desde 14/12/2025.
  - `clima_clean.csv` — 56 × 10, con `weather_cat` y `temp_avg`.
  - `eventos_clean.csv` — dataset auxiliar (no entra en el modelo por la limitación temporal de Ticketmaster, ver notebook para detalles).

### 4. `04_integracion.ipynb` · ~1 min

Join final `calendar ⟕ listings ⟕ clima` en granularidad listing × día.

- **Inputs (todos en `data/processed/`, generados por el notebook 03):**
  - `listings_clean.csv`
  - `calendar_clean.csv`
  - `clima_clean.csv`
- **Outputs:** `data/processed/dataset_integrado.csv` (~1 M filas × 42 columnas, ~190 MB, 0 nulos).

### 5. `05_modelado.ipynb` · ~5-10 min

Baseline de clasificación en scikit-learn (Logistic Regression, Random Forest, Gradient Boosting) antes del trabajo visual en Orange. Split train/test por fecha (42 días train, 14 días test).

- **Inputs:** `data/processed/dataset_integrado.csv` (generado por el notebook 04).
- **Outputs:** ninguno en disco. Prints con métricas (accuracy, F1, AUC), matriz de confusión, curvas ROC y top-20 de feature importance.
- **Nota anti-leakage:** el notebook excluye `availability_30/60/90/365` y `estimated_occupancy_l365d` por ser proxies directos del target (vienen del propio `calendar.csv`).

---

## Subida a BigQuery y uso en Power BI

Una vez tienes `dataset_integrado.csv`:

1. **Subir a BigQuery** (GUI o script):

   - GUI: BigQuery Studio → **Crear dataset** `datos` → **Crear tabla** `fact_ocupacion` → **Subir** el CSV con auto-detectar esquema.
   - Script: opcional, ver `sql/subir_dataset.py` (pendiente).

2. **Consultas SQL** de ejemplo (carpeta `sql/`):

   - `ocupacion_por_barrio.sql` — KPI por barrio.
   - `ocupacion_por_room_type.sql` — KPI por tipo de alojamiento.
   - `ocupacion_por_clima.sql` — efecto del tiempo sobre la ocupación.

3. **Power BI** → Obtener datos → **Google BigQuery** → autentícate con la cuenta Google → selecciona el proyecto y la tabla → carga → construye el dashboard.

---

## Metodología

Se aplica **CRISP-DM** (Cross-Industry Standard Process for Data Mining):

1. **Business Understanding** — documentado en `docs/entrega1_predictor_ocupacion_barcelona.docx`.
2. **Data Understanding** — notebook 02.
3. **Data Preparation** — notebooks 03 y 04.
4. **Modeling** — notebook 05 (sklearn) + Orange Data Mining.
5. **Evaluation** — métricas F1, AUC, matriz de confusión.
6. **Deployment** — dashboard en Power BI sobre BigQuery.

---

## Limitaciones conocidas

- **Ticketmaster** solo expone eventos futuros desde el momento de la llamada, por lo que no hay solapamiento con el horizonte del modelo (Dic 2025 – Feb 2026). La columna `n_eventos` no se integra en `dataset_integrado.csv`; se mantiene el fichero `eventos_clean.csv` como tabla auxiliar para BigQuery/Power BI.
- **Inside Airbnb** ya no publica la columna `price`, lo que forzó el pivot del proyecto de regresión (precio) a clasificación (ocupación).
- En `calendar.csv`, `available='f'` no distingue entre *reservado* y *bloqueado por el anfitrión*. Este es el motivo por el que el modelo se limita a 8 semanas desde la fecha del scrape, donde predomina la reserva real frente al bloqueo.
- Para las fechas del rango del proyecto posteriores a ~5 días antes de hoy, los datos de clima se sustituyen por climatología del año anterior (marcado en la columna `fuente` del CSV).

---

## Autor

**Dasbits** — Curso Big Data e IA, IFP España (2025-2026)
