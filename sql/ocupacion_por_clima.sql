-- =====================================================================
-- ocupacion_por_clima.sql
-- ---------------------------------------------------------------------
-- Efecto del tiempo meteorológico sobre la ocupación.
-- Trabajamos con dos vistas:
--   1) Por categoría de clima (weather_cat): soleado / nublado / lluvia / extremo.
--   2) Por bins de temperatura media diaria (temp_avg).
--
-- IMPORTANTE: agregamos a nivel día (no listing-día) cuando lo que nos
-- interesa es el efecto del clima — si no, los barrios con muchos pisos
-- pesarían más solo por volumen.
--
-- Métricas:
--   * dias                  - días distintos en cada bucket
--   * pct_ocupacion_media   - ocupación media de los listings en esos días
--
-- Uso en Power BI:
--   Barras horizontales por categoría + scatter de temperatura vs ocupación.
--
-- =====================================================================

WITH ocup_diaria AS (
  -- Ocupación media de cada día (cada fila = un día)
  SELECT
    date,
    weather_cat,
    temp_avg,
    has_rain,
    AVG(occupied)                                                 AS pct_ocupado_dia
  FROM `price-optimizer-bcn.datos.fact_ocupacion`
  GROUP BY date, weather_cat, temp_avg, has_rain
)

-- Vista 1: ocupación por categoría de clima
SELECT
  'por_categoria'                               AS metrica,
  weather_cat                                   AS bucket,
  COUNT(*)                                      AS dias,
  ROUND(AVG(pct_ocupado_dia) * 100, 2)          AS pct_ocupacion_media
FROM ocup_diaria
GROUP BY weather_cat

UNION ALL

-- Vista 2: ocupación por bins de temperatura (5°C de ancho)
SELECT
  'por_temperatura'                             AS metrica,
  CONCAT(
    CAST(FLOOR(temp_avg / 5) * 5 AS STRING),
    ' a ',
    CAST(FLOOR(temp_avg / 5) * 5 + 5 AS STRING),
    ' C'
  )                                             AS bucket,
  COUNT(*)                                      AS dias,
  ROUND(AVG(pct_ocupado_dia) * 100, 2)          AS pct_ocupacion_media
FROM ocup_diaria
GROUP BY bucket

UNION ALL

-- Vista 3: con/sin lluvia
SELECT
  'por_lluvia'                                  AS metrica,
  IF(has_rain = 1, 'con lluvia', 'sin lluvia') AS bucket,
  COUNT(*)                                      AS dias,
  ROUND(AVG(pct_ocupado_dia) * 100, 2)          AS pct_ocupacion_media
FROM ocup_diaria
GROUP BY bucket

ORDER BY metrica, bucket
;
