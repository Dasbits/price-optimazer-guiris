-- =====================================================================
-- ocupacion_por_barrio.sql
-- ---------------------------------------------------------------------
-- KPI de ocupación a nivel barrio (neighbourhood_cleansed) durante el
-- horizonte de 8 semanas analizado (14/12/2025 - 07/02/2026).
--
-- La query devuelve DOS rankings en una sola tabla, distinguidos por la
-- columna `segmento`:
--
--   * 'todo'             - todos los listings del barrio (cualquier tipo).
--   * 'entire_home'      - solo `Entire home/apt`, que representa el grueso
--                          del mercado turístico real.
--
-- Justificación: en barrios pequeños y residenciales (Montbau, Turó de la
-- Peira, Sant Genís) Inside Airbnb mezcla en `available='f'` los días
-- *reservados* y los *bloqueados por el anfitrión*. Eso infla la ocupación
-- aparente. Subimos el umbral mínimo a `listings >= 30` y añadimos la
-- vista filtrada a `Entire home/apt` para que el ranking refleje el
-- mercado turístico de verdad.
--
-- Métricas (idénticas en ambos segmentos):
--   * listings              - listings distintos en el barrio
--   * noches_total          - filas listing x día en el barrio
--   * noches_ocupadas       - SUM(occupied)
--   * pct_ocupacion         - tasa media de ocupación
--   * pct_ocupacion_finde   - ocupación solo en sábados y domingos
--   * delta_finde_pp        - puntos porcentuales que sube/baja el finde
--                             respecto al global del barrio
--
-- Uso en Power BI:
--   Filtrar por `segmento` para alternar entre las dos vistas. El visual
--   recomendado es un mapa coroplético + barras horizontales con top-N.
--
-- =====================================================================

WITH base AS (
  SELECT
    neighbourhood_group_cleansed AS distrito,
    neighbourhood_cleansed       AS barrio,
    listing_id,
    occupied,
    is_weekend,
    room_type
  FROM `price-optimizer-bcn.datos.fact_ocupacion`
)

-- ─────────────────────────────────────────────────────────────────
-- Segmento 1: ranking general (todos los room_type)
-- ─────────────────────────────────────────────────────────────────
SELECT
  'todo'                                                    AS segmento,
  distrito,
  barrio,
  COUNT(DISTINCT listing_id)                                AS listings,
  COUNT(*)                                                  AS noches_total,
  SUM(occupied)                                             AS noches_ocupadas,
  ROUND(AVG(occupied) * 100, 2)                             AS pct_ocupacion,
  ROUND(AVG(IF(is_weekend = 1, occupied, NULL)) * 100, 2)   AS pct_ocupacion_finde,
  ROUND(
    (AVG(IF(is_weekend = 1, occupied, NULL))
     - AVG(occupied)) * 100,
    2
  )                                                         AS delta_finde_pp
FROM base
GROUP BY distrito, barrio
HAVING listings >= 30   -- umbral subido para evitar barrios residenciales

UNION ALL

-- ─────────────────────────────────────────────────────────────────
-- Segmento 2: ranking restringido a Entire home/apt
-- ─────────────────────────────────────────────────────────────────
SELECT
  'entire_home'                                             AS segmento,
  distrito,
  barrio,
  COUNT(DISTINCT listing_id)                                AS listings,
  COUNT(*)                                                  AS noches_total,
  SUM(occupied)                                             AS noches_ocupadas,
  ROUND(AVG(occupied) * 100, 2)                             AS pct_ocupacion,
  ROUND(AVG(IF(is_weekend = 1, occupied, NULL)) * 100, 2)   AS pct_ocupacion_finde,
  ROUND(
    (AVG(IF(is_weekend = 1, occupied, NULL))
     - AVG(occupied)) * 100,
    2
  )                                                         AS delta_finde_pp
FROM base
WHERE room_type = 'Entire home/apt'
GROUP BY distrito, barrio
HAVING listings >= 30

ORDER BY segmento, pct_ocupacion DESC
;
