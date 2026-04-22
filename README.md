# Optimizador de Precios para Apartamentos Turísticos en Barcelona

Proyecto Final de Especialidad — Big Data e IA | IFP España

Modelo de predicción del precio óptimo por noche para apartamentos turísticos en Barcelona, cruzando datos históricos de Airbnb con clima local (Open-Meteo) y eventos (Ticketmaster API).

---

## Stack tecnológico

| Herramienta | Uso |
|---|---|
| Python 3.12 (pandas, matplotlib) | Limpieza, EDA e integración de datos |
| Google BigQuery | Almacenamiento y consultas SQL a escala |
| Orange Data Mining | Pipeline visual de Machine Learning |
| Power BI | Dashboard interactivo de resultados |

---

## Estructura del proyecto

```
price-optimazer-guiris/
│
├── data/                        # Datasets (no subidos al repo, ver abajo)
│   ├── raw/                     # Datos originales sin procesar
│   └── processed/               # Datos limpios e integrados
│
├── notebooks/                   # Jupyter Notebooks de análisis
│   ├── 01_exploracion.ipynb
│   ├── 02_limpieza.ipynb
│   └── 03_integracion.ipynb
│
├── orange/                      # Flujos de trabajo de Orange Data Mining (.ows)
│
├── powerbi/                     # Fichero .pbix del dashboard
│
├── sql/                         # Consultas BigQuery (.sql)
│
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Configuración del entorno

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/price-optimazer-guiris.git
cd price-optimazer-guiris
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar credenciales de Google BigQuery

1. Descarga tu fichero de clave JSON desde Google Cloud Console (IAM → Cuentas de servicio).
2. Guárdalo en la raíz del proyecto como `credentials.json` (está en `.gitignore`, nunca se sube al repo).
3. Crea un fichero `.env` basándote en `.env.example`:

```bash
cp .env.example .env
```

Contenido del `.env`:
```
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
BIGQUERY_PROJECT_ID=price-optimizer-bcn
```

---

## Fuentes de datos

Los datos **no se incluyen en el repositorio** por su tamaño. Descárgalos manualmente y colócalos en `data/raw/`:

| Dataset | URL | Ficheros necesarios |
|---|---|---|
| Inside Airbnb — Barcelona | http://insideairbnb.com/barcelona | `listings.csv`, `calendar.csv` | (14/12/2025)
| Open-Meteo | https://open-meteo.com | Se descarga vía API (ver `notebooks/01_exploracion.ipynb`) |
| Ticketmaster | https://developer.ticketmaster.com | Se descarga vía API |

---

## Metodología

Se aplica **CRISP-DM** (Cross-Industry Standard Process for Data Mining):

1. Comprensión del negocio
2. Comprensión de los datos
3. Preparación de los datos
4. Modelado
5. Evaluación
6. Despliegue

---

## Autor

Dasbits — Curso Big Data e IA, IFP España (2025-2026)
