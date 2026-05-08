# Power BI — Dashboard del Predictor de Ocupación

Esta carpeta contiene el dashboard interactivo de Power BI Desktop que cierra la fase **Deployment** de CRISP-DM. El `.pbix` consume datos directamente desde BigQuery (la tabla `fact_ocupacion` y las tres queries SQL de KPI) y los presenta en tres páginas pensadas para responder a preguntas de negocio concretas.

---

## Contenido

```
powerbi/
├── dashboard_ocupacion.pbix    # Fichero del dashboard (abrir con Power BI Desktop)
└── README.md                   # Este documento
```

---

## ¿Por qué Power BI cierra el proyecto?

CRISP-DM termina en **Deployment**: una vez tienes los datos limpios, modelados y validados, el último paso es ponerlos en manos del usuario final en un formato consumible. Power BI cumple eso porque:

1. **Audiencia no técnica.** Un anfitrión, gestor de propiedades o tribunal del curso no quiere abrir un Jupyter notebook ni leer Python. Quiere ver gráficos, KPIs y poder filtrar por fecha o barrio.
2. **Conexión viva a BigQuery.** El dashboard se conecta al dataset que ya tenemos en la nube. Si mañana subes un nuevo scrape de Inside Airbnb, basta con pulsar **Actualizar** y todos los visuales se recalculan.
3. **Explorabilidad.** Los slicers (filtros interactivos) permiten al usuario investigar el dato sin necesidad de volver a programar nada.

---

## Prerequisitos

1. **Power BI Desktop 2.150 o superior** (gratuito, solo Windows). Descarga desde la Microsoft Store o desde https://www.microsoft.com/en-us/download/details.aspx?id=58494.
2. **Cuenta de Google** con acceso al proyecto `price-optimizer-bcn` en Google Cloud (la misma que usaste para la cuenta de servicio de BigQuery).
3. **Tabla `price-optimizer-bcn.datos.fact_ocupacion`** ya cargada en BigQuery. Si no la tienes, ejecuta antes el script `sql/subir_dataset.py` desde la raíz del repo.

---

## Datos importados (4 fuentes independientes)

Power BI no exige que las fuentes estén relacionadas con claves: cada visual del dashboard consume **una sola fuente**, así que no hace falta crear relaciones formales en el modelo de datos. Las cuatro fuentes son:

### 1. `fact_ocupacion` — la tabla principal

Es la tabla cargada en BigQuery por el script `sql/subir_dataset.py`. Contiene **una fila por listing × día**, con todos los atributos del piso replicados en cada fila más los datos meteorológicos del día.

| Característica | Valor |
|---|---|
| Filas | 1.012.783 |
| Columnas | 40 |
| Cobertura temporal | 14/12/2025 → 07/02/2026 (56 días) |
| Listings únicos | 18.172 |
| Tamaño en memoria | ~190 MB |
| Modo de conexión | Importar (no DirectQuery) |

Columnas relevantes para el dashboard:

- **Identificadores**: `listing_id`, `date`.
- **Target**: `occupied` (1 = noche reservada o bloqueada, 0 = libre).
- **Ubicación**: `neighbourhood_cleansed`, `neighbourhood_group_cleansed` (distrito), `latitude`, `longitude`.
- **Tipo de alojamiento**: `room_type`, `property_type`, `accommodates`, `bathrooms`, `bedrooms`, `beds`.
- **Reputación**: `number_of_reviews`, `reviews_per_month`, `review_scores_rating`, `review_scores_location`, `review_scores_value`.
- **Anfitrión**: `host_is_superhost`, `instant_bookable`.
- **Tiempo**: `dow`, `is_weekend`, `month`, `day`, `week`, `is_holiday`.
- **Clima**: `temperature_2m_max/min`, `temp_avg`, `precipitation_sum`, `windspeed_10m_max`, `weather_cat`, `has_rain`.

### 2. `ocupacion_por_room_type` — vista de tipo de alojamiento

Generada por la query `sql/ocupacion_por_room_type.sql`. **4 filas**, una por categoría: Entire home/apt, Private room, Shared room, Hotel room.

| Columna | Significado |
|---|---|
| `room_type` | Tipo (Entire home/apt, Private room, Shared room, Hotel room) |
| `listings` | Número de pisos en esa categoría |
| `pct_listings` | Peso de la categoría sobre el total de la oferta (%) |
| `pct_ocupacion` | Tasa media de ocupación (%) |
| `pct_ocupacion_finde` | Ocupación restringida a sábados y domingos (%) |
| `pct_ocupacion_navidad` | Ocupación durante el periodo 14/12 - 06/01 (%) |
| `pct_ocupacion_resto` | Ocupación fuera de Navidad/Reyes (%) |

### 3. `ocupacion_por_barrio` — vista de barrios

Generada por la query `sql/ocupacion_por_barrio.sql`. **~150 filas** porque devuelve **dos rankings concatenados con UNION ALL** distinguidos por la columna `segmento`.

| Columna | Significado |
|---|---|
| `segmento` | `'todo'` (todos los room_type) o `'entire_home'` (solo pisos enteros) |
| `distrito` | Uno de los 10 distritos de Barcelona |
| `barrio` | Barrio (`neighbourhood_cleansed`) |
| `listings` | Número de pisos en el barrio (umbral mínimo: 30) |
| `noches_total`, `noches_ocupadas` | Volumen agregado |
| `pct_ocupacion` | Tasa media de ocupación (%) |
| `pct_ocupacion_finde` | Ocupación solo sábados y domingos (%) |
| `delta_finde_pp` | Puntos porcentuales que sube/baja el finde respecto al global |

**Por qué dos segmentos**: el ranking sin filtrar inflaba barrios residenciales pequeños (Montbau, Turó de la Peira) donde Inside Airbnb mezcla *reservado* con *bloqueado por el anfitrión*. El segmento `entire_home` filtra a `room_type = 'Entire home/apt'` para reflejar el mercado turístico real.

### 4. `ocupacion_por_clima` — vista del efecto del tiempo

Generada por la query `sql/ocupacion_por_clima.sql`. **~12 filas** porque devuelve tres vistas concatenadas con UNION ALL, distinguidas por la columna `metrica`.

| Columna | Significado |
|---|---|
| `metrica` | `'por_categoria'`, `'por_temperatura'` o `'por_lluvia'` |
| `bucket` | El valor concreto dentro de la métrica (p. ej. `lluvia`, `0 a 5 C`, `con lluvia`) |
| `dias` | Número de días distintos en ese bucket |
| `pct_ocupacion_media` | Ocupación media de los listings esos días (%) |

**Importante**: la query agrega primero a nivel **día** (no listing × día), porque al estudiar el efecto del clima los barrios con muchos pisos pesarían más solo por volumen. Cada fila representa una propiedad climática del día, no de los pisos.

---

## Modelo de datos

Como cada página consume una sola fuente, **no hay relaciones formales entre las cuatro tablas**. El panel **Modelo** de Power BI muestra cuatro tablas aisladas. Esto es intencional y simplifica:

- Evitamos cardinalidad muchos-a-muchos accidental.
- Cada query SQL ya viene agregada al nivel correcto (barrio, room_type, día), no hay que recalcular medidas.
- Si en el futuro quisiéramos cruzar (p. ej. ranking de barrios filtrado por mes), podríamos crear una relación entre `fact_ocupacion[neighbourhood_cleansed]` y `ocupacion_por_barrio[barrio]`. De momento no es necesario.

---

## Página 1 — Visión general

Responde a la pregunta **"¿qué tamaño tiene el mercado y cómo evoluciona la ocupación en el tiempo?"**. Usa exclusivamente la tabla `fact_ocupacion`.

### Medidas DAX creadas

Power BI permite definir fórmulas (medidas) que se calculan dinámicamente sobre cualquier filtro aplicado. Esta página usa cuatro:

```dax
Listings totales = DISTINCTCOUNT(fact_ocupacion[listing_id])
```
Cuenta los listings únicos. Se filtra automáticamente al aplicar el slicer de fechas.

```dax
Noches totales = COUNTROWS(fact_ocupacion)
```
Número total de filas (listing × día). Equivale a la oferta total de noches.

```dax
% Ocupación = AVERAGE(fact_ocupacion[occupied])
```
Promedio del campo `occupied` (que vale 0 o 1). Da la fracción de noches ocupadas. **Formato: Porcentaje, 1 decimal**.

```dax
Pico ocupación diaria = 
MAXX(
    SUMMARIZE(fact_ocupacion, fact_ocupacion[date], "ocup_dia", AVERAGE(fact_ocupacion[occupied])),
    [ocup_dia]
)
```
Esta es la más elaborada: agrupa el dataset por día, calcula la ocupación media de cada día, y devuelve el máximo. Responde "¿cuál fue el día más reservado del horizonte?".

### Visuales

**1. Cuatro tarjetas KPI (parte superior)**

Una tarjeta por cada medida. Pensadas para que el lector capture en 5 segundos las cifras del mercado:

| Tarjeta | Valor esperado | Lectura |
|---|---|---|
| Listings totales | 18.172 | Tamaño del mercado en pisos |
| Noches totales | 1.012.783 | Volumen del análisis |
| % Ocupación | 54,2 % | Tasa media en el horizonte |
| Pico ocupación diaria | 76 % | Día de máxima demanda (Nochebuena) |

**2. Slicer "Rango de fechas"**

Control con dos manijas (modo `Entre`) que permite filtrar todo el dashboard al rango temporal deseado. Cuando lo mueves, las cuatro tarjetas y los dos gráficos siguientes se recalculan automáticamente.

Útil para responder preguntas como "¿qué pasa si solo miro Navidad?" (mover la manija derecha al 6/1) o "¿cómo es la zona post-temporada?" (mover la izquierda al 11/1).

**3. Gráfico de líneas — "Ocupación diaria (%)"**

- **Eje X**: `date` (campo continuo, sin jerarquía de fecha).
- **Eje Y**: medida `% Ocupación`.
- **Línea de referencia**: discontinua en el promedio (54,3 %).

Cuenta la historia temporal del mercado en una imagen: pico el día del scrape (~76 %), repunte navideño (28/12 - 4/1) en torno al 70 %, descenso brusco a primeros de enero hasta estabilizarse en 47-50 % en febrero.

**Detalle a comentar en la memoria**: el primer punto del 14/12 está sobreelevado porque el día del scrape captura todos los calendarios bloqueados desde semanas antes. El sesgo se diluye a partir del día 16-17.

**4. Gráfico de barras horizontales — "Ocupación media por distrito"**

- **Eje Y**: `neighbourhood_group_cleansed` (los 10 distritos de Barcelona).
- **Eje X**: medida `% Ocupación`.
- **Color**: gradiente condicional rojo-amarillo-verde por valor.
- **Orden**: descendente por valor.

Lectura: distritos con más ocupación arriba (Horta-Guinardó 60,8 %, Sant Andreu 60,5 %, Sarrià-Sant Gervasi 57,3 %), distritos con más oferta y competencia abajo (Ciutat Vella, Sant Martí, Nou Barris). El gradiente hace que se lea de un vistazo.

---

## Página 2 — Mercado

Responde a la pregunta **"¿cómo se reparte la oferta y dónde está el negocio?"**. Usa los datasets `ocupacion_por_room_type` y `ocupacion_por_barrio`.

### Visuales

**1. Treemap — "Oferta del mercado por tipo de alojamiento"**

- **Categoría**: `room_type` (de la tabla `ocupacion_por_room_type`).
- **Valores**: `listings`.

Un treemap representa cada categoría como un rectángulo proporcional al valor. La imagen muestra de inmediato que el mercado lo dominan **Entire home/apt (11.740, ~65 %)** y **Private room (6.216, ~34 %)**. Las dos colas (Hotel y Shared, ~100 cada una) son anecdóticas.

**2. Gráfico de barras agrupadas — "Ocupación por tipo: Navidad vs resto"**

- **Eje Y**: `room_type`.
- **Eje X**: dos medidas (`pct_ocupacion_navidad` y `pct_ocupacion_resto`), una por barra agrupada.

Visualiza el efecto temporada por cada tipo de alojamiento. Resultado: las cuatro categorías suben en Navidad respecto al resto (entre +8 y +14 puntos). **Hotel room** y **Entire home/apt** son los más beneficiados por la temporada.

Dato curioso para la memoria: **Private room tiene MÁS ocupación base (61 %) que Entire home/apt (50 %)**. Probable explicación: precio menor, llena más fácil. Es un insight no obvio.

**3. Slicer "Segmento de mercado"**

Control de tipo botón único con dos opciones:
- **Mercado completo** — incluye todos los `room_type`.
- **Solo pisos enteros** — restringe a `room_type = 'Entire home/apt'`.

Filtra al ranking de barrios siguiente. Permite alternar entre la vista global del barrio y la vista del mercado puramente turístico (sin habitaciones, hoteles boutique, etc.).

**4. Gráfico de barras — "Top 10 barrios por ocupación"**

- **Eje Y**: `barrio` (de la tabla `ocupacion_por_barrio`).
- **Eje X**: `pct_ocupacion`.
- **Filtro de visual**: `segmento` (controlado por el slicer anterior).
- **Filtro de visual**: `Top N = 10` por valor `pct_ocupacion`.
- **Color**: gradiente condicional verde-amarillo-rojo.

Los 10 barrios más ocupados según el segmento elegido. Cuando el slicer está en "Mercado completo" lideran barrios residenciales acomodados (la Sagrera, Sarrià, el Guinardó). Cuando está en "Solo pisos enteros" aparecen barrios turísticos clásicos (El Raval, La Barceloneta, Sagrada Família).

---

## Página 3 — Clima

Responde a la pregunta **"¿cómo afecta el tiempo a la ocupación?"**. Usa exclusivamente el dataset `ocupacion_por_clima`.

### Visuales

**1. "Ocupación por categoría de clima (%)"**

- **Eje Y**: `bucket` (lluvia, nublado, extremo).
- **Eje X**: `pct_ocupacion_media`.
- **Filtro de visual**: `metrica = 'por_categoria'`.

Solo aparecen tres categorías porque el horizonte es invernal (no hay días "soleados" según la categorización del notebook 03). No hay diferencias dramáticas entre categorías (~50-58 %).

**2. "Ocupación por temperatura (bins de 5°C, %)"**

- **Eje Y**: `bucket` (`0 a 5 C`, `5 a 10 C`, `10 a 15 C`).
- **Eje X**: `pct_ocupacion_media`.
- **Filtro de visual**: `metrica = 'por_temperatura'`.

La temperatura nunca supera 15°C en este horizonte invernal. Los días más fríos (0-5°C) tienen menor ocupación, pero las diferencias son pequeñas.

**3. "Ocupación con vs sin lluvia (%)"**

- **Eje Y**: `bucket` (con lluvia, sin lluvia).
- **Eje X**: `pct_ocupacion_media`.
- **Filtro de visual**: `metrica = 'por_lluvia'`.

**Hallazgo importante a documentar**: aparentemente "con lluvia" tiene **mayor** ocupación que "sin lluvia" (~56 % vs ~52 %). Esto **no implica que la lluvia atraiga turistas**. Es un caso de **confounding temporal**: los días lluviosos del horizonte coinciden cronológicamente con la semana de Navidad/Reyes, donde la demanda turística sube por motivos completamente independientes del tiempo. La fecha es la variable confusora oculta.

Es un buen ejemplo para mencionar en la memoria como **"correlación ≠ causalidad"** y demuestra conciencia de los sesgos del dato más allá de leer cifras.

---

## Insights principales del dashboard

Resumen de los hallazgos que se pueden extraer interactuando con las tres páginas:

1. **El mercado es enorme y muy concentrado en pisos enteros**. 18.172 listings, dos tercios son Entire home/apt.
2. **Tasa de ocupación media del 54 %** durante el horizonte invernal de 8 semanas. Pico en Nochebuena (~76 %), suelo a principios de febrero (~47 %).
3. **El efecto temporada navideña sube la ocupación 13-14 puntos** en Hotel room y Entire home/apt, las categorías más sensibles a la estacionalidad.
4. **Sarrià, Sant Gervasi y Horta-Guinardó lideran el ranking** en el segmento Entire home/apt — barrios residenciales acomodados con poca oferta y anfitriones más profesionales.
5. **El delta finde-vs-resto es prácticamente cero** en todos los barrios. Conclusión: Barcelona es destino de **estancias largas** (city break de 3-5 días), no de escapadas de fin de semana.
6. **El clima no explica la ocupación de forma directa** — la correlación lluvia-ocupación es aparente pero está mediada por la fecha.

---

## Cómo abrir y editar el `.pbix`

1. Doble clic en `dashboard_ocupacion.pbix` (Power BI Desktop debe estar instalado).
2. La primera vez que se abra, Power BI puede pedir credenciales para BigQuery — usa la cuenta de Google que tiene acceso al proyecto `price-optimizer-bcn`.
3. Para refrescar los datos (si has subido un nuevo scrape a BigQuery): pestaña **Inicio → Actualizar**. Tarda ~2 minutos por la tabla principal.
4. Para añadir/editar visuales: simplemente clic sobre cualquier elemento del lienzo y modificar desde el panel **Visualizaciones** o **Formato del visual**.

---

## Cómo se conecta este dashboard con el resto del proyecto

| Fase CRISP-DM | Entregable | Carpeta |
|---|---|---|
| Business Understanding | Documentación inicial | `docs/` |
| Data Understanding | EDA | `notebooks/02_exploracion.ipynb` |
| Data Preparation | Limpieza + integración | `notebooks/03_limpieza.ipynb`, `notebooks/04_integracion.ipynb` |
| Modeling | Random Forest, Logistic, Gradient Boosting | `notebooks/05_modelado.ipynb` + `orange/pipeline_ocupacion.ows` |
| Evaluation | Métricas, matrices, ROC | `orange/images/` + `notebooks/05_modelado.ipynb` |
| **Deployment** | **Dashboard Power BI** | **este `.pbix`** |

El dashboard es el último eslabón: convierte el dataset que hemos construido y validado en una herramienta consumible por usuarios no técnicos. Cualquiera puede abrir el `.pbix`, mover los slicers, leer las cifras y entender la dinámica del mercado de Airbnb en Barcelona durante el horizonte 14/12/2025 - 07/02/2026.
