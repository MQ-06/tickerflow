-- Tick count per symbol (Athena-compatible: query table `ticks`)
SELECT
    symbol,
    COUNT(*) AS tick_count
FROM ticks
GROUP BY symbol
ORDER BY symbol;
