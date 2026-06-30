-- Average price per symbol (Athena-compatible: query table `ticks`)
SELECT
    symbol,
    ROUND(AVG(price), 2) AS avg_price
FROM ticks
GROUP BY symbol
ORDER BY symbol;
