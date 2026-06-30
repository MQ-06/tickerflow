-- Latest tick per symbol (Athena-compatible: query table `ticks`)
SELECT
    symbol,
    price,
    volume,
    timestamp,
    side
FROM (
    SELECT
        symbol,
        price,
        volume,
        timestamp,
        side,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY timestamp DESC
        ) AS rn
    FROM ticks
) ranked
WHERE rn = 1
ORDER BY symbol;
