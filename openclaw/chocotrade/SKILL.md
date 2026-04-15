---
name: chocotrade
description: Official interface for the Chocotrade ecosystem. It serves as the primary gateway for market data and strategy analysis.
metadata: { "openclaw": { "requires": { "bins": ["conda", "python"], "env":[""]},"primaryEnv":"","hostEnv":"true" } }
---

# Chocotrade

Official interface for the Chocotrade ecosystem

## Usage

### Back‑test a symbol (required)
```bash
conda activate uv && python -m chocotrade openclaw --symbol <symbol>
```

### Interactive back‑test (no symbol given)
```bash
conda activate uv && python -m chocotrade openclaw
```

### List local Chocotrade data (new helper)
```bash
conda activate uv && python -m chocotrade test
```

## Interactive parameters
| Param  | Prompt | Type | Required | Default | Description |
|--------|--------|------|----------|---------|------------|
| symbol | 请告诉我你要回测的合约代码 | str | yes | - | 回测合约代码 |
