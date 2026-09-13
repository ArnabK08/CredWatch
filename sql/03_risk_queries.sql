SELECT
    date(timestamp) AS txn_date,
    COUNT(transaction_id) AS total_transactions,
    SUM(amount) AS total_volume
FROM transactions
GROUP BY date(timestamp)
ORDER BY txn_date DESC
LIMIT 10;

SELECT
    account_id,
    transaction_id,
    amount,
    timestamp,
    COUNT(transaction_id) OVER (
        PARTITION BY account_id
        ORDER BY timestamp
    ) AS running_txn_count
FROM transactions
ORDER BY account_id, timestamp
LIMIT 20;

WITH HighValueTransactors AS (
    SELECT
        account_id,
        SUM(amount) AS total_sent_volume
    FROM transactions
    GROUP BY account_id
    HAVING SUM(amount) > 20000
),
RiskyBorrowers AS (
    SELECT
        account_id,
        credit_utilization,
        existing_defaults
    FROM accounts
    WHERE credit_utilization > 0.8 OR existing_defaults > 0
)
SELECT
    h.account_id,
    h.total_sent_volume,
    r.credit_utilization,
    r.existing_defaults
FROM HighValueTransactors h
JOIN RiskyBorrowers r ON h.account_id = r.account_id
ORDER BY h.total_sent_volume DESC
LIMIT 15;
