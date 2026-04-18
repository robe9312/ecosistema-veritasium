# 🌌 Ecosistema-Veritasium
### Trading Algorítmico Autónomo · Solana Mainnet · OpenFang + Groq AI

[![Bot Status](https://img.shields.io/github/actions/workflow/status/robe9312/ecosistema-veritasium/trading_bot.yml?label=🤖%20Bot%20Status&style=for-the-badge)](../../actions/workflows/trading_bot.yml)
[![Runs on Groq](https://img.shields.io/badge/AI-Groq%20Llama--3.3--70b-orange?style=for-the-badge)](https://groq.com)
[![Solana](https://img.shields.io/badge/Blockchain-Solana%20Mainnet-9945FF?style=for-the-badge)](https://solana.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🧠 ¿Qué es Ecosistema-Veritasium?

Sistema de trading algorítmico **completamente autónomo** que opera 24/7 en **GitHub Actions** sin servidor ni laptop encendida.

- 🤖 **OpenFang** — Motor de agentes de IA en Rust
- 🦙 **Groq + Llama-3.3-70b** — Inferencia ultra-rápida y gratuita
- 🌊 **Solana Mainnet** — Blockchain de alta velocidad
- 🪐 **Jupiter Aggregator** — Mejor precio para swaps SOL/USDC
- 📊 **Z-Score Mean Reversion** — Estrategia estadística probada

**Costo de operación: $0 USD**

---

## 🏗️ Arquitectura

```
GitHub Actions (cron */10 min)
         │
         ▼
   OpenFang Runtime
         │
    ┌────┴────┐
    │         │
    ▼         ▼
Groq AI    Solana RPC
(Llama)    (Helius)
    │         │
    ▼         ▼
 Análisis   Jupiter DEX
 Z-Score    Swaps
    │         │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 Trades    20% Profit
 SQLite  → Bot 3 Wallet
```

---

## ⚡ Activación en 5 pasos

### Paso 1: Clonar
```bash
git clone https://github.com/robe9312/ecosistema-veritasium.git
cd ecosistema-veritasium
```

### Paso 2: Obtener credenciales

#### GROQ_API_KEY (Gratuito)
1. [console.groq.com](https://console.groq.com) → Create API Key
2. Capa gratuita: 6,000 tokens/min, 30 req/min ✅

#### SOLANA_PRIVATE_KEY
> ⚠️ Usa una wallet NUEVA. NUNCA tu wallet principal.

```bash
# Con Solana CLI:
solana-keygen new --outfile trading-wallet.json
# O exporta desde Phantom: Settings → Security → Export Private Key
```

#### SOLANA_RPC_URL (Gratuito)
| Proveedor | URL | Límite |
|-----------|-----|--------|
| **Helius** ⭐ | `https://mainnet.helius-rpc.com/?api-key=KEY` | 100K req/día |
| QuickNode | `https://endpoint.quicknode.pro/KEY` | 10M créditos/mes |
| Ankr (público) | `https://rpc.ankr.com/solana` | ~100 req/seg |

#### PROFIT_WALLET
Dirección pública Solana de tu wallet secundaria (Bot 3).

### Paso 3: Configurar Secrets en GitHub

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Obligatorio |
|--------|-------------|
| `GROQ_API_KEY` | ✅ Sí |
| `SOLANA_PRIVATE_KEY` | ✅ Sí |
| `SOLANA_RPC_URL` | ✅ Sí |
| `PROFIT_WALLET` | ✅ Sí |
| `WEBHOOK_URL` | ❌ Opcional |

### Paso 4: Fondear la wallet de trading
- **Mínimo:** 0.5 SOL (~$75 USD)
- **Óptimo:** 1-2 SOL (~$150-300 USD)
- El bot reserva 0.02 SOL para fees de red

> **Nunca envíes más de lo que puedas permitirte perder.**

### Paso 5: Activar
```bash
git push origin main  # El cron arranca automáticamente
```
O manualmente: **Actions → Veritasium Trading Engine → Run workflow**

---

## 🧪 Modo Dry-Run (Empieza aquí)

1. Actions → Run workflow → mode: `dry-run`
2. Observa 24-48 horas de señales simuladas
3. Descarga logs en Artifacts → `trade-logs-XXX`
4. Si todo se ve bien → cambia a `live`

---

## 🛡️ Gestión de Riesgo

| Protección | Valor | Descripción |
|------------|-------|-------------|
| Max por trade | 0.1 SOL | Por operación |
| Max posición | 0.25 SOL | En riesgo simultáneo |
| Pérdida diaria | 0.05 SOL | Auto-detención |
| Stop-Loss | -3.5σ | Cierre de emergencia |
| Reserva fees | 0.02 SOL | Intocable |
| Max errores | 5 consecutivos | Halt y revisión |

---

## 📊 Monitoreo

- **Logs en tiempo real:** Actions → último run → "Run Recolector Hand"
- **Historia de trades:** Artifacts → `trade-logs-XXX` (7 días de retención)
- **SQLite persistido** entre ejecuciones via GitHub Cache

---

## 🔧 Troubleshooting

| Error | Solución |
|-------|----------|
| "Validate required secrets" falla | Verifica los 4 secrets en Settings |
| "RPC endpoint unreachable" | Regenera tu API key del RPC |
| "Insufficient balance" | Fondea la wallet (min 0.02 SOL) |
| Sin trades por días | Normal — solo opera en Z < -2 o Z > +2 |
| Groq rate limit | El bot reintenta automáticamente con llama-3.1-8b |

---

## 🗺️ Roadmap

- [x] Bot 1 — Recolector (Mean Reversion Z-Score)
- [ ] Bot 2 — Momentum (seguimiento de tendencia)
- [ ] Bot 3 — Acumulador (gestión del 20% de profits)
- [ ] Dashboard web de métricas
- [ ] Alertas por Telegram

---

## ⚠️ Advertencias

> **RIESGO FINANCIERO:** El trading de criptoactivos implica riesgo de pérdida total. Solo opera con fondos que puedas perder completamente.

> **SEGURIDAD:** Jamás compartas tu `SOLANA_PRIVATE_KEY`.

> **REGULACIONES:** Verifica la legalidad del trading automatizado en tu jurisdicción.

---

*Ecosistema-Veritasium v1.0.0 — OpenFang + Groq + Solana*
