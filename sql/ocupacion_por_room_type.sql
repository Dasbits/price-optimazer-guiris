-- =====================================================================
-- ocupacion_por_room_type.sql
-- ---------------------------------------------------------------------
-- KPI de ocupación por tipo de alojamiento (room_type).
-- Inside Airbnb diferencia 4 tipos: Entire home/apt, Private room,
-- Hotel room y Shared room.
--
-- Métricas:
--   * listings              - listings distintos en cada categoría
--   * pct_listings          - peso de la categoría sobre el total (oferta)
--   * pct_ocupacion         - tasa media de ocupación
--   * pct_ocupacion_finde   - ocupación restringida a sábados y domingos
--   * pct_ocupacion_navidad - ocupación durante 14/12/2025 - 06/01/2026
--   * pct_ocupacion_resto   - ocupación fuera de Navidad (resto del horizonte)
--
-- Uso en Power BI:
--   Tarjetas + treemap o barras apiladas comparando categorías.
--
-- =====================================================================

WITH base AS (
  SELECT
    room_type,
    listing_id,
    occupied,
    is_weekend,
    -- Marcamos los días considerados temporada de Navidad/Reyes
    IF(date BETWEEN DATE '2025-12-14' AND DATE '2026-01-06', 1, 0) AS es_navidad
  FROM `price-optimizer-bcn.datos.fact_ocupacion`
)

SELECT
  room_type,
  COUNT(DISTINCT listing_id)                                       AS listings,
  ROUND(
    COUNT(DISTINCT listing_id) * 100.0 /
      SUM(COUNT(DISTINCT listing_id)) OVER (),
    2
  )                                                                AS pct_listings,
  ROUND(AVG(occupied) * 100, 2)                                    AS pct_ocupacion,
  ROUND(AVG(IF(is_weekend = 1, occupied, NULL)) * 100, 2)          AS pct_ocupacion_finde,
  ROUND(AVG(IF(es_navidad = 1, occupied, NULL)) * 100, 2)          AS pct_ocupacion_navidad,
  ROUND(AVG(IF(es_navidad = 0, occupied, NULL)) * 100, 2)          AS pct_ocupacion_resto
FROM base
GROUP BY room_type
ORDER BY listings DESC
;
