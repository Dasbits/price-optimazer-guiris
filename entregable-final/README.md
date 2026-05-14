# Entregable Final del Proyecto

> **Predictor de Ocupación para Apartamentos Turísticos en Barcelona**
> Big Data e Inteligencia Artificial · IFP España 2025-2026 · Dasbits

Esta carpeta contiene **todo lo que pide el enunciado del proyecto final**, organizado en cuatro piezas numeradas que mapean uno a uno con los cuatro puntos de los entregables.

---

## Contenido de la carpeta

```
entregable-final/
├── 1_informe_final.pdf              ← Informe final en PDF con todo el recorrido del proyecto
├── 2_codigo_proyecto.zip            ← ZIP con el código y los paquetes generados por cada herramienta
├── 3_README_proyecto.md/.pdf        ← README estructurado para el repositorio GitHub
├── 4_guia_presentacion.md/.pdf      ← Guía detallada de la presentación final (15 min)
└── README.md                        ← Este documento (índice del entregable)
```

---

## Mapeo con el enunciado oficial

### Punto 1 · Informe final en PDF con todo el recorrido del proyecto

**Fichero:** `1_informe_final.pdf` (~344 KB, 17 capítulos, ~40 páginas)

Es la memoria completa del proyecto convertida a PDF. Incluye portada, índice, resumen ejecutivo, las seis fases de CRISP-DM (Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment), resultados, conclusiones, limitaciones, bibliografía y anexos con la estructura del repositorio y los comandos de reproducción.

### Punto 2 · ZIP con el código desarrollado y todas las herramientas

**Fichero:** `2_codigo_proyecto.zip` (~16 MB, 41 entradas)

Contenido:

- **Python (notebooks Jupyter):** los cinco notebooks del flujo (descarga, exploración, limpieza, integración, modelado).
- **Python (scripts):** `sql/subir_dataset.py` y `orange/preparar_dataset_orange.py`.
- **Orange Data Mining:** `orange/pipeline_ocupacion.ows` + las cinco capturas de evaluación en `orange/images/`.
- **Power BI Desktop:** `powerbi/dashboard_ocupacion.pbix` con tres páginas interactivas.
- **SQL:** las tres queries de KPI para BigQuery + el script de subida.
- **Documentación:** todos los READMEs (principal, `orange/`, `powerbi/`, `data/`), la memoria final y los cortes intermedios.

**Excluido del ZIP** (por tamaño/licencia/seguridad):

- `data/` — datos descargados de Inside Airbnb (sus términos de uso prohíben redistribuir; se descargan manualmente).
- `.venv/` — entorno virtual de Python.
- `credentials.json` y `.env` — credenciales sensibles.
- Cachés (`__pycache__/`, `.ipynb_checkpoints/`).

### Punto 3 · Repositorio en GitHub

**Fichero:** `3_README_proyecto.md` (versión Markdown editable) y `3_README_proyecto.pdf` (versión imprimible).

Este es el README principal estructurado **como una web con menú desplegable**: una tabla de contenido con anchors al inicio que permite navegar a cualquiera de las seis secciones principales. Cubre lo que pide el enunciado:

1. Resumen / Abstract.
2. Introducción.
3. Desarrollo del proyecto en orden cronológico (las seis fases de CRISP-DM).
4. Conclusiones.
5. Bibliografía y referencias (fuentes de datos, documentación técnica, citas académicas, asistencia con IA).
6. Anexos (estructura del repositorio, comandos para reproducir el proyecto).

**Cuidado puesto en:**

- Redacción y ortografía revisadas.
- Tildes y eñes correctas en todo el documento.
- Tablas con datos numéricos formateados.
- Referencias correctamente atribuidas (autores, sitios web, IA utilizada).
- Imágenes y capturas referenciadas con rutas relativas dentro del repositorio.

**Para subir a GitHub:** el contenido de `3_README_proyecto.md` puede usarse directamente como el `README.md` raíz del repositorio. El repositorio en sí está estructurado en carpetas (`notebooks/`, `orange/`, `powerbi/`, `sql/`, `docs/`, `data/`) cada una con su propio README detallado para facilitar la navegación.

### Punto 4 · Presentación final (15 minutos)

**Fichero:** `4_guia_presentacion.md/.pdf`

**No es la presentación en sí** (eso se hace en PowerPoint o Google Slides), sino una **guía detallada para construirla y ejecutarla**:

- Estructura recomendada de 11 diapositivas con tiempos exactos sumando 15 minutos.
- Cómo contar la historia con datos en cuatro actos (problema, solución, producto, cierre).
- Reglas de calidad para los gráficos (entender en 5 segundos, un mensaje por gráfico, sin elementos decorativos).
- Detalle por diapositiva con contenido visual sugerido y frases para acompañar.
- Una demo en directo del dashboard Power BI (diapositiva 8).
- Consejos de presentación oral.
- Las tres preguntas más probables del tribunal con respuestas preparadas.

---

## Cómo usar este entregable

### Si tu profesor pide la entrega en formato físico o por email

Adjunta los cuatro ficheros principales:

- `1_informe_final.pdf`
- `2_codigo_proyecto.zip`
- `3_README_proyecto.pdf`
- `4_guia_presentacion.pdf` (opcional, es para ti)

### Si la entrega es vía GitHub

1. Sube el contenido de `2_codigo_proyecto.zip` (descomprimido) al repositorio.
2. Usa el contenido de `3_README_proyecto.md` como `README.md` raíz del repo.
3. Sube `1_informe_final.pdf` a la carpeta `docs/` del repo o como release attachment.

### Cómo preparar la presentación

1. Lee el documento `4_guia_presentacion.md` de principio a fin.
2. Construye las 11 diapositivas en PowerPoint o Google Slides siguiendo la estructura propuesta.
3. Ensaya en voz alta dos veces para encajar los tiempos.
4. Para la diapositiva 8, abre Power BI Desktop con el dashboard y haz una pequeña demo en directo.

---

## Verificación final antes de entregar

- [ ] `1_informe_final.pdf` se abre correctamente y tiene índice navegable.
- [ ] `2_codigo_proyecto.zip` se descomprime sin errores y contiene las 41 entradas esperadas (notebooks, scripts, queries, dashboard, capturas, READMEs y docs).
- [ ] `3_README_proyecto.md/.pdf` tiene las seis secciones (Resumen, Introducción, Desarrollo, Conclusiones, Bibliografía, Anexos).
- [ ] El repositorio en GitHub tiene su `README.md` raíz actualizado y todas las carpetas con sus READMEs correspondientes.
- [ ] La memoria menciona explícitamente el uso de Claude (IA) en la sección de bibliografía/referencias.
- [ ] La presentación final está construida y ensayada según `4_guia_presentacion.md`.

---

**Autor:** Dasbits — Curso Big Data e Inteligencia Artificial, IFP España (2025-2026)
