# Predictor de Ocupación para Apartamentos Turísticos en Barcelona

> **Proyecto Final — Big Data e Inteligencia Artificial · IFP España (2025-2026)**
>
> **Repositorio:** https://github.com/Dasbits/price-optimazer-guiris

Modelo de clasificación binaria que predice si un apartamento turístico de Barcelona estará reservado o libre un día concreto, integrando datos de Inside Airbnb, clima (Open-Meteo) y eventos (Ticketmaster), almacenado en Google BigQuery y consumido por un dashboard interactivo en Power BI.

---

## Tabla de contenido

1. [Resumen / Abstract](#1-resumen--abstract)
2. [Introducción](#2-introducción)
3. [Desarrollo del proyecto](#3-desarrollo-del-proyecto-por-orden-cronológico-crisp-dm)
   - 3.1. [Business Understanding](#31-business-understanding--definición-del-problema-y-pivot-estratégico)
   - 3.2. [Data Understanding](#32-data-understanding--exploración-y-hallazgos-críticos)
   - 3.3. [Data Preparation](#33-data-preparation--limpieza-e-integración)
   - 3.4. [Modeling](#34-modeling--entrenamiento-de-tres-modelos-en-dos-plataformas)
   - 3.5. [Evaluation](#35-evaluation--métricas-y-comparativa-de-modelos)
   - 3.6. [Deployment](#36-deployment--bigquery--dashboard-power-bi)
4. [Conclusiones](#4-conclusiones)
5. [Bibliografía y referencias](#5-bibliografía-y-referencias)
6. [Anexos](#6-anexos)

---

## 1. Resumen / Abstract

Este proyecto desarrolla un sistema completo de predicción de ocupación para apartamentos turísticos de Airbnb en Barcelona siguiendo la metodología CRISP-DM en sus seis fases. La tarea es de **clasificación binaria supervisada**: predecir, para cada combinación piso-día, si esa noche estará reservada o bloqueada (`1`) o libre (`0`).

El proyecto se concibió originalmente como un Predictor de Precio Óptimo, pero durante la fase de Data Understanding se descubrió que la columna `price` del dataset Inside Airbnb está completamente vacía desde finales de 2024 por restricciones legales aplicadas por la plataforma. Esta limitación motivó un **pivot estratégico** desde la regresión sobre el precio hacia la clasificación sobre la ocupación, manteniendo intacto el resto del stack tecnológico, la metodología y los entregables.

El dataset final integra **cuatro fuentes heterogéneas** (Inside Airbnb, Open-Meteo, Ticketmaster, festivos catalanes) en una tabla de **1.012.783 filas × 40 columnas**, con granularidad listing × día sobre un horizonte de 56 días (14/12/2025 → 07/02/2026). Sobre este dataset se entrenan, validan y comparan tres modelos de clasificación binaria — **Logistic Regression, Random Forest y Gradient Boosting** — implementados en dos plataformas independientes: scikit-learn (programático) y Orange Data Mining (visual). El modelo ganador es **Random Forest con AUC = 0,895 y F1 = 0,812**, superando con holgura los umbrales mínimos del curso (F1 ≥ 0,75 y AUC ≥ 0,80). La fase de Deployment se materializa en la subida del dataset a **Google BigQuery** y la construcción de un **dashboard interactivo en Power BI Desktop** con tres páginas (Visión general, Mercado, Clima) conectado directamente a la nube.

---

## 2. Introducción

Barcelona es uno de los destinos turísticos más dinámicos de Europa, con un mercado de alquiler vacacional especialmente intenso desde la popularización de plataformas como Airbnb. Comprender los patrones de ocupación de los apartamentos turísticos tiene utilidad práctica para anfitriones independientes (anticipar baja demanda y ajustar precios), gestores profesionales (optimizar limpieza y operaciones), inversores inmobiliarios (estimar rentabilidad esperable) y reguladores municipales (informar políticas urbanísticas).

**Inside Airbnb** es un proyecto de open data que publica scrapes mensuales de los listings de Airbnb por ciudad. Aunque la información es pública, su explotación no es trivial: los datasets son grandes, las columnas relevantes cambian con el tiempo y la naturaleza de los datos (basada en disponibilidad declarada por el anfitrión, no en reservas reales) introduce ambigüedades semánticas que hay que conocer y documentar.

El presente proyecto aborda un caso de uso concreto sobre estos datos: construir un modelo de Machine Learning que prediga, para un piso dado y una fecha dada, si esa noche aparecerá como no disponible en el calendario público de Airbnb. La predicción se enriquece con información meteorológica diaria y con un cruce inicial con eventos culturales y deportivos del área metropolitana, persiguiendo capturar tanto los factores estructurales del listing (ubicación, capacidad, reputación) como los factores coyunturales del día (clima, calendario laboral, temporada turística).

El proyecto se desarrolla siguiendo la metodología estándar **CRISP-DM (Cross-Industry Standard Process for Data Mining)**, que estructura el ciclo de vida de un proyecto analítico en seis fases secuenciales pero iterativas, cada una con sus entregables identificables y reproducibles documentados en el repositorio público.

---

## 3. Desarrollo del proyecto (por orden cronológico, CRISP-DM)

### 3.1. Business Understanding — Definición del problema y pivot estratégico

El enunciado original del proyecto era construir un Predictor de Precio Óptimo para apartamentos turísticos de Barcelona. Tras descargar el scrape del 14 de diciembre de 2025 y realizar la exploración inicial se constató que la columna `price` estaba 100 % vacía en todos los registros, atribuible a restricciones legales aplicadas por Airbnb tras finales de 2024. Esta limitación hizo inviable la tarea de regresión sobre el precio.

Se evaluaron tres alternativas (descartar el dataset, buscar fuentes alternativas de pricing, o redefinir la tarea) y se optó por reformular el objetivo hacia un **Predictor de Ocupación**. La reformulación mantiene intacto el stack tecnológico, las fuentes de datos secundarias, la metodología CRISP-DM y los entregables académicos comprometidos. El cambio se documenta explícitamente en todos los READMEs y entregables previos.

**Variable objetivo definida:** `occupied` — vale 1 si la noche aparece en el calendar de Inside Airbnb con `available='f'` (no disponible) y 0 en caso contrario.

**Métricas de éxito acordadas:** F1-score ≥ 0,75 y AUC-ROC ≥ 0,80 sobre el conjunto de test.

### 3.2. Data Understanding — Exploración y hallazgos críticos

Notebook: `notebooks/02_exploracion.ipynb`.

Se realizó un EDA exhaustivo de las cuatro fuentes integradas:

- **Inside Airbnb (`listings.csv` + `calendar.csv`):** 18.172 listings de Barcelona, ~5,3 millones de filas de calendario sobre 365 días futuros.
- **Open-Meteo:** serie diaria de temperatura, precipitación y viento.
- **Ticketmaster Discovery API:** ~1.000 eventos del área metropolitana.
- **Festivos catalanes:** lista codificada manualmente.

**Tres hallazgos críticos documentados:**

1. **Columna `price` completamente vacía** → motivó el pivot del proyecto.
2. **Ambigüedad semántica de `available='f'`:** mezcla noches reservadas con noches bloqueadas voluntariamente por el anfitrión sin distinción. En barrios pequeños y residenciales el bloqueo manual contamina la señal de ocupación turística real, motivando la limitación del modelo a las primeras 8 semanas posteriores al scrape.
3. **Desfase temporal con Ticketmaster:** los eventos disponibles cubrían abril-julio 2026, sin solapamiento con el horizonte del modelo (diciembre 2025-febrero 2026). Decisión: dejar los eventos como tabla auxiliar pero no incorporarlos como feature.

### 3.3. Data Preparation — Limpieza e integración

Notebooks: `notebooks/03_limpieza.ipynb` y `notebooks/04_integracion.ipynb`.

**Limpieza por fuente:**

- Imputación de nulos en `bedrooms` y `bathrooms` por mediana de barrio.
- Conversión de booleanos textuales `t`/`f` a enteros `1`/`0`.
- Categorización del weathercode WMO en cuatro categorías (`soleado`, `nublado`, `lluvia`, `extremo`).
- Filtrado del calendario al horizonte de 56 días.
- Generación de variables temporales (`dow`, `is_weekend`, `month`, `day`, `week`, `is_holiday`).

**Integración:** join secuencial con pandas en granularidad listing × día. Resultado: `dataset_integrado.csv` con **1.012.783 filas × 40 columnas y cero nulos**.

### 3.4. Modeling — Entrenamiento de tres modelos en dos plataformas

Notebook: `notebooks/05_modelado.ipynb` (scikit-learn) y flujo paralelo en `orange/pipeline_ocupacion.ows` (Orange Data Mining).

**Estrategia de evaluación:** split por fecha (no aleatorio) para simular predicción real. Train = 758.375 filas (42 días), Test = 254.408 filas (14 días). El test cae intencionadamente fuera de la temporada navideña, añadiendo exigencia.

**Feature engineering avanzado:**

- **Eliminación de columnas con leakage:** `availability_30/60/90/365` y `estimated_occupancy_l365d` se descartan por ser proxies directos del target.
- **Target encoding:** `neigh_enc` (media de ocupación por barrio) y `listing_te` (media por listing), calculados solo con train para evitar leakage hacia test.
- **One-hot encoding:** de `room_type`, `property_type`, `weather_cat` y `neighbourhood_group_cleansed`.

**Tres modelos entrenados** (mismos hiperparámetros en sklearn y Orange):

- **Logistic Regression** (referencia lineal): Ridge L2, C = 1.
- **Random Forest** (ensemble por bagging): 200 árboles, max_depth = 15, min_samples_leaf = 5.
- **Gradient Boosting** (ensemble por boosting iterativo): 200 árboles, learning_rate = 0,10, max_depth = 5.

### 3.5. Evaluation — Métricas y comparativa de modelos

Métricas finales sobre el conjunto de test (254.408 filas):

| Modelo | AUC | F1 | Accuracy | MCC | Cumple umbral |
|---|---:|---:|---:|---:|:---:|
| Logistic Regression | 0,891 | 0,785 | 0,787 | 0,595 | Sí |
| **Random Forest (ganador)** | **0,895** | **0,812** | **0,812** | **0,627** | **Sí** |
| Gradient Boosting | 0,893 | 0,804 | 0,804 | 0,612 | Sí |

**Matriz de confusión del Random Forest:** 102.473 verdaderos negativos, 104.202 verdaderos positivos, 28.209 falsos positivos y 19.524 falsos negativos. Errores casi simétricos, indicando un modelo equilibrado.

**Curva ROC** (`orange/images/roc_analysis.png`): las tres curvas casi superpuestas en la esquina superior izquierda, lejos de la diagonal aleatoria. Capacidad discriminativa similar y muy alta en los tres modelos.

**Feature importance del Random Forest:** la variable más predictiva es `listing_te` (target encoding por listing) con importancia 0,66 sobre 1,0, capturando la popularidad histórica intrínseca de cada piso.

**Validación cruzada de implementación:** las métricas en sklearn y Orange son virtualmente idénticas para Random Forest y Gradient Boosting, confirmando la consistencia del pipeline en dos plataformas independientes.

### 3.6. Deployment — BigQuery + Dashboard Power BI

**Subida a Google BigQuery:** el script `sql/subir_dataset.py` carga el dataset_integrado.csv a la tabla `price-optimizer-bcn.datos.fact_ocupacion`. Free tier suficiente, conector nativo a Power BI, escalable sin migración.

**Tres queries SQL de KPI** (`sql/ocupacion_por_*.sql`): agregaciones por barrio (con doble segmento), por tipo de alojamiento (con efecto Navidad) y por clima (a nivel día para evitar contaminación con volumen).

**Dashboard Power BI** (`powerbi/dashboard_ocupacion.pbix`) con tres páginas interactivas:

- **Visión general:** KPIs (18.172 listings, 1M noches, 54,2 % ocupación, pico 76 %), serie temporal y ranking de distritos.
- **Mercado:** treemap por tipo de alojamiento, comparativa Navidad vs resto, top 10 barrios con slicer entre "Mercado completo" y "Solo pisos enteros".
- **Clima:** efecto del tiempo sobre la ocupación con nota didáctica sobre **confounding temporal** (la correlación lluvia-ocupación está mediada por la fecha de Navidad, no es causalidad directa).

---

## 4. Conclusiones

El proyecto demuestra que es posible construir un sistema completo de predicción de ocupación de apartamentos turísticos integrando múltiples fuentes de datos heterogéneas, aplicando técnicas modernas de Machine Learning, almacenando los resultados en infraestructura cloud y comunicándolos mediante un dashboard interactivo. **Las métricas finales (AUC = 0,895, F1 = 0,812) superan con holgura los umbrales del curso.**

La metodología CRISP-DM resultó clave: la separación entre Business Understanding y Data Understanding permitió detectar tempranamente el problema de la columna `price` vacía y reorientar el proyecto sin desperdiciar trabajo. El feature engineering — especialmente el target encoding por listing y la eliminación de columnas con leakage — fue determinante para alcanzar las métricas reportadas; el algoritmo elegido tuvo menos impacto que la calidad del preprocessing, como demuestra el hecho de que los tres modelos quedaran a menos de 0,03 puntos de F1 entre sí.

La duplicación intencional del pipeline de modelado en scikit-learn y Orange Data Mining no fue redundante: validó la consistencia de los resultados, expuso diferencias sutiles entre implementaciones (especialmente en Logistic Regression por el preprocessing automático de Orange) y produjo una herramienta accesible para audiencias no técnicas.

La feature más importante del modelo final, `listing_te`, es a la vez su mayor fortaleza y su mayor limitación: el modelo funciona excepcionalmente bien para listings con historial pero degradaría su rendimiento ante listings completamente nuevos (escenario de cold start), lo cual define la frontera de aplicabilidad del modelo y abre la línea de trabajo futuro más clara.

**Hallazgo no obvio para destacar:** el dashboard de Clima muestra que los días lluviosos tienen aparentemente mayor ocupación que los secos. No es causalidad sino **confounding temporal**: los días lluviosos del horizonte coinciden con la semana de Navidad, donde la demanda turística sube por motivos completamente independientes del tiempo. Es un buen ejemplo metodológico de que correlación no implica causalidad.

---

## 5. Bibliografía y referencias

### Fuentes de datos

- **Inside Airbnb.** http://insideairbnb.com/get-the-data/ — proyecto open data con scrapes mensuales de listings de Airbnb por ciudad. Scrape utilizado: Barcelona, 14/12/2025.
- **Open-Meteo.** https://open-meteo.com/en/docs/historical-weather-api — API gratuita de datos meteorológicos históricos con licencia CC BY 4.0.
- **Ticketmaster Discovery API.** https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/ — API gratuita de eventos.

### Documentación técnica

- **scikit-learn.** https://scikit-learn.org/stable/documentation.html
- **Orange Data Mining.** https://orangedatamining.com/docs/
- **Google BigQuery.** https://cloud.google.com/bigquery/docs
- **Power BI Desktop.** https://learn.microsoft.com/en-us/power-bi/
- **DAX.** https://learn.microsoft.com/en-us/dax/

### Metodología y conceptos

- Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* SPSS.
- Micci-Barreca, D. (2001). *A Preprocessing Scheme for High-Cardinality Categorical Attributes in Classification and Prediction Problems.* ACM SIGKDD Explorations.
- Breiman, L. (2001). *Random Forests.* Machine Learning, 45(1), 5-32.
- Friedman, J. H. (2001). *Greedy Function Approximation: A Gradient Boosting Machine.* The Annals of Statistics.

### Asistencia con IA

- Asistencia de **Claude (Anthropic)** para revisión de código, redacción de documentación y verificación metodológica del proyecto.

---

## 6. Anexos

### Estructura del repositorio

```
price-optimazer-guiris/
├── README.md                           # Este documento (manual de usuario)
├── requirements.txt                    # Dependencias Python
├── .env.example                        # Plantilla de variables de entorno
├── .gitignore
│
├── data/                               # Datos (excluidos de Git por tamaño/licencia)
│   ├── raw/                            # Datos originales descargados
│   ├── processed/                      # Datos limpios e integrados
│   └── README.md                       # Documentación de los datos
│
├── notebooks/                          # 5 notebooks Jupyter en orden de ejecución
│   ├── 01_descarga_datos.ipynb
│   ├── 02_exploracion.ipynb
│   ├── 03_limpieza.ipynb
│   ├── 04_integracion.ipynb
│   └── 05_modelado.ipynb
│
├── orange/                             # Pipeline visual de Machine Learning
│   ├── pipeline_ocupacion.ows
│   ├── preparar_dataset_orange.py
│   ├── images/                         # 5 capturas de evaluación
│   └── README.md
│
├── powerbi/                            # Dashboard interactivo
│   ├── dashboard_ocupacion.pbix
│   └── README.md
│
├── sql/                                # Queries y script de subida a BigQuery
│   ├── subir_dataset.py
│   ├── ocupacion_por_barrio.sql
│   ├── ocupacion_por_room_type.sql
│   └── ocupacion_por_clima.sql
│
└── docs/                               # Documentación académica
```

### Comandos para reproducir el proyecto

```bash
# 1. Clonar repositorio
git clone https://github.com/Dasbits/price-optimazer-guiris.git
cd price-optimazer-guiris

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows
pip install -r requirements.txt

# 3. Configurar credenciales
cp .env.example .env
# editar .env con TICKETMASTER_API_KEY, BIGQUERY_PROJECT_ID y GOOGLE_APPLICATION_CREDENTIALS

# 4. Descargar manualmente listings.csv y calendar.csv en data/raw/ desde Inside Airbnb

# 5. Ejecutar notebooks en orden
jupyter notebook notebooks/

# 6. Generar CSVs para Orange (opcional)
python orange/preparar_dataset_orange.py

# 7. Subir a BigQuery (opcional, requiere credenciales)
python sql/subir_dataset.py

# 8. Abrir orange/pipeline_ocupacion.ows con Orange Data Mining
# 9. Abrir powerbi/dashboard_ocupacion.pbix con Power BI Desktop
```

### Documentos de referencia complementarios

- **Memoria final completa:** `docs/memoria_final_predictor_ocupacion_barcelona.docx` (17 capítulos, ~40 páginas).
- **README detallado de Orange:** `orange/README.md` (configuración de widgets, lectura de matrices, explicación didáctica de la curva ROC).
- **README detallado de Power BI:** `powerbi/README.md` (datasets, medidas DAX, descripción visual a visual de las tres páginas).
- **Capturas de los resultados de Orange:** `orange/images/` (Test and Score, tres matrices de confusión, ROC).

---
