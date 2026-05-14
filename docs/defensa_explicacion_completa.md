# Explicación completa del proyecto — Predictor de Ocupación Barcelona

> Documento integrador para defender el proyecto: origen de los datos, fases del flujo, métricas, modelos y arquitectura cloud. Pensado para acompañar la defensa oral con un nivel de detalle medio, suficiente para responder a casi cualquier pregunta sin entrar en código.

---

## 1. ¿De dónde salen los datos?

El proyecto integra **cuatro fuentes externas** muy distintas entre sí. Combinar fuentes heterogéneas no es trivial: cada una tiene su propio formato, granularidad y limitaciones, y hacerlas convivir es uno de los puntos fuertes del proyecto.

### 1.1 Inside Airbnb — el corazón del dataset

**URL:** https://insideairbnb.com/get-the-data/

Inside Airbnb es un proyecto de open data que publica scrapes mensuales de los listings de Airbnb por ciudad. Es la fuente principal y aporta dos ficheros:

- **`listings.csv`** — catálogo de pisos. 18.172 filas, una por apartamento turístico activo en Barcelona. Contiene ubicación, capacidad, características del piso, scores de reviews y datos del anfitrión.
- **`calendar.csv`** — calendario de disponibilidad. ~5,3 millones de filas: una por cada combinación piso × día durante los 365 días siguientes al scrape. La columna clave es `available` (`'t'` = libre, `'f'` = no disponible), que es la base de la **variable objetivo del modelo**.

**Versión utilizada:** scrape del 14 de diciembre de 2025.

### 1.2 Open-Meteo — clima diario

**URL:** https://open-meteo.com (gratuito, licencia CC BY 4.0)

API meteorológica pública que devuelve histórico y climatología de cualquier punto del planeta sin necesidad de clave. Aporta los datos diarios de **temperatura máxima/mínima/media, precipitación acumulada y velocidad del viento** para Barcelona. Para los días futuros sin datos observados, se sustituye con la climatología del año anterior.

### 1.3 Ticketmaster Discovery API — eventos

**URL:** https://developer.ticketmaster.com (clave gratuita, 5.000 llamadas/día)

API de eventos que devuelve conciertos, partidos y eventos culturales por área geográfica. Aunque se descargan los eventos del área metropolitana de Barcelona, **finalmente no se integran en el modelo** porque los eventos disponibles cubren Abril-Julio 2026 y el horizonte del modelo es Diciembre 2025-Febrero 2026: no hay solapamiento. Quedan como tabla auxiliar.

### 1.4 Festivos catalanes — calendario laboral

Lista manual de festivos oficiales de Cataluña codificada directamente en el notebook 03 (Navidad, Reyes, Año Nuevo, etc.). Genera la variable binaria `is_holiday`.

---

## 2. Fase por fase con los notebooks

El proyecto sigue **CRISP-DM** (la metodología estándar de proyectos de ciencia de datos: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment) y la articula en cinco notebooks Jupyter ejecutables en orden, más un script auxiliar para Orange.

| # | Notebook | Fase CRISP-DM | Output principal |
|---|---|---|---|
| 01 | `01_descarga_datos.ipynb` | Data Understanding | Datos crudos en `data/raw/` |
| 02 | `02_exploracion.ipynb` | Data Understanding | EDA, hallazgos críticos |
| 03 | `03_limpieza.ipynb` | Data Preparation | CSVs limpios en `data/processed/` |
| 04 | `04_integracion.ipynb` | Data Preparation | `dataset_integrado.csv` |
| 05 | `05_modelado.ipynb` | Modeling + Evaluation | Modelos entrenados y métricas |

### Notebook 01 — Descarga de datos

**Qué hace:** trae los datos al disco local. Inside Airbnb se descarga manualmente desde su web (no admite API), Open-Meteo y Ticketmaster vía sus APIs.

**Por qué está:** sin materia prima en local no hay proyecto. Esta fase deja todos los inputs disponibles antes de empezar a procesar.

### Notebook 02 — Exploración (EDA)

**Qué hace:** análisis exploratorio completo de las cuatro fuentes. Distribuciones de variables, nulos, correlaciones, gráficos de tendencia, estadísticas descriptivas.

**Por qué es la fase más importante:** **antes de modelar, hay que entender qué tienes entre manos**. Esta fase detectó los tres hallazgos críticos del proyecto:

1. **La columna `price` está 100 % vacía.** Inside Airbnb dejó de publicarla en 2024 por restricciones legales. Esto motivó el **pivot del proyecto** desde "Predictor de Precio" hacia "Predictor de Ocupación".
2. **La columna `available='f'` mezcla dos cosas distintas:** noches reservadas por turistas y noches bloqueadas voluntariamente por el anfitrión. En barrios pequeños y residenciales el bloqueo manual contamina la señal. Por eso el modelo se **limita a 8 semanas posteriores al scrape**, donde predomina la reserva real.
3. **Los eventos de Ticketmaster no se solapan temporalmente** con el horizonte del modelo. Decisión: dejar los eventos como tabla auxiliar pero no integrarlos como feature.

Este EDA es lo que demuestra **criterio analítico** y no implementación a ciegas.

### Notebook 03 — Limpieza por fuente

**Qué hace:** transforma los datos crudos en datos modelables. Tres operaciones por fuente:

- **listings.csv:** filtrado a 25 columnas útiles, conversión de booleanos textuales `t`/`f` a `1`/`0`, imputación de nulos en `bedrooms` y `bathrooms` por la mediana del barrio.
- **calendar.csv:** filtrado al horizonte de 56 días (14/12/2025 → 07/02/2026), creación de la variable target `occupied`, generación de features temporales como `dow` (día de la semana), `is_weekend`, `month`, `is_holiday`.
- **clima.csv:** categorización del código WMO en 4 categorías cualitativas (`soleado`, `nublado`, `lluvia`, `extremo`), cálculo de la temperatura media (`temp_avg`).

**Por qué está:** los datos crudos no se pueden modelar directamente. **Garbage in, garbage out** — si los datos entran sucios, el modelo aprende basura.

### Notebook 04 — Integración

**Qué hace:** une las cuatro fuentes limpias en una única tabla con un join a tres bandas usando pandas:

```
calendar_clean ⟕ listings_clean ⟕ clima_clean
```

**Resultado:** `dataset_integrado.csv` con **1.012.783 filas × 40 columnas** y cero nulos. Granularidad: una fila por combinación piso × día.

**Por qué está:** el modelo necesita ver toda la información de un día concreto de un piso en una sola fila. Antes están en tablas separadas y no se podrían combinar al entrenar.

**Algunas columnas representativas del dataset final:**

| Columna | Tipo | Significado |
|---|---|---|
| `listing_id` | identificador | ID único del piso |
| `date` | fecha | Día concreto |
| `occupied` | target binario | 1 si reservado/bloqueado, 0 si libre |
| `room_type` | categórica | Tipo de alojamiento |
| `accommodates` | numérica | Capacidad de personas |
| `temp_avg` | numérica | Temperatura media del día |
| `is_weekend` | binaria | 1 si sábado o domingo |
| `is_holiday` | binaria | 1 si festivo catalán |

### Notebook 05 — Modelado

**Qué hace:** entrena, evalúa y compara tres modelos de clasificación binaria. Es el **corazón del proyecto**.

Pasos internos:

1. **Feature engineering avanzado** (ver siguiente apartado).
2. **Split temporal**: primeros 42 días = train (758.375 filas), últimos 14 días = test (254.408 filas). No es split aleatorio, es split por fecha para **simular predicción real** (entrenar con pasado, evaluar con futuro).
3. **Entrenamiento** de los tres modelos.
4. **Evaluación** con métricas estándar y matrices de confusión.

**Feature engineering crítico:**

- **Drop de columnas con leakage:** se eliminan `availability_30/60/90/365` y `estimated_occupancy_l365d`. Vienen del propio calendar y son proxies directos del target. Sin este filtro, los modelos darían AUC > 0,93 pero por motivos tramposos.
- **Target encoding por listing y por barrio:** se sustituyen las variables categóricas de alta cardinalidad por su tasa media de ocupación en el train. Esto convierte el `listing_id` (18.172 valores) en una variable numérica predictiva (`listing_te`).
- **One-hot encoding** para las categóricas de baja cardinalidad (`room_type`, `property_type`, `weather_cat`, `neighbourhood_group_cleansed`).

### Flujo paralelo en Orange Data Mining

Además de los cinco notebooks, hay un flujo visual en `orange/pipeline_ocupacion.ows` que **replica el modelado del notebook 05** con widgets en lugar de código. Como Orange no calcula target encoding internamente, antes hay que ejecutar el script `orange/preparar_dataset_orange.py` que produce `train.csv` y `test.csv` con todo el feature engineering ya aplicado.

**Por qué dos plataformas:** demuestra dominio de un enfoque programático (sklearn) y otro visual (Orange). Si las métricas coinciden entre ambas, gana confianza la solidez del pipeline.

---

## 3. Resultados: AUC, F1 y la curva ROC

Las métricas finales del modelo ganador (Random Forest) sobre el conjunto de test (254.408 filas):

| Métrica | Valor | Umbral del curso | ¿Cumple? |
|---|---:|---:|:---:|
| AUC | **0,895** | ≥ 0,80 | Sí |
| F1 | **0,812** | ≥ 0,75 | Sí |
| Accuracy | 0,812 | — | — |
| MCC | 0,627 | — | — |

### F1-score — "¿qué tan bueno es cuando dice OCUPADO?"

Combina dos cosas en un solo número entre 0 y 1:

- **Precision:** de las noches que el modelo etiqueta como ocupadas, ¿cuántas lo están de verdad?
- **Recall:** de las noches realmente ocupadas, ¿cuántas detecta el modelo?

El F1 es la media armónica de las dos: si una de ellas es muy baja, el F1 cae mucho. Por eso es una métrica más exigente que la accuracy simple.

**En el proyecto:** F1 = 0,812. De cada 100 noches que el modelo dice "ocupada", acierta unas 81. Es un buen equilibrio entre detectar bien y no equivocarse demasiado.

**Característica clave:** el F1 depende del **umbral de decisión** (por defecto 0,5). Si cambias el umbral, el F1 cambia.

### AUC — "¿qué tan bien distingue OCUPADO de LIBRE?"

Mide la capacidad **global** del modelo para discriminar entre las dos clases, sin depender de un umbral concreto. Va de 0,5 (modelo aleatorio) a 1,0 (modelo perfecto).

**Interpretación intuitiva:** si pongo dos noches al azar delante del modelo (una realmente ocupada, otra realmente libre) y le pregunto "¿cuál crees que está ocupada?", el AUC es la probabilidad de que acierte.

**En el proyecto:** AUC = 0,895. Acierta el 89,5 % de las veces, lo cual está en el rango "muy bueno" según la escala estándar:

| AUC | Interpretación |
|---|---|
| < 0,6 | Inservible |
| 0,6 – 0,7 | Pobre |
| 0,7 – 0,8 | Aceptable |
| **0,8 – 0,9** | **Bueno (zona del proyecto)** |
| 0,9 – 1,0 | Excelente |

### Curva ROC — el dibujo

La curva ROC es **el gráfico que mide visualmente lo mismo que el AUC**. De hecho, **el AUC es literalmente el área debajo de esta curva**.

**Cómo se construye:** se varía el umbral de decisión desde 1,0 hasta 0,0, y para cada umbral se calculan dos cosas:

- **Eje X — FPR (False Positive Rate):** errores. De los pisos realmente libres, ¿qué porcentaje se confunden con ocupados?
- **Eje Y — TPR (True Positive Rate):** aciertos. De los pisos realmente ocupados, ¿qué porcentaje se detectan?

**Cómo se lee:**

- La **esquina superior izquierda** (0, 1) representa el modelo perfecto: detecta todo sin equivocarse.
- La **línea diagonal** representa un modelo aleatorio (sin valor predictivo).
- **Cuanto más pegada esté la curva a la esquina superior izquierda, mejor el modelo.**

**En el proyecto** (`roc_analysis.png` en `orange/images/`): las **tres curvas** (Logistic Regression, Random Forest, Gradient Boosting) están **casi superpuestas y muy pegadas a la esquina superior izquierda**. Eso significa que los tres modelos discriminan muy bien y de manera muy similar entre noches ocupadas y libres.

### Diferencia clave entre F1 y AUC en una frase

- **F1** evalúa la decisión final del modelo con un umbral concreto.
- **AUC** evalúa la capacidad subyacente del modelo de distinguir clases con cualquier umbral.

Por eso se reportan las dos: el F1 para la calidad de las predicciones tomadas, el AUC para la "inteligencia general" del clasificador.

---

## 4. Modelos usados, por qué y cómo van

Se entrenaron **tres modelos de clasificación binaria** porque representan los **tres paradigmas estándar** de Machine Learning para datos tabulares. No son tres modelos al azar: cubren todo el espectro de complejidad.

### 4.1 Logistic Regression — el modelo lineal

**Qué es:** un modelo lineal clásico. Aprende coeficientes (pesos) para cada feature, los suma y aplica una función sigmoide para obtener una probabilidad entre 0 y 1.

**Por qué se usa:**

- Es la **línea base** del proyecto. Si un modelo más complejo no consigue superarla, algo va mal.
- **Rápido** de entrenar (segundos).
- **Interpretable**: puedes mirar los coeficientes y entender qué pesa más.

**Cómo va en el proyecto:** F1 = 0,785, AUC = 0,891. Cumple los umbrales pero queda detrás de los ensembles.

### 4.2 Random Forest — el ensemble por bagging (GANADOR)

**Qué es:** un conjunto de cientos de árboles de decisión, cada uno entrenado sobre un subconjunto aleatorio de filas y columnas. La predicción final es la mayoría de votos.

**Por qué se usa:**

- **No lineal**: captura interacciones complejas entre variables.
- **Robusto**: tolera ruido, outliers y features irrelevantes sin necesidad de tunear mucho.
- Es el **caballo de batalla** de la industria para datos tabulares medianos.
- Proporciona **feature importance**, lo que ayuda a entender qué variables son más predictivas.

**Cómo va en el proyecto:** F1 = **0,812**, AUC = **0,895**. **Es el modelo ganador**, con errores casi simétricos en la matriz de confusión.

### 4.3 Gradient Boosting — el ensemble por boosting

**Qué es:** también un conjunto de árboles, pero entrenados **uno detrás de otro de forma iterativa**: cada árbol nuevo se especializa en corregir los errores que cometió el conjunto anterior.

**Por qué se usa:**

- Es la **base de XGBoost, LightGBM y CatBoost**, considerados estado del arte para clasificación tabular.
- Demuestra entender la diferencia entre **bagging** (modelos en paralelo) y **boosting** (modelos en serie corrigiéndose).

**Cómo va en el proyecto:** F1 = 0,804, AUC = 0,893. Va prácticamente empatado con Random Forest (diferencia de ~0,002 en AUC).

### 4.4 Comparativa final

| Modelo | AUC | F1 | Posición |
|---|---:|---:|---|
| **Random Forest** | **0,895** | **0,812** | **Ganador** |
| Gradient Boosting | 0,893 | 0,804 | Casi empatado |
| Logistic Regression | 0,891 | 0,785 | Tercero pero cumple |

**Lectura clave:** los tres modelos cumplen los umbrales del curso. La diferencia entre ellos es pequeña porque **hay una feature dominante** en el dataset (el target encoding por listing, que captura la popularidad histórica de cada piso). Esto demuestra que **el feature engineering pesa tanto como el algoritmo elegido**.

---

## 5. ¿Por qué Google BigQuery?

BigQuery es el **data warehouse cloud** de Google, donde se almacena el dataset integrado para que pueda consultarse mediante SQL desde cualquier herramienta (en este caso, Power BI).

### 5.1 Cuatro razones técnicas

**1. Free tier generoso.** Google ofrece 1 TB de queries al mes y 10 GB de almacenamiento sin coste. El dataset del proyecto pesa 227 MB y todas las consultas juntas no llegan ni al 1 % de la cuota mensual. Coste real del proyecto en cloud: **0 €**.

**2. Conector nativo a Power BI.** Power BI Desktop tiene un conector oficial para Google BigQuery. Esto significa que el dashboard se conecta directamente a la tabla cloud sin necesidad de scripts intermedios. Si mañana se sube un nuevo scrape, basta con pulsar **Actualizar** en Power BI y todos los visuales se recalculan.

**3. SQL estándar.** BigQuery usa una variante de SQL muy similar al estándar ANSI, lo que permite escribir consultas analíticas (las tres queries `ocupacion_por_*.sql` del proyecto) sin curvas de aprendizaje específicas. Una persona que sepa SQL básico puede explorar el dataset en BigQuery sin más herramientas.

**4. Escalabilidad sin migración.** Si el proyecto creciera de Barcelona a 50 ciudades europeas (decenas de millones de filas), BigQuery escalaría sin necesidad de cambiar nada de la arquitectura. Es la misma plataforma que usan empresas con petabytes de datos.

### 5.2 Encaje en el proyecto

BigQuery es **el puente entre la fase de Modeling (notebooks/Orange) y la fase de Deployment (Power BI)**. El flujo es:

```
dataset_integrado.csv
   ↓ (script sql/subir_dataset.py)
BigQuery: price-optimizer-bcn.datos.fact_ocupacion
   ↓ (3 queries SQL agregadas + tabla principal)
Power BI: dashboard_ocupacion.pbix (3 páginas interactivas)
```

Sin BigQuery en medio, el dashboard tendría que cargar el CSV de 227 MB localmente cada vez, perdiendo la ventaja de la conexión cloud y del refresco automático. Con BigQuery, el dataset vive en la nube y es accesible desde cualquier herramienta autorizada.

### 5.3 Alternativas descartadas y por qué

- **PostgreSQL/MySQL local:** requiere instalación, mantenimiento y no tiene free tier comparable.
- **AWS Redshift, Azure Synapse:** equivalentes a BigQuery pero sin free tier para proyectos pequeños.
- **Solo CSV en disco:** sin escalabilidad, sin acceso multi-herramienta, sin refresco programable.

BigQuery es el equilibrio óptimo entre **facilidad de uso, integración con Power BI, gratuidad y profesionalidad** para un proyecto de este tamaño.

---

## Frase de cierre para defensa

> *"El proyecto integra cuatro fuentes heterogéneas de datos públicos en un dataset único de un millón de filas. El flujo se articula en cinco notebooks (descarga, exploración, limpieza, integración, modelado) más un flujo paralelo en Orange para validación visual. Los tres modelos entrenados (Logistic Regression, Random Forest, Gradient Boosting) cumplen los umbrales del curso, con Random Forest como ganador (AUC = 0,895, F1 = 0,812). Los resultados se almacenan en Google BigQuery para que un dashboard interactivo en Power BI los consuma directamente. Toda la decisión técnica está documentada y justificada, y el sistema completo es reproducible desde cero clonando el repositorio."*
