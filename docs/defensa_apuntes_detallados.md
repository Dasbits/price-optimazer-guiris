# Apuntes detallados para defensa — Predictor de Ocupación Barcelona

> Este documento es para empollar. Cubre todos los conceptos del proyecto con explicaciones didácticas, las preguntas más probables del profesor con respuestas extensas y frases preparadas para defender cada decisión técnica.

---

## Índice

1. [Glosario de términos clave](#1-glosario-de-términos-clave)
2. [El proyecto en 30 segundos](#2-el-proyecto-en-30-segundos)
3. [CRISP-DM fase a fase con detalle](#3-crisp-dm-fase-a-fase-con-detalle)
4. [Los tres modelos explicados](#4-los-tres-modelos-explicados)
5. [Métricas de evaluación con explicación didáctica](#5-métricas-de-evaluación-con-explicación-didáctica)
6. [Las 25 preguntas más probables del profesor](#6-las-25-preguntas-más-probables-del-profesor)
7. [Frases preparadas para defender decisiones](#7-frases-preparadas-para-defender-decisiones)

---

## 1. Glosario de términos clave

| Término | Qué es | Ejemplo del proyecto |
|---|---|---|
| **CRISP-DM** | Cross-Industry Standard Process for Data Mining. Metodología estándar de 6 fases. | Estructura todo el proyecto. |
| **Clasificación binaria** | Predecir entre dos clases (0/1). | Predecir si una noche estará ocupada o libre. |
| **Variable target** | Lo que queremos predecir. | `occupied`. |
| **Features** | Variables que el modelo usa para predecir. | Las 56 columnas del dataset modelado. |
| **Train / Test** | División del dataset: train para entrenar, test para evaluar. | 758k filas train, 254k filas test. |
| **Split temporal** | Dividir train/test por fecha en lugar de aleatorio. | Primeros 42 días train, últimos 14 test. |
| **Leakage (fuga de información)** | Cuando una feature contiene información del target. | `availability_*` proxy directo de `occupied`. |
| **Target encoding** | Codificar una categoría como la media del target en ese grupo. | `listing_te`, `neigh_enc`. |
| **One-hot encoding** | Codificar una categoría con N valores en N columnas binarias. | `room_type` → 4 columnas binarias. |
| **Class weight** | Peso aplicado a cada clase para equilibrar desbalanceos. | Quitado para mejorar F1. |
| **Hiperparámetro** | Parámetro del modelo que se elige antes de entrenar. | `n_estimators=200`, `max_depth=15`. |
| **Ensemble** | Combinación de varios modelos simples. | Random Forest = ensemble de árboles. |
| **Bagging** | Técnica de ensemble: entrenar modelos sobre subconjuntos aleatorios. | Random Forest. |
| **Boosting** | Técnica de ensemble: cada modelo corrige errores del anterior. | Gradient Boosting. |
| **Threshold** | Umbral de probabilidad para decidir la clase. | Default 0.5. |
| **Accuracy** | Porcentaje de aciertos sobre el total. | 0.812 (81%). |
| **Precision** | De los que predigo positivos, cuántos lo son de verdad. | 78.7% en RF. |
| **Recall** | De los positivos reales, cuántos detecto. | 84.2% en RF. |
| **F1-score** | Media armónica de precision y recall. | 0.812 en RF. |
| **AUC-ROC** | Área bajo la curva ROC. Capacidad discriminativa. | 0.895 en RF. |
| **MCC** | Matthews Correlation Coefficient. Métrica robusta para binaria. | 0.627 en RF. |
| **Matriz de confusión** | Tabla 2x2 con TP/FP/TN/FN. | TP=104k, TN=102k, FP=28k, FN=20k. |
| **TP, TN, FP, FN** | True/False Positive/Negative. | Aciertos y errores por tipo. |
| **ROC** | Curva que muestra TPR vs FPR para todos los thresholds. | Casi pegada a la esquina superior izquierda. |
| **Cold start** | Problema de predecir para entidades nuevas sin historial. | Listings nuevos sin `listing_te`. |
| **Confounding** | Variable oculta que media la relación entre dos variables. | Lluvia-ocupación mediada por la fecha. |
| **EDA** | Exploratory Data Analysis. | Notebook 02. |
| **Pivot del proyecto** | Cambio de objetivo a mitad de proyecto. | Precio → Ocupación. |
| **Data warehouse** | Base de datos cloud para análisis. | Google BigQuery. |
| **DAX** | Lenguaje de fórmulas de Power BI. | `% Ocupación = AVERAGE(...)`. |
| **Slicer** | Filtro interactivo en Power BI. | Slicer temporal, slicer de segmento. |

---

## 2. El proyecto en 30 segundos

> *"Predictor de ocupación de apartamentos turísticos en Barcelona. Clasificación binaria supervisada. Predigo, para cada combinación piso-día, si ese día estará reservado o bloqueado. El target es la columna `occupied` derivada del calendario público de Inside Airbnb. El proyecto integra cuatro fuentes (Inside Airbnb, Open-Meteo, Ticketmaster, festivos catalanes) en un dataset de 1 millón de filas. Compara tres modelos (Logistic Regression, Random Forest, Gradient Boosting) en dos plataformas (scikit-learn y Orange Data Mining), almacena los resultados en BigQuery y los presenta en un dashboard interactivo de Power BI. El modelo ganador, Random Forest, obtiene AUC=0.895 y F1=0.812, superando los umbrales del curso."*

---

## 3. CRISP-DM fase a fase con detalle

CRISP-DM (Cross-Industry Standard Process for Data Mining) es la metodología estándar para proyectos de ciencia de datos. Define 6 fases secuenciales pero iterativas.

### Fase 1: Business Understanding

**Pregunta que responde:** ¿Qué problema queremos resolver y por qué?

**Lo que hice:**
- Definí el problema original: Predictor de Precio Óptimo (regresión sobre `price`).
- Establecí métricas de éxito: F1 ≥ 0.75 y AUC ≥ 0.80.
- Tras la fase 2 detecté que `price` estaba vacía y reformulé el problema a clasificación binaria sobre `occupied`.

**Decisión clave:** El pivot del proyecto. Es importante porque demuestra que hay análisis crítico antes de implementar, no implementación a ciegas. Los proyectos reales se reorientan constantemente cuando los datos no son lo esperado.

### Fase 2: Data Understanding

**Pregunta que responde:** ¿Qué datos tenemos y qué nos cuentan?

**Lo que hice:**
- EDA completo en el notebook 02 sobre las cuatro fuentes.
- Estadísticos descriptivos de listings.csv: 18.172 pisos, distribución por barrio, room_type, etc.
- Análisis de calendar.csv: ~5,3 millones de filas, distribución de `available='t'` vs `'f'`.
- Visualización de la serie temporal del clima.
- Cálculo de correlaciones diarias entre clima/eventos y ocupación.

**Tres hallazgos críticos documentados:**
1. **Columna `price` vacía.** Inside Airbnb dejó de publicarla en 2024 por restricciones legales. Motiva el pivot.
2. **Ambigüedad de `available='f'`.** Mezcla noches reservadas con noches bloqueadas por el anfitrión sin distinción. Se mitiga limitando el modelo a 8 semanas posteriores al scrape.
3. **Desfase temporal de Ticketmaster.** Los eventos disponibles cubren Abr-Jul 2026, sin solapamiento con el horizonte del modelo (Dic 2025-Feb 2026). Se descarta como feature.

### Fase 3: Data Preparation

**Pregunta que responde:** ¿Cómo dejamos los datos listos para modelar?

**Lo que hice (notebooks 03 y 04):**

**Limpieza por fuente:**
- `listings.csv`: filtrado a 25 columnas útiles, conversión booleanos textuales `t`/`f` a `1`/`0`, imputación de nulos en `bedrooms`/`bathrooms` por mediana de barrio.
- `calendar.csv`: filtrado al horizonte de 56 días, creación de la variable `occupied`, generación de features temporales (`dow`, `is_weekend`, `month`, `day`, `week`, `is_holiday`).
- `clima_barcelona.csv`: categorización del `weathercode` en cuatro categorías (soleado, nublado, lluvia, extremo) basadas en códigos WMO. Cálculo de `temp_avg`.
- `eventos_barcelona.csv`: limpieza pero no integración en el modelo principal.

**Integración:**
- Join secuencial: `calendar_clean ⟕ listings_clean` (LEFT JOIN por `listing_id`) → `⟕ clima_clean` (LEFT JOIN por `date`).
- Resultado: `dataset_integrado.csv` con 1.012.783 filas × 40 columnas y cero nulos.
- Granularidad: una fila por combinación listing × día.

**Decisiones clave:**
- **Limitación a 8 semanas post-scrape.** Mitiga el sesgo de bloqueos de anfitrión que dominan en horizontes largos.
- **Eliminación de eventos del modelo.** Por desfase temporal documentado, se mantiene como tabla auxiliar.

### Fase 4: Modeling

**Pregunta que responde:** ¿Qué algoritmos usamos y con qué hiperparámetros?

**Lo que hice (notebook 05 + Orange):**

**Estrategia de evaluación:**
- Split temporal en `2026-01-25`: train = 42 días (758.375 filas), test = 14 días (254.408 filas).
- Por qué temporal: simula predicción real (entrenar con pasado, evaluar con futuro). El test cae además fuera de temporada alta, lo que añade exigencia.

**Feature engineering crítico:**
- **Anti-leakage:** drop de `availability_30/60/90/365` y `estimated_occupancy_l365d`. Vienen del propio calendar y son proxies directos del target.
- **Target encoding:** cálculo de `neigh_enc` (media de `occupied` por barrio en train) y `listing_te` (media por listing). Solo con datos de train para evitar data leakage hacia test.
- **One-hot encoding:** de `room_type`, `property_type`, `weather_cat`, `neighbourhood_group_cleansed`.

**Tres modelos entrenados** (ver sección 4 para detalle).

**Plataforma dual:**
- **scikit-learn** (notebook 05): implementación programática con control fino.
- **Orange Data Mining** (`pipeline_ocupacion.ows`): pipeline visual con widgets para validación cruzada.

### Fase 5: Evaluation

**Pregunta que responde:** ¿Cuán bien funciona el modelo?

**Métricas finales sobre el conjunto de test (254.408 filas):**

| Modelo | AUC | F1 | Accuracy | MCC |
|---|---:|---:|---:|---:|
| Random Forest | **0.895** | **0.812** | **0.812** | **0.627** |
| Gradient Boosting | 0.893 | 0.804 | 0.804 | 0.612 |
| Logistic Regression | 0.891 | 0.785 | 0.787 | 0.595 |

**Cumplimiento de umbrales del curso:**
- F1 ≥ 0.75 ✓ en los tres modelos.
- AUC ≥ 0.80 ✓ en los tres modelos.

**Matriz de confusión del Random Forest:**

|  | Pred libre (0) | Pred ocupado (1) |
|---|---:|---:|
| Real libre (0) | 102.473 (TN) | 28.209 (FP) |
| Real ocupado (1) | 19.524 (FN) | 104.202 (TP) |

- TN: 102.473 → 78,4% de los libres reales.
- FP: 28.209 → 21,6% de los libres reales (errores tipo I).
- FN: 19.524 → 15,8% de los ocupados reales (errores tipo II).
- TP: 104.202 → 84,2% de los ocupados reales.

**Importance del Random Forest:**
- `listing_te`: 0.66 (dominante).
- `reviews_per_month`, `latitude`, `longitude`, `number_of_reviews`: 0.03-0.07 cada una.
- Resto de features: <0.03.

### Fase 6: Deployment

**Pregunta que responde:** ¿Cómo lo ponemos en manos del usuario?

**Lo que hice:**

**Subida a BigQuery:**
- Script `sql/subir_dataset.py`.
- Carga `dataset_integrado.csv` a `price-optimizer-bcn.datos.fact_ocupacion`.
- Auto-detección de esquema, modo Importar, free tier.

**Tres queries SQL de KPI:**
- `ocupacion_por_barrio.sql`: ranking dual con UNION ALL (segmento `todo` vs `entire_home`, umbral listings ≥ 30).
- `ocupacion_por_room_type.sql`: KPI por categoría con efecto Navidad vs resto.
- `ocupacion_por_clima.sql`: 3 vistas (categoría, temperatura, lluvia) agregadas a nivel día.

**Dashboard Power BI** (`dashboard_ocupacion.pbix`):
- Conexión a BigQuery en modo Importar.
- 4 datasets independientes, sin relaciones formales.
- Página 1 (Visión general): 4 KPIs, slicer temporal, gráfico de líneas, ranking de distritos.
- Página 2 (Mercado): treemap por room_type, comparativa Navidad vs resto, top 10 barrios con slicer de segmento.
- Página 3 (Clima): 3 visuales filtrados por métrica, nota didáctica sobre confounding temporal.
- 4 medidas DAX: Listings totales, Noches totales, % Ocupación, Pico ocupación diaria.

---

## 4. Los tres modelos explicados

### Logistic Regression (Regresión Logística)

**Qué es:** modelo lineal que estima la probabilidad de la clase positiva mediante la función sigmoide aplicada a una combinación lineal de las features.

**Fórmula simplificada:** `P(y=1|x) = 1 / (1 + e^(-z))` donde `z = w0 + w1*x1 + w2*x2 + ...`

**Hiperparámetros usados:**
- Regularización: L2 (Ridge), C=1.
- max_iter: 1000.
- class_weight: desmarcado.

**Por qué se incluye:** referencia (baseline). Es rápido, sus coeficientes son interpretables y sirve como suelo mínimo de rendimiento.

**Resultado:** F1=0.785, AUC=0.891 en Orange. Sorpresivamente alto comparado con sklearn (0.514, 0.629); la diferencia se explica por el preprocessing automático de Orange y el `class_weight='balanced'` que sí estaba activo en sklearn.

### Random Forest

**Qué es:** ensemble basado en bagging. Entrena múltiples árboles de decisión sobre subconjuntos aleatorios del dataset y de las features. Agrega las predicciones por votación mayoritaria (clasificación) o media (regresión).

**Por qué funciona:** la diversidad de los árboles reduce la varianza y captura interacciones no lineales sin requerir feature engineering manual.

**Hiperparámetros usados:**
- n_estimators: 200 (más árboles → más estable, más lento).
- max_depth: 15 (limita la profundidad para evitar overfitting).
- min_samples_leaf: 5 (hojas mínimas para evitar fragmentación).
- random_state: 42 (reproducibilidad).

**Por qué es el ganador:** equilibra precision y recall mejor que los otros dos. Los errores son simétricos (28k FP vs 20k FN). Es robusto a hiperparámetros y captura la señal del `listing_te` mejor que la regresión lineal.

**Resultado:** AUC=0.895, F1=0.812.

### Gradient Boosting

**Qué es:** ensemble basado en boosting iterativo. Cada árbol nuevo se entrena para corregir los errores residuales del conjunto de árboles anteriores. Es la base de algoritmos modernos como XGBoost, LightGBM, CatBoost.

**Por qué funciona:** la corrección iterativa permite alcanzar precisión muy alta. Suele ser uno de los modelos más fuertes en datos tabulares.

**Hiperparámetros usados:**
- n_estimators: 200.
- learning_rate: 0.10 (peso de cada árbol nuevo).
- max_depth: 5 (árboles superficiales que se combinan).
- min_samples_split: 2 (default).

**Por qué no gana:** muy pegado al RF (AUC 0.893 vs 0.895). En datos donde la señal está concentrada en una feature dominante (`listing_te`), todos los modelos ensembles dan resultados similares.

**Resultado:** AUC=0.893, F1=0.804.

---

## 5. Métricas de evaluación con explicación didáctica

### Matriz de confusión

Es una tabla 2×2 que cruza predicciones con realidad:

|  | Predicho positivo | Predicho negativo |
|---|---|---|
| Real positivo | **TP** (acierto) | **FN** (falso negativo, error tipo II) |
| Real negativo | **FP** (falso positivo, error tipo I) | **TN** (acierto) |

**De la matriz se derivan todas las demás métricas.**

### Accuracy (precisión global)

`Accuracy = (TP + TN) / Total`

**Qué mide:** porcentaje de aciertos sobre el total.

**Cuándo es engañosa:** cuando las clases están desbalanceadas. Si el 95% de los datos son negativos, predecir siempre "negativo" da 95% de accuracy pero el modelo no sirve.

**En el proyecto:** RF acierta el 81,2% de las predicciones. Es buena porque las clases están casi balanceadas (55/45).

### Precision

`Precision = TP / (TP + FP)`

**Qué mide:** de los que predigo positivos, cuántos lo son de verdad.

**Cuándo importa:** cuando los falsos positivos son costosos. Ej: si etiqueto un email como spam y no lo es, el usuario pierde un email importante.

**En el proyecto:** 78,7% en RF. De cada 100 noches que predigo como ocupadas, 79 lo están realmente.

### Recall (sensibilidad)

`Recall = TP / (TP + FN)`

**Qué mide:** de los positivos reales, cuántos detecto.

**Cuándo importa:** cuando los falsos negativos son costosos. Ej: en un test médico de cáncer, no detectar un caso real es muy grave.

**En el proyecto:** 84,2% en RF. De cada 100 noches realmente ocupadas, detecto 84.

### F1-score

`F1 = 2 × (Precision × Recall) / (Precision + Recall)`

**Qué mide:** media armónica de precision y recall. Penaliza los extremos: si una de las dos es muy baja, el F1 baja mucho.

**Por qué se usa en lugar de accuracy:** robusto al desbalanceo.

**En el proyecto:** 0.812 en RF. Indica un buen equilibrio entre precision y recall.

### AUC-ROC

**ROC** = Receiver Operating Characteristic. Es una curva que dibuja, para todos los umbrales de decisión posibles:
- Eje X: **FPR** (False Positive Rate) = FP / (FP + TN). Tasa de falsos positivos sobre los negativos reales.
- Eje Y: **TPR** (True Positive Rate, igual que recall) = TP / (TP + FN). Tasa de verdaderos positivos sobre los positivos reales.

**Cómo se construye:** se varía el threshold desde 1.0 (siempre predice negativo, punto (0,0)) hasta 0.0 (siempre predice positivo, punto (1,1)). Cada threshold genera un punto en la curva.

**Esquinas de referencia:**
- (0,0): nunca predice positivo. 0 TP, 0 FP.
- (1,1): siempre predice positivo. Detecta todo, falla en todo lo negativo.
- (0,1): clasificador perfecto. Detecta todo sin falsos positivos.
- Diagonal (línea negra punteada): clasificador aleatorio.

**AUC** = Area Under the Curve. Va de 0.5 (aleatorio) a 1.0 (perfecto).

| AUC | Interpretación |
|---|---|
| < 0.6 | Inservible |
| 0.6-0.7 | Pobre |
| 0.7-0.8 | Aceptable |
| 0.8-0.9 | **Bueno (zona del proyecto)** |
| 0.9-1.0 | Excelente |

**En el proyecto:** AUC=0.895 en RF. Indica que si tomamos al azar una noche realmente ocupada y una realmente libre, el modelo da una probabilidad mayor a la ocupada el 89,5% de las veces.

### MCC (Matthews Correlation Coefficient)

`MCC = (TP·TN - FP·FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))`

**Qué mide:** correlación entre predicciones y etiquetas reales. Va de -1 (totalmente equivocado) a +1 (perfecto), 0 = aleatorio.

**Por qué se usa:** muy robusta al desbalanceo. Solo es alta si el modelo acierta bien en las cuatro celdas de la matriz de confusión.

**En el proyecto:** 0.627 en RF. Indica una correlación positiva clara.

---

## 6. Las 25 preguntas más probables del profesor

### Sobre el problema y el pivot

**1. ¿Qué predice tu modelo?**
Predice si una noche concreta de un piso turístico de Barcelona estará reservada/bloqueada (1) o libre (0). Es clasificación binaria supervisada.

**2. ¿Por qué cambiaste de Predictor de Precio a Predictor de Ocupación?**
Porque la columna `price` del dataset Inside Airbnb está 100% vacía desde finales de 2024 por restricciones legales aplicadas por la plataforma. Lo descubrí en la fase de Data Understanding y decidí pivotar la tarea para mantener el resto del stack y la metodología.

**3. ¿Cuál es la variable target?**
La columna `occupied`, derivada de `available` del calendar.csv: vale 1 si `available='f'` (no disponible) y 0 si `available='t'`.

### Sobre la metodología

**4. ¿Qué es CRISP-DM?**
Cross-Industry Standard Process for Data Mining. Metodología estándar para proyectos de ciencia de datos, con seis fases: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation y Deployment.

**5. ¿Cómo aplicaste CRISP-DM?**
Cada fase tiene su entregable identificable en el repo: notebooks 02-05 cubren Data Understanding, Preparation y Modeling; los entregables de Evaluation están en `orange/images/` y en el notebook 05; el Deployment se materializa en BigQuery + Power BI.

### Sobre los datos

**6. ¿De dónde vienen los datos?**
De cuatro fuentes: Inside Airbnb (listings y calendar), Open-Meteo (clima), Ticketmaster (eventos, no integrado finalmente) y una lista manual de festivos catalanes.

**7. ¿Cuántas filas tiene el dataset modelado?**
1.012.783 filas, una por combinación de los 18.172 listings con cada uno de los 56 días del horizonte (14/12/2025 a 07/02/2026).

**8. ¿Qué problemas encontraste en los datos?**
Tres: la columna `price` vacía, la ambigüedad de `available='f'` (mezcla reservas con bloqueos del anfitrión) y el desfase temporal de Ticketmaster (eventos disponibles solo de Abr-Jul 2026).

**9. ¿Cómo limpiaste los datos?**
Imputación de nulos por mediana de barrio, conversión de booleanos `t`/`f` a `1`/`0`, categorización del weathercode en cuatro grupos, filtrado del calendario al horizonte de 8 semanas.

### Sobre el modelado

**10. ¿Qué algoritmos usaste y por qué?**
Tres: Logistic Regression como referencia lineal, Random Forest como ensemble basado en bagging y Gradient Boosting como ensemble basado en boosting iterativo. Son los tres clasificadores más representativos del estado del arte para datos tabulares.

**11. ¿Por qué split temporal y no aleatorio?**
Para simular un escenario realista de predicción: el modelo se entrena con el pasado y se evalúa con el futuro. El test cae además fuera de temporada alta, lo que añade exigencia.

**12. ¿Qué es leakage y cómo lo evitaste?**
Es cuando una feature contiene información del target. Las columnas `availability_30/60/90/365` y `estimated_occupancy_l365d` vienen del propio `calendar.csv` y son proxies directos del target. Las eliminé explícitamente del feature set. Sin ese filtro daban AUC tramposo > 0.93.

**13. ¿Qué es target encoding?**
Codificar una categoría como la media del target en ese grupo. Calculo `listing_te` como la media de `occupied` por listing y `neigh_enc` como la media por barrio. Las calculo solo sobre datos de train para no contaminar el test.

**14. ¿Por qué usas one-hot encoding?**
Porque los algoritmos de ML no consumen strings directamente. One-hot convierte una variable categórica con N valores en N columnas binarias 0/1, sin imponer un orden artificial entre categorías.

**15. ¿Cuál es el modelo ganador y con qué métricas?**
Random Forest, con AUC=0.895 y F1=0.812 en el conjunto de test. Supera los umbrales del curso (F1 ≥ 0.75 y AUC ≥ 0.80) con holgura.

**16. ¿Qué feature es más importante?**
`listing_te` (target encoding por listing) con importance 0.66 sobre 1.0. La popularidad histórica del piso es el mejor predictor de su ocupación futura.

### Sobre la evaluación

**17. ¿Qué diferencia hay entre F1 y AUC?**
F1 mide el rendimiento en un threshold concreto (0.5 por defecto). AUC mide la capacidad discriminativa del modelo en todos los thresholds. AUC es más robusta al desbalanceo de clases y a la elección del threshold.

**18. ¿Cómo lees una matriz de confusión?**
Es una tabla 2×2 con clase real en las filas y predicha en las columnas. La diagonal son aciertos (TP y TN), las celdas off-diagonal son errores (FP y FN).

**19. ¿Qué es la curva ROC?**
Curva que muestra la tasa de verdaderos positivos vs la tasa de falsos positivos para todos los thresholds posibles. El área bajo la curva (AUC) es una métrica escalar de capacidad discriminativa.

### Sobre el deployment

**20. ¿Por qué BigQuery?**
Por tres razones: free tier generoso (1 TB queries/mes, 10 GB almacenamiento), conector nativo a Power BI y escalabilidad sin cambios de arquitectura.

**21. ¿Por qué Power BI?**
Por su conector nativo a BigQuery, su soporte de medidas DAX, sus slicers interactivos y su gratuidad en versión Desktop. Permite a usuarios no técnicos explorar el dato sin programar.

**22. ¿Qué páginas tiene tu dashboard?**
Tres: Visión general (KPIs, evolución, ranking distritos), Mercado (treemap, comparativa Navidad vs resto, top 10 barrios) y Clima (efecto del tiempo con nota didáctica sobre confounding).

**23. ¿Qué es el confounding temporal de la página de Clima?**
Aparentemente "con lluvia" tiene más ocupación que "sin lluvia". No es causalidad: los días lluviosos coinciden con la semana de Navidad, donde la demanda turística es estructuralmente mayor. La fecha es la variable confusora oculta. Es un ejemplo de "correlación no implica causalidad".

### Sobre alternativas y limitaciones

**24. ¿Qué harías diferente con más tiempo?**
Probaría XGBoost o LightGBM (suelen dar 1-3 puntos extra en AUC), construiría un modelo específico para listings nuevos sin historial (cold start), ampliaría el horizonte temporal acumulando varios scrapes mensuales y desplegaría el modelo como API REST.

**25. ¿Qué limitaciones tiene tu modelo?**
Cuatro: la ambigüedad intrínseca de `available='f'` (mezcla reserva con bloqueo), la dependencia del `listing_te` que no funciona en cold start, el horizonte limitado a 56 días que no permite extrapolar a otras temporadas, y el sesgo del primer día del scrape (~76% ocupación artificial por bloqueos previos).

---

## 7. Frases preparadas para defender decisiones

### Frases sobre metodología

- *"Apliqué CRISP-DM de forma estricta. Cada fase tiene su entregable identificable en el repositorio."*
- *"El proyecto siguió la metodología CRISP-DM, lo cual permitió que el pivot de la fase de Business Understanding no destruyera el trabajo posterior."*
- *"La separación clara entre Business Understanding y Data Understanding permitió detectar el problema de la columna `price` antes de implementar nada."*

### Frases sobre los datos

- *"El dataset combina cuatro fuentes heterogéneas integradas mediante joins en pandas con granularidad listing × día."*
- *"Documenté tres hallazgos críticos en la fase exploratoria que condicionaron las decisiones posteriores del modelado."*
- *"El horizonte se limita a 8 semanas posteriores al scrape para mitigar el sesgo de bloqueos del anfitrión."*

### Frases sobre el modelado

- *"Usé split temporal en lugar de aleatorio para simular un escenario realista de predicción."*
- *"Apliqué target encoding solo sobre los datos de train, evitando data leakage hacia el conjunto de test."*
- *"Eliminé explícitamente las columnas `availability_*` por ser proxies directos del target. Es una decisión metodológica importante."*
- *"Implementé el pipeline en dos plataformas independientes (sklearn y Orange) para validar de manera cruzada la consistencia de los resultados."*

### Frases sobre la evaluación

- *"El modelo ganador, Random Forest, supera con holgura los dos umbrales del curso: F1=0.812 y AUC=0.895."*
- *"La matriz de confusión muestra errores casi simétricos, lo cual indica un modelo equilibrado sin sesgo grave hacia ninguna clase."*
- *"La feature más predictiva es `listing_te` con importance 0.66, capturando la popularidad histórica intrínseca del piso."*

### Frases sobre las limitaciones

- *"El modelo se beneficia mucho del target encoding por listing, lo cual implica que su rendimiento degradaría con listings completamente nuevos. Esta limitación, conocida como cold start, queda documentada."*
- *"La columna `available` de Inside Airbnb mezcla noches reservadas con noches bloqueadas por el anfitrión. Esta ambigüedad es intrínseca al dataset y no se puede resolver sin acceso al backend de Airbnb."*
- *"El horizonte está limitado a 56 días que cubren temporada navideña. Las conclusiones no son extrapolables directamente a verano u otras temporadas."*

### Frases para responder a "¿está desplegado en producción?"

- *"El alcance del curso llega a Deployment como dashboard analítico, no como API. El modelo se entrena offline y los resultados se presentan en Power BI conectado a BigQuery."*
- *"Para producción real, desplegaría el modelo como endpoint REST con FastAPI o como función serverless en Google Cloud Run. Es una línea de mejora futura documentada."*

---

## Bonus: errores típicos a evitar en la defensa

1. **No leas la memoria palabra por palabra.** El profe ya la tiene. Tu rol es comentarla.
2. **No te entretengas en código.** Si el profe pregunta por una función concreta, abre el notebook; si no, no hace falta.
3. **No prometas lo que no hay.** Si te pregunta si has hecho XGBoost y no lo has hecho, dilo claro.
4. **No empieces por la solución.** Empieza por el problema (el pivot) — eso engancha y demuestra criterio.
5. **Si te bloqueas, vuelve al README principal.** Es tu mapa de navegación.
6. **No digas "muy bueno" sin cifras.** Di "AUC 0.895, dentro del rango bueno-excelente según la escala estándar".
7. **No confundas precision con accuracy.** Son métricas distintas con interpretaciones diferentes.
8. **No olvides mencionar la dualidad sklearn/Orange.** Es un punto fuerte que el profe valorará.

---

## Última frase para cerrar la defensa

> *"Para resumir: el proyecto sigue CRISP-DM en sus seis fases, integra cuatro fuentes de datos heterogéneas, entrena tres modelos en dos plataformas independientes y supera los umbrales del curso con holgura. El Random Forest, con AUC=0.895 y F1=0.812, demuestra que la popularidad histórica de cada piso es el mejor predictor de su ocupación futura. El sistema completo está documentado en cuatro READMEs jerarquizados, los resultados se almacenan en BigQuery y se presentan en un dashboard interactivo de Power BI consumible por usuarios no técnicos. Quedo abierto a preguntas."*
