# Guion rápido de defensa — Predictor de Ocupación Barcelona

> **Duración objetivo: 12-15 minutos.** Tener este documento impreso o en una pestaña aparte mientras hablas.

---

## Antes de empezar — ten todo abierto

- [ ] **VS Code** con el repo (README principal visible).
- [ ] **Navegador**: README en GitHub, BigQuery con la tabla `fact_ocupacion`, notebook 05.
- [ ] **Orange Data Mining** con `pipeline_ocupacion.ows` cargado y ejecutado (Test and Score con métricas visibles).
- [ ] **Power BI Desktop** con `dashboard_ocupacion.pbix` en la página Visión general.
- [ ] La memoria final en PDF abierta como respaldo.
- [ ] Las cinco capturas de `orange/images/` accesibles.

---

## Frase de apertura (memorizar)

> *"El proyecto era construir un Predictor de Precio Óptimo para apartamentos turísticos de Barcelona. Al analizar el scrape de Inside Airbnb del 14 de diciembre de 2025 descubrí que la columna `price` está 100 % vacía desde 2024. Pivoté el proyecto hacia un Predictor de Ocupación: clasificación binaria, manteniendo todo el stack y la metodología CRISP-DM."*

---

## Estructura por bloques

### Bloque 1 — Problema y pivot (~2 min)
**Visible:** README principal.

- Enunciado original: Predictor de Precio.
- Hallazgo crítico: columna `price` vacía.
- Decisión: pivot a Predictor de Ocupación.
- Target: `occupied` = 1 si `available='f'`, 0 si `available='t'`.

### Bloque 2 — Arquitectura general (~1 min)
**Visible:** sección "Estructura del proyecto" del README.

- CRISP-DM en sus 6 fases.
- 4 fuentes integradas: Inside Airbnb, Open-Meteo, Ticketmaster, festivos catalanes.
- Dataset integrado: 1.012.783 filas, granularidad listing × día.

### Bloque 3 — CRISP-DM fase a fase (~5-7 min)

| Fase | Material | Frase clave |
|---|---|---|
| **Data Understanding** | Notebook 02 | "Tres hallazgos críticos: price vacía, ambigüedad de available='f', desfase Ticketmaster." |
| **Data Preparation** | Notebooks 03 y 04 | "Limpieza por fuente, join a tres bandas, dataset final con cero nulos." |
| **Modeling** | Notebook 05 + Orange | "Tres modelos en dos plataformas. Anti-leakage, target encoding, one-hot. Split por fecha." |
| **Evaluation** | Orange (Test and Score) | "Random Forest gana con AUC=0.895 y F1=0.812. Supera los umbrales del curso." |
| **Deployment** | Power BI + BigQuery | "BigQuery + queries SQL + dashboard interactivo de 3 páginas." |

### Bloque 4 — Demo en vivo (~3 min)
**Visible:** Power BI Desktop, página Visión general.

1. Señalar las 4 tarjetas: 18.172 listings, 1M noches, 54,2 % ocupación, pico 76 %.
2. **Mover el slicer temporal** a la semana de Navidad → ocupación sube a ~65 %.
3. Cambiar a página **Mercado**, alternar slicer "Solo pisos enteros" → ranking de barrios cambia.
4. Cambiar a página **Clima**, leer la nota didáctica del confounding lluvia-Navidad.

### Bloque 5 — Cierre (~1 min)
**Visible:** sección de conclusiones de la memoria.

- El modelo cumple los dos umbrales del curso con holgura.
- La feature más predictiva es el target encoding por listing (popularidad histórica).
- Limitación honesta: degradaría con listings nuevos (cold start). Línea de mejora documentada.

---

## Métricas a saber de memoria

| Concepto | Valor |
|---|---:|
| Listings totales | **18.172** |
| Filas modeladas | **1.012.783** |
| Train / Test (split temporal) | **758.375 / 254.408** |
| % Ocupación medio | **54,2 %** |
| Pico ocupación (un día) | **76 %** |
| AUC Random Forest | **0,895** |
| F1 Random Forest | **0,812** |
| Accuracy Random Forest | **0,812** |
| Umbral F1 del curso | ≥ 0,75 |
| Umbral AUC del curso | ≥ 0,80 |
| Importance de `listing_te` | **0,66** sobre 1,0 |

---

## Las 5 frases salvavidas

- *"Es un problema de clasificación binaria supervisada."*
- *"Validación con split temporal, no aleatorio, para simular predicción real."*
- *"Eliminé las columnas `availability_*` por leakage."*
- *"Target encoding calculado solo sobre train para no contaminar el test."*
- *"Cumplo los dos umbrales del curso con holgura."*

---

## Recurso de emergencia

Si te quedas en blanco, dí: **"Déjame mostrar el README principal — ahí tengo el resumen completo del proyecto"** y abre el README. Tiene toda la información organizada y te sirve de mapa.
