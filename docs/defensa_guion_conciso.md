# Guion conciso de defensa — Predictor de Ocupación Barcelona

> **Objetivo:** explicar el proyecto en **5-7 minutos** sin entrar en detalles técnicos. Filosofía: planteamiento → soluciones → conclusiones.

---

## 1. PLANTEAMIENTO (1-2 min)

**Qué problema había:**

- El proyecto era construir un **predictor de precio** para apartamentos turísticos de Airbnb en Barcelona.
- Descargué los datos de Inside Airbnb del 14 de diciembre de 2025 y descubrí un problema crítico: **la columna `price` estaba 100 % vacía**. Inside Airbnb dejó de publicarla en 2024 por restricciones legales.
- Sin la columna `price`, la tarea original era inviable.

**Qué decidí hacer:**

- **Pivoté el proyecto** a un **predictor de ocupación**: en lugar de predecir el precio, predigo si una noche concreta de un piso estará reservada o libre.
- Cambia la tarea (de regresión a clasificación binaria) pero **mantuve toda la infraestructura del proyecto**: misma metodología, mismos datos, mismas herramientas.

---

## 2. SOLUCIONES (3-4 min)

**Qué construí:**

- **Un dataset integrado** combinando cuatro fuentes: Inside Airbnb (los pisos y sus calendarios), Open-Meteo (clima de Barcelona día a día), Ticketmaster (eventos), y festivos catalanes. Resultado: **1 millón de filas**, una por cada combinación de piso y día.

- **Tres modelos de Machine Learning** para comparar y elegir el mejor:
  - Regresión Logística (modelo lineal de referencia).
  - Random Forest (modelo no lineal robusto).
  - Gradient Boosting (modelo iterativo potente).

- **Dos implementaciones en paralelo:**
  - Una **programática** en Python con scikit-learn (notebook 05).
  - Una **visual** en Orange Data Mining (flujo de widgets sin código).
  - Sirve como validación cruzada: si los dos dan lo mismo, el pipeline está bien.

- **Una capa de explotación** para usuarios no técnicos:
  - El dataset sube a **Google BigQuery** como tabla cloud consultable con SQL.
  - Tres queries SQL sirven de capa de KPIs (por barrio, por tipo de alojamiento, por clima).
  - Un **dashboard en Power BI** con tres páginas interactivas (Visión general, Mercado, Clima) conectadas a BigQuery.

**Cómo aseguré la calidad:**

- Seguí la metodología estándar **CRISP-DM**: cada decisión tiene su justificación documentada.
- **Documentación jerarquizada**: un README principal, dos READMEs especializados (uno para Orange, otro para Power BI), comentarios inline en código y queries.
- **Reproducibilidad total**: cualquiera que clone el repo puede regenerar todo desde cero ejecutando los notebooks en orden.

---

## 3. CONCLUSIONES Y SIGUIENTES PASOS (1 min)

**Qué obtuve:**

- El modelo ganador es **Random Forest** con:
  - **AUC = 0,895** (capacidad de discriminación: muy buena).
  - **F1 = 0,812** (equilibrio entre acierto y cobertura).
- **Supera con holgura los dos umbrales mínimos del curso** (F1 ≥ 0,75 y AUC ≥ 0,80).
- La feature más predictiva resultó ser la **popularidad histórica de cada piso**: el dato que mejor explica si un piso estará ocupado mañana es cuánto lo ha estado en el pasado.

**Qué hallazgo curioso documenté:**

- En la página de Clima del dashboard se ve que los días con lluvia tienen más ocupación que los días sin lluvia. **No es causalidad**: los días lluviosos del horizonte coinciden con Navidad, que tiene más demanda por motivos turísticos, no meteorológicos. Es un ejemplo de **correlación que no implica causalidad**, documentado explícitamente con una nota didáctica.

**Qué viene después / línea de mejora:**

- Probar modelos más avanzados (**XGBoost o LightGBM**) que podrían aportar uno o dos puntos extra en AUC.
- Construir un modelo específico para **listings nuevos sin historial** (lo que se llama *cold start*), porque el modelo actual depende mucho de la popularidad pasada.
- Acumular **varios scrapes mensuales** para ampliar el horizonte temporal y capturar variaciones estacionales más allá de los 56 días actuales.
- Desplegar el modelo como **API REST** para que aplicaciones externas puedan consumirlo.

---

## Frase de cierre

> *"En resumen: el proyecto siguió CRISP-DM en sus seis fases, integró cuatro fuentes de datos, entrenó tres modelos en dos plataformas para validarse cruzadamente y desplegó los resultados en una infraestructura cloud con un dashboard interactivo. El modelo cumple los objetivos del curso, está totalmente documentado y reproducible, y deja líneas claras de mejora futura."*
