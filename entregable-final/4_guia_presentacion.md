# Guía de la presentación final — 15 minutos

> **Objetivo:** contar la historia del proyecto con datos durante 15 minutos. Gráficos de calidad que se entiendan en 5 segundos. Aunque la entrega sea por equipos, la evaluación es individual.

---

## Estructura recomendada — 10 diapositivas + portada y cierre

| # | Diapositiva | Tiempo | Objetivo |
|---|---|---:|---|
| 1 | Portada | 0:30 | Título, autor, contexto del curso |
| 2 | El problema y el pivot | 1:30 | Enganchar con la historia: precio → ocupación |
| 3 | Las 4 fuentes de datos | 1:30 | De dónde sale todo |
| 4 | Metodología CRISP-DM | 1:00 | Hoja de ruta del proyecto |
| 5 | Cifras del dataset final | 1:00 | Volumen y horizonte |
| 6 | Tres modelos comparados | 2:00 | Por qué tres y cuál gana |
| 7 | Métricas finales + ROC | 2:00 | AUC, F1, matriz de confusión |
| 8 | Demo Power BI (live) | 2:30 | Tres páginas en directo |
| 9 | Hallazgo curioso (confounding) | 1:00 | Diferenciarse del resto |
| 10 | Conclusiones y mejoras futuras | 1:00 | Cerrar con valor |
| 11 | Cierre + preguntas | 1:00 | Frase memorable y ronda Q&A |

**Total: 15 minutos exactos.**

---

## Cómo contar la historia con datos

La presentación debe ser una **narrativa**, no una lista de cosas hechas. Estos son los hilos a seguir:

### Acto 1 — El problema (slides 1-3, 3 minutos)

> *"Empecé el proyecto pensando que iba a predecir precios de Airbnb. Cuando descargué los datos descubrí que el precio estaba vacío. Tuve que pivotar la pregunta sin tirar nada del trabajo previo."*

Conflicto + decisión + acción. Eso engancha al tribunal desde el primer minuto.

### Acto 2 — La solución (slides 4-7, 6 minutos)

> *"Apliqué la metodología estándar CRISP-DM en seis fases. Integré cuatro fuentes en un dataset de un millón de filas. Comparé tres modelos en dos plataformas para validar la consistencia del pipeline. El Random Forest gana con AUC 0,895."*

Aquí toca demostrar el trabajo, las decisiones y los resultados. Pero **sin entrar en código**.

### Acto 3 — El producto y los hallazgos (slides 8-10, 4 minutos)

> *"El modelo no se queda en un notebook. Está desplegado en BigQuery y se consume desde un dashboard de Power BI que cualquier persona puede usar. Y al analizarlo descubrí algo curioso: parece que la lluvia atrae turistas, pero en realidad es una correlación espuria con Navidad."*

Cierre con el hallazgo no obvio, que demuestra criterio analítico y diferencia tu defensa.

### Acto 4 — Cierre (slide 11, 1 minuto)

> *"El modelo cumple los umbrales del curso con holgura. La feature más predictiva es la popularidad histórica del piso. La limitación principal es el cold start, que abre la línea de mejora futura. Gracias, ¿preguntas?"*

Cierre + apertura al Q&A.

---

## Reglas de calidad para los gráficos

El enunciado dice **"los gráficos deben entenderse a los 5 segundos"**. Aplicar estos principios:

### Reglas obligatorias

- **Un mensaje por gráfico.** Si necesitas explicar dos cosas, son dos gráficos.
- **Título descriptivo del mensaje, no del dato.** "Random Forest supera los umbrales del curso" en lugar de "Métricas del modelo".
- **Resaltar lo importante en color.** Todo en gris claro excepto la barra/línea/punto que cuenta tu historia.
- **Quitar lo decorativo.** Sin gridlines innecesarias, sin sombras, sin 3D, sin leyendas redundantes.
- **Tipografía grande.** Si el tribunal está al fondo del aula, los números tienen que verse.
- **Etiquetas directas en el gráfico**, no en una leyenda separada cuando sea posible.

### Gráficos imprescindibles

| Gráfico | Diapositiva | Mensaje |
|---|---|---|
| Tabla comparativa de modelos | 6 | "Random Forest gana con AUC 0,895" |
| Curva ROC (Orange) | 7 | "Los tres modelos discriminan muy bien (curvas pegadas a la esquina)" |
| Matriz de confusión | 7 | "Errores casi simétricos: modelo equilibrado" |
| Evolución temporal de ocupación | 8 | "El pico de Navidad domina el horizonte" |
| Ranking de distritos | 8 | "Sarrià lidera la ocupación turística" |
| Tabla AUC/F1/Accuracy/MCC | 7 | "Cumplo los umbrales del curso con holgura" |

### Gráficos que **NO** debes incluir

- Pie charts con más de 4 categorías.
- Tablas con más de 5 columnas o 10 filas.
- Capturas de código (a menos que sea muy puntual y muestre una decisión clave).
- Diagramas de arquitectura demasiado complejos (3-4 cajas máximo).

---

## Detalle por diapositiva

### Diapositiva 1 — Portada (0:30)

**Contenido:**

- Título: *"Predictor de Ocupación para Apartamentos Turísticos en Barcelona"*
- Subtítulo: *"Proyecto Final — Big Data e Inteligencia Artificial"*
- Autor: Dasbits
- Curso e IFP España, 2025-2026

**Frase de apertura:**

> *"Buenos días. Voy a presentar mi proyecto final, un predictor de ocupación de apartamentos turísticos en Barcelona basado en datos públicos de Inside Airbnb y aprendizaje automático."*

### Diapositiva 2 — El problema y el pivot (1:30)

**Contenido visual:**

- Captura de la columna `price` vacía en el dataset, con `NaN NaN NaN…` resaltado.
- Flecha del esquema: "Predictor de Precio" → "Predictor de Ocupación".

**Qué decir:**

> *"El enunciado original pedía predecir el precio. Pero al cargar los datos de Inside Airbnb descubrí que la columna `price` está completamente vacía desde 2024 por restricciones legales. Lo documenté en la fase de Data Understanding y pivoté la tarea hacia un Predictor de Ocupación: clasificación binaria sobre si un piso estará reservado o libre. Mantuve todo el stack y la metodología — solo cambia la tarea."*

### Diapositiva 3 — Las cuatro fuentes (1:30)

**Contenido visual:** cuatro logos/iconos en cuatro cajas (Inside Airbnb, Open-Meteo, Ticketmaster, festivos catalanes) con una flecha que confluye en una caja final "Dataset integrado · 1.012.783 filas".

**Qué decir:**

> *"El dataset combina cuatro fuentes públicas: Inside Airbnb aporta los listings y los calendarios, Open-Meteo aporta el clima diario, Ticketmaster los eventos y manualmente codifiqué los festivos catalanes. Después de la limpieza e integración tengo un millón de filas con granularidad piso-por-día."*

### Diapositiva 4 — CRISP-DM (1:00)

**Contenido visual:** seis cajas en círculo o secuencia: Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment. Cada caja con el icono de su entregable principal.

**Qué decir:**

> *"Apliqué la metodología estándar CRISP-DM en sus seis fases. Cada fase tiene su entregable identificable: notebooks 01-05 cubren las cuatro primeras, Orange y Power BI cierran Evaluation y Deployment."*

### Diapositiva 5 — Cifras del dataset (1:00)

**Contenido visual:** tarjetas KPI grandes con los cuatro números clave:

- 18.172 listings
- 1.012.783 filas
- 56 días de horizonte
- 4 fuentes integradas

**Qué decir:**

> *"Estas son las cifras del dataset modelado. Un millón de filas, cada una representando una noche concreta de un piso, sobre un horizonte de ocho semanas que cubre la temporada navideña y el inicio de febrero."*

### Diapositiva 6 — Tres modelos (2:00)

**Contenido visual:** tres tarjetas en horizontal con icono, nombre y una frase corta:

- **Logistic Regression** — el modelo lineal de referencia
- **Random Forest** — el ensemble por bagging (← marcado como ganador)
- **Gradient Boosting** — el ensemble por boosting iterativo

**Qué decir:**

> *"Comparé tres modelos que representan los tres paradigmas estándar de clasificación tabular: lineal, bagging y boosting. Los entrené en scikit-learn (notebook 05) y los repliqué en Orange Data Mining para validar la consistencia del pipeline. El ganador fue Random Forest."*

### Diapositiva 7 — Métricas finales (2:00)

**Contenido visual (dos elementos en la misma slide):**

- Tabla pequeña: modelo / AUC / F1, con la fila del Random Forest resaltada.
- Curva ROC capturada de Orange con las tres curvas casi superpuestas.

**Qué decir:**

> *"Random Forest da AUC 0,895 y F1 0,812 en el test, superando los umbrales del curso (F1 ≥ 0,75 y AUC ≥ 0,80) con holgura. En la curva ROC se ve que los tres modelos tienen capacidad discriminativa muy similar: las tres curvas están casi superpuestas y pegadas a la esquina superior izquierda."*

### Diapositiva 8 — Demo Power BI (2:30)

**No usar slide estática — abrir Power BI en directo.**

**Qué hacer físicamente:**

1. Abrir página "Visión general". Señalar las cuatro tarjetas KPI.
2. Mover el slicer temporal a la semana de Navidad. Mostrar cómo cambian todos los visuales.
3. Cambiar a página "Mercado". Alternar el slicer "Solo pisos enteros". Mostrar cómo cambia el ranking de barrios.
4. Cambiar a página "Clima". Señalar la nota didáctica sobre confounding.

**Qué decir:**

> *"El modelo no se queda en código. El dataset está en Google BigQuery y este dashboard de Power BI lo consume directamente. Cualquier usuario sin conocimientos técnicos puede explorar el mercado. Mira lo que pasa si filtro solo Navidad… o si me quedo con los pisos enteros para ver el ranking real del mercado turístico."*

### Diapositiva 9 — Hallazgo curioso (1:00)

**Contenido visual:** captura del gráfico de "Ocupación con vs sin lluvia" del dashboard, con la nota didáctica sobre confounding temporal.

**Qué decir:**

> *"Aquí hay un hallazgo bonito que descubrí analizando el dataset. Aparentemente, los días lluviosos tienen más ocupación que los secos. Suena raro. Y lo es: no es causalidad. Los días lluviosos del horizonte coinciden con la semana de Navidad, donde hay más demanda turística por motivos completamente independientes del tiempo. Es un ejemplo de correlación espuria mediada por una tercera variable, la fecha. Y demuestra que mirar los datos sin pensar puede llevarte a conclusiones equivocadas."*

### Diapositiva 10 — Conclusiones y mejoras (1:00)

**Contenido visual:** dos columnas:

- **Conclusiones:** cumple umbrales, popularidad histórica predice mejor, pipeline validado en dos plataformas, deployment funcional.
- **Mejoras futuras:** XGBoost/LightGBM, modelo cold start para listings nuevos, ampliación temporal, API REST.

**Qué decir:**

> *"Las tres conclusiones principales: cumplo los umbrales del curso con holgura, la popularidad histórica de cada piso es la feature más predictiva, y el sistema completo es reproducible. Como líneas de mejora, probaría XGBoost, construiría un modelo específico para cold start y ampliaría el horizonte temporal con varios scrapes."*

### Diapositiva 11 — Cierre y preguntas (1:00)

**Contenido visual:** el QR del repositorio en GitHub o el link.

**Frase de cierre memorable:**

> *"Para resumir: empecé queriendo predecir precios, terminé prediciendo ocupación con AUC 0,895. El proyecto está totalmente documentado, reproducible y desplegado. Gracias por la atención, abierto a preguntas."*

---

## Consejos de presentación oral

- **Habla en voz alta antes** al menos dos veces para encajar bien los tiempos de cada diapositiva.
- **No leas la pantalla** — el tribunal ya la ve. Tú miras al frente y la pantalla la usas como guía visual.
- **No te apoyes contra la mesa ni te metas las manos en los bolsillos.**
- **Pausa entre cifras importantes:** "AUC… 0,895." da más peso que "AUC0coma895".
- **Si te bloqueas**, di "voy a comentar la siguiente diapositiva" y avanza. Mejor avanzar que quedarse mudo.

---

## Tres preguntas que casi seguro te van a hacer

1. **¿Por qué tres modelos y no más?** → *"Porque representan los tres paradigmas estándar de clasificación tabular: lineal, bagging y boosting. Cubren el espectro completo de complejidad. Probar XGBoost queda como línea de mejora futura."*

2. **¿Qué es target encoding y por qué fue tan importante?** → *"Es codificar una categoría como la media del target en ese grupo. Sustituyo el `listing_id` por la media de ocupación de ese listing en el train. Es la feature más predictiva del modelo con importancia 0,66 sobre 1,0. La calculé solo con datos de train para evitar leakage hacia test."*

3. **¿Cuáles son las limitaciones del modelo?** → *"Cuatro principales: la ambigüedad de `available='f'` que mezcla reserva con bloqueo, la dependencia del `listing_te` que falla con cold start, el horizonte limitado a 56 días que no permite extrapolar a otras temporadas, y el sesgo del primer día del scrape. Todas están documentadas en la memoria final."*

---

**Autor:** Dasbits — Curso Big Data e Inteligencia Artificial, IFP España (2025-2026)
