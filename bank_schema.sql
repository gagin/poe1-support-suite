-- bank.db schema: inventory snapshots + price observations + SQL valuation.
-- Conventions:
--   * `items.item_id` is canonical (trade-API name where one exists).
--   * Chaos Orb is the numeraire: every price is stored in chaos.
--     Convertible currencies (divine, exalted, ...) are themselves rows in
--     `prices` (e.g. item_id='Divine Orb', unit_chaos=10.4).
--   * `prices` is append-only; latest row per item wins.
--   * Staleness threshold lives in `config` so the SQL warning stays in SQL.

CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,
    display TEXT NOT NULL,
    kind    TEXT NOT NULL DEFAULT 'currency'  -- currency | omen | bone | tablet | misc
);

CREATE TABLE IF NOT EXISTS aliases (
    alias   TEXT PRIMARY KEY,   -- lowercased free-text shorthand
    item_id TEXT NOT NULL REFERENCES items(item_id)
);

CREATE TABLE IF NOT EXISTS inventory_snapshots (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    taken_at TEXT NOT NULL,
    note     TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS inventory_lines (
    snapshot_id INTEGER NOT NULL REFERENCES inventory_snapshots(id),
    item_id     TEXT NOT NULL REFERENCES items(item_id),
    qty         REAL NOT NULL,
    PRIMARY KEY (snapshot_id, item_id)
);

CREATE TABLE IF NOT EXISTS prices (
    item_id    TEXT NOT NULL REFERENCES items(item_id),
    unit_chaos REAL NOT NULL,
    n          INTEGER NOT NULL DEFAULT 0,   -- listings backing it (-1 = manual)
    src        TEXT NOT NULL DEFAULT '',
    fetched_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_prices_item_time
    ON prices(item_id, fetched_at DESC);

CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO config(key, value) VALUES ('price_max_age_h', '1.0')
    ON CONFLICT(key) DO NOTHING;
INSERT INTO config(key, value) VALUES ('voices_target_d', '359.0')
    ON CONFLICT(key) DO NOTHING;

-- Cost-basis lots (buy-and-hold thesis tracking). One row per buy;
-- qty_remaining drops on sells (FIFO). NULL unit_cost = unknown basis.
CREATE TABLE IF NOT EXISTS lots (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id       TEXT NOT NULL REFERENCES items(item_id),
    qty_bought    REAL NOT NULL,
    qty_remaining REAL NOT NULL,
    unit_cost_chaos REAL,
    acquired_at   TEXT NOT NULL,
    note          TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_lots_item ON lots(item_id);

-- Realized P&L, written by the sell command (FIFO cost captured then).
CREATE TABLE IF NOT EXISTS realized (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id         TEXT NOT NULL REFERENCES items(item_id),
    qty             REAL NOT NULL,
    unit_price_chaos REAL NOT NULL,
    unit_cost_chaos REAL,
    pnl_chaos       REAL,
    sold_at         TEXT NOT NULL,
    note            TEXT NOT NULL DEFAULT ''
);

-- Position P&L: basedqty, average cost, latest price, unrealized.
CREATE VIEW IF NOT EXISTS position_pnl AS
SELECT
    b.item_id,
    b.based_qty,
    b.basis_chaos,
    b.basis_chaos / NULLIF(b.based_qty, 0) AS avg_cost,
    lp.unit_chaos AS latest,
    (lp.unit_chaos - b.basis_chaos / NULLIF(b.based_qty, 0)) * b.based_qty
        AS unrealized_chaos,
    CASE WHEN b.basis_chaos AND b.basis_chaos > 0
         THEN (lp.unit_chaos / (b.basis_chaos / b.based_qty) - 1.0) * 100.0
         ELSE NULL END AS unrealized_pct
FROM (
    SELECT item_id,
           SUM(qty_remaining) AS based_qty,
           SUM(qty_remaining * unit_cost_chaos) AS basis_chaos
    FROM lots
    WHERE unit_cost_chaos IS NOT NULL AND qty_remaining > 0
    GROUP BY item_id
) b
LEFT JOIN latest_prices lp ON lp.item_id = b.item_id;

-- Latest known price per item, with age and staleness flag (pure SQL).
CREATE VIEW IF NOT EXISTS latest_prices AS
SELECT
    p.item_id,
    p.unit_chaos,
    p.n,
    p.src,
    p.fetched_at,
    (strftime('%s','now') - strftime('%s', p.fetched_at)) / 3600.0 AS age_h,
    CASE WHEN (strftime('%s','now') - strftime('%s', p.fetched_at)) / 3600.0
              > CAST((SELECT value FROM config
                      WHERE key = 'price_max_age_h') AS REAL)
         THEN 1 ELSE 0 END AS is_stale
FROM prices p
WHERE p.fetched_at = (
    SELECT MAX(p2.fetched_at) FROM prices p2 WHERE p2.item_id = p.item_id
);

-- Value one inventory snapshot at latest prices (pure SQL).
-- value_chaos NULL = no price ever recorded; is_stale / is_missing flag it.
CREATE VIEW IF NOT EXISTS snapshot_value AS
SELECT
    l.snapshot_id,
    l.item_id,
    l.qty,
    lp.unit_chaos,
    l.qty * lp.unit_chaos AS value_chaos,
    lp.fetched_at AS price_at,
    lp.age_h AS price_age_h,
    lp.src AS price_src,
    CASE WHEN lp.unit_chaos IS NULL THEN 1 ELSE 0 END AS is_missing,
    CASE WHEN lp.unit_chaos IS NULL THEN 0 ELSE lp.is_stale END AS is_stale
FROM inventory_lines l
LEFT JOIN latest_prices lp ON lp.item_id = l.item_id;

-- Snapshot totals in chaos and (via the divine price row) in divines.
CREATE VIEW IF NOT EXISTS snapshot_totals AS
SELECT
    v.snapshot_id,
    SUM(v.value_chaos) AS total_chaos,
    SUM(v.value_chaos) / NULLIF((
        SELECT unit_chaos FROM latest_prices WHERE item_id = 'Divine Orb'
    ), 0) AS total_div,
    SUM(v.value_chaos) / NULLIF((
        SELECT unit_chaos FROM latest_prices WHERE item_id = 'Divine Orb'
    ), 0) / CAST((SELECT value FROM config
                   WHERE key = 'voices_target_d') AS REAL) * 100.0
        AS voices_pct,
    SUM(v.is_missing) AS n_missing,
    SUM(v.is_stale) AS n_stale
FROM snapshot_value v
GROUP BY v.snapshot_id;
