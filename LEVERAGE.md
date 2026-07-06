# Paper Battery Leverage Policy

**Applied:** 2026-07-07  
**Approach:** Recommended **5× notional scaling** on four delta-neutral strategy families only.  
**Not applied:** Full 10× everywhere.

Each strategy in the paper battery runs on an isolated **$10 ledger** (`START_BAL`). Scaling multiplies **position notional** (gross exposure per leg) while the ledger balance stays $10 — this is intentional paper sizing to measure edge at higher gross without changing account capital.

## Where the paper battery lives

| Location | Path | In git? |
|----------|------|---------|
| **VPS** (live paper service) | `/opt/deep-paper/server.mjs` | No — deployed directly on VPS |
| **VPS** (carry backtests) | `/opt/carry/carry_suite.py` | No — analysis only, no live notional |
| **Local repo** | — | **Not found** — no `carry_btc`, `funding_arb_xv`, etc. in this repository |

Search paths tried (local):

- `/Users/michael/Desktop/nautilus_trader` — full repo grep for `carry_btc`, `carry_eth`, `funding_arb_xv`, `spot_perp_arb`, `paper_battery`, `clip_size`, `inventory_cap`
- `nautilus_trader/examples/strategies/**` — ported folders only (freqtrade, chan, academic, etc.)

Search paths tried (VPS `root@80.208.228.117`):

- `/root/nautilus_trader` — upstream nautilus clone; no paper battery configs
- `/opt/deep-paper/` — **paper battery service** (modified)
- `/opt/carry/` — funding backtest suite (unchanged)

## Before / after (5× on four families)

| Strategy | Before | After 5× | Ledger | Status |
|----------|--------|----------|--------|--------|
| `carry_btc` / `carry_eth` | $10 spot + $10 perp | **$50 + $50** | $10 | **Scaled** |
| `funding_arb_xv` | $3 × 2 venues | **$15 × 2 venues** | $10 | **Scaled** |
| `spot_perp_arb` | $5 × 2 legs | **$25 × 2 legs** | $10 | **Scaled** |
| `carry_xsection` | 10 × $1 | 10 × $1 | $10 | Unchanged |
| `mm_queue_doge` | $2 clip, $6 cap | $2 clip, $6 cap | $10 | Unchanged |
| `mm_imbalance_btc` | $2 clip, $6 cap | $2 clip, $6 cap | $10 | Unchanged |
| `mm_basis_eth` | $2 clip, $6 cap | $2 clip, $6 cap | $10 | Unchanged |
| `xemm_bnb_bybit` | $2 clips | $2 clips | $10 | Unchanged |
| `xs_momentum` | max ~75% deployed | max ~75% deployed | $10 | Unchanged |

## Files changed

### VPS: `/opt/deep-paper/server.mjs`

Edits in strategy definitions only:

- **funding_arb_xv:** `notional: 3` → `15`, `legFee = 3 * 2` → `15 * 2`, Telegram `$3` → `$15`
- **carry_btc / carry_eth:** entry fees and funding multiplier `10` → `50`, description `$10` → `$50`
- **spot_perp_arb:** `notional: 5` → `25`, `legFee` base `5` → `25`, Telegram `$5` → `$25`

Unchanged lines (sanity check):

- `mmCycle(..., 2, 6)` — clip $2, inventory cap $6
- `carry_xsection` — `$1` per position (`qty: 1 / mark`, fees `1 * ...`)
- `xemm_bnb_bybit` — `clip = 2`
- `xs_momentum` — `w * START_BAL` (75% cap via `0.25` weight)

### Local repo

This file (`LEVERAGE.md`) only. Ported strategy folders (`freqtrade_ported/`, `chan_ported/`, etc.) were not modified.

## Restart after VPS edit

```bash
# On VPS — restart if a supervisor/systemd unit exists; otherwise:
pkill -f "/opt/deep-paper/server.mjs" || true
cd /opt/deep-paper && node server.mjs &
```

Existing `state.json` positions keep their prior notionals until closed/reopened.

## Recommended config template (if re-deploying)

```javascript
// 5× delta-neutral families only — do NOT scale mm_*, xemm, carry_xsection, xs_momentum
const CARRY_NOTIONAL = 50;        // was 10 per leg (spot + perp)
const FUNDING_ARB_NOTIONAL = 15;  // was 3 per venue
const SPOT_PERP_ARB_NOTIONAL = 25; // was 5 per leg pair
const START_BAL = 10;             // ledger unchanged
const MM_CLIP_USD = 2;            // unchanged
const MM_MAX_INV_USD = 6;         // unchanged
```

## Revert to unlevered sizing

Restore prior values in `server.mjs`:

- carry: `50` → `10`
- funding_arb_xv: `15` → `3`
- spot_perp_arb: `25` → `5`
