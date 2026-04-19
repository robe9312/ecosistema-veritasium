# 🌌 Ecosistema-Veritasium
### Trading Algorítmico Autónomo · Solana Mainnet · OpenFang + Groq AI

[![Bot Status](https://img.shields.io/github/actions/workflow/status/TU_USUARIO/ecosistema-veritasium/trading_bot.yml?label=🤖%20Bot%20Status&style=for-the-badge)](../../actions/workflows/trading_bot.yml)
[![Runs on Groq](https://img.shields.io/badge/AI-Groq%20Llama--3.3--70b-orange?style=for-the-badge)](https://groq.com)
[![Solana](https://img.shields.io/badge/Blockchain-Solana%20Mainnet-9945FF?style=for-the-badge)](https://solana.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🧠 ¿Qué es Ecosistema-Veritasium?

Un sistema de trading algorítmico **completamente autónomo** que opera 24/7 en **GitHub Actions** sin necesidad de un servidor ni tu laptop encendida. Usa:

- 🤖 **OpenFang** — Motor de agentes de IA escrito en Rust
- 🦙 **Groq + Llama-3.3-70b** — Inferencia ultra-rápida y gratuita
- 🌊 **Solana Mainnet** — Blockchain de alta velocidad y bajo costo
- 🪐 **Jupiter Aggregator** — Mejor precio para swaps SOL/USDC
- 📊 **Z-Score Mean Reversion** — Estrategia estadística probada

**Costo de operación: $0 USD** (todo en capas gratuitas)

---

## 🏗️ Arquitectura del Sistema

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
(Llama)    (Helius/QuickNode)
    │         │
    ▼         ▼
 Análisis   Jupiter
 Z-Score     DEX
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

## ⚡ Configuración Rápida (5 pasos)

### Paso 1: Fork e inicializar el repositorio

```bash
# Clona el repositorio en tu máquina local
git clone https://github.com/TU_USUARIO/ecosistema-veritasium.git
cd ecosistema-veritasium

# El repositorio ya está listo para usar
# Solo necesitas configurar los secrets
```

### Paso 2: Obtener las credenciales necesarias

#### 🔑 GROQ_API_KEY (Gratuito)
1. Ve a [console.groq.com](https://console.groq.com)
2. Crea una cuenta gratuita
3. Ve a **API Keys** → **Create API Key**
4. Copia la key (empieza con `gsk_...`)
5. La capa gratuita incluye: 6,000 tokens/min y 30 req/min ✅

#### 💰 SOLANA_PRIVATE_KEY (Tu wallet de trading)
> ⚠️ **IMPORTANTE:** Usa una wallet NUEVA y separada, NUNCA tu wallet principal.

```bash
# Opción A: Usando Solana CLI
solana-keygen new --outfile trading-wallet.json
# La clave privada es el array de bytes en el JSON
# Conviértela a base58: cat trading-wallet.json | python3 -c "import sys,json,base58; k=json.load(sys.stdin); print(base58.b58encode(bytes(k)).decode())"

# Opción B: Usando Phantom/Solflare
# Exporta la clave privada desde Settings → Security → Export Private Key
```

**Formato aceptado:** Base58 o array de bytes JSON

#### 🌐 SOLANA_RPC_URL (Gratuito)
Elige uno de los siguientes proveedores gratuitos:

| Proveedor | URL Gratuita | Límite |
|-----------|-------------|--------|
| **Helius** | `https://mainnet.helius-rpc.com/?api-key=TU_KEY` | 100K req/día |
| **QuickNode** | `https://tus-endpoints.quicknode.pro/TU_KEY` | 10M créditos/mes |
| **Alchemy** | `https://solana-mainnet.g.alchemy.com/v2/TU_KEY` | 300M compute units |
| **Ankr** (sin key) | `https://rpc.ankr.com/solana` | ~100 req/seg público |

**Recomendado:** [Helius](https://helius.dev) — La mejor capa gratuita para Solana.

#### 💸 PROFIT_WALLET (Wallet del Bot 3)
La dirección pública de Solana donde se enviará el 20% de las ganancias.
Ejemplo: `7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`

### Paso 3: Configurar los Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Haz clic en **Settings** (pestaña, no ícono)
3. En el menú izquierdo: **Secrets and variables** → **Actions**
4. Haz clic en **New repository secret** para cada uno:

| Secret Name | Valor | Obligatorio |
|-------------|-------|-------------|
| `GROQ_API_KEY` | Tu API key de Groq | ✅ Sí |
| `SOLANA_PRIVATE_KEY` | Clave privada de tu wallet | ✅ Sí |
| `SOLANA_RPC_URL` | URL de tu RPC endpoint | ✅ Sí |
| `PROFIT_WALLET` | Dirección pública de Bot 3 | ✅ Sí |
| `WEBHOOK_URL` | URL de Discord/Slack webhook | ❌ Opcional |

### Paso 4: Fondear la wallet de trading

Envía SOL a la wallet de trading. Recomendaciones:
- **Mínimo para operar:** 0.5 SOL (~$75 USD)
- **Óptimo inicial:** 1-2 SOL (~$150-300 USD)
- **El bot reserva siempre 0.02 SOL para fees de transacción**

**Nunca envíes más de lo que puedas permitirte perder.**

### Paso 5: Activar el bot

```bash
# Opción A: Push al repositorio (activa el workflow automáticamente)
git add .
git commit -m "🚀 Activar Ecosistema-Veritasium"
git push origin main

# Opción B: Ejecución manual (para probar)
# GitHub → Actions → "Veritasium Trading Engine" → "Run workflow"
# Selecciona modo: "dry-run" para empezar sin riesgo real
```

---

## 🧪 Modo Dry-Run (Recomendado para empezar)

Antes de operar con dinero real, ejecuta 24-48 horas en modo simulación:

1. Ve a **Actions** → **Veritasium Trading Engine**
2. Haz clic en **Run workflow**
3. Selecciona `mode: dry-run`
4. Revisa los logs para verificar que todo funciona
5. Descarga los artefactos de logs para analizar las señales

---

## 📊 Monitoreo y Logs

### Ver logs en tiempo real
**GitHub** → **Actions** → Último workflow run → **Run Recolector Hand**

### Descargar logs históricos
**GitHub** → **Actions** → Workflow run → **Artifacts** → `trade-logs-XXX`

### Métricas almacenadas en SQLite
El archivo `.veritasium/state.db` se persiste entre ejecuciones mediante GitHub Cache.
Contiene toda la historia de trades, P&L diario y métricas de performance.

---

## 📁 Estructura del Proyecto

```
ecosistema-veritasium/
├── .github/
│   └── workflows/
│       └── trading_bot.yml       # 🔄 Workflow principal (cron cada 10 min)
├── hands/
│   └── recolector/
│       ├── HAND.toml             # 📋 Manifiesto y configuración del Bot 1
│       ├── prompt.txt            # 🧠 Sistema de prompts con lógica de trading
│       └── SKILL.md              # 📚 Base de conocimiento estadístico
├── config.toml                   # ⚙️  Configuración global de OpenFang
└── README.md                     # 📖 Esta guía
```

---

## 🛡️ Gestión de Riesgo

El bot tiene múltiples capas de protección:

| Protección | Valor | Descripción |
|------------|-------|-------------|
| Max por trade | 0.1 SOL | Tamaño máximo de cada operación |
| Max posición | 0.25 SOL | Capital máximo en riesgo simultáneo |
| Pérdida diaria | 0.05 SOL | Stop total del bot si se supera |
| Stop-Loss | -3.5σ | Cierre de emergencia de posición |
| Reserva fees | 0.02 SOL | Nunca se toca (para fees de red) |
| Max errores | 5 consecutivos | Detiene el bot para revisión |

---

## ⚠️ Advertencias Legales y de Riesgo

> **RIESGO FINANCIERO:** El trading de criptoactivos conlleva un alto riesgo de pérdida de capital. Las estrategias algorítmicas no garantizan rentabilidad. Solo opera con fondos que puedas permitirte perder completamente.

> **USO BAJO TU RESPONSABILIDAD:** Este software se proporciona "tal cual" sin garantías. El autor no es responsable de pérdidas financieras derivadas de su uso.

> **SEGURIDAD:** Nunca compartas tu `SOLANA_PRIVATE_KEY`. Los secrets de GitHub están encriptados pero es tu responsabilidad mantenerlos seguros.

> **REGULACIONES:** Verifica las regulaciones aplicables al trading automatizado de criptoactivos en tu jurisdicción.

---

## 🔧 Troubleshooting

### El workflow falla en "Validate required secrets"
→ Verifica que los 4 secrets obligatorios estén configurados correctamente.

### Error "RPC endpoint unreachable"
→ Tu SOLANA_RPC_URL puede haber expirado o alcanzado el límite. Regenera la key.

### Error "Insufficient balance"
→ El balance de SOL es menor a 0.02 (reserva mínima). Fondea la wallet.

### El bot no ejecuta trades en horas/días
→ Normal. La estrategia solo opera cuando Z-Score < -2σ o > +2σ. Paciencia.

### Error de Groq "Rate limit exceeded"
→ El bot reintentará automáticamente con backoff. Si persiste, ya se usará `llama-3.1-8b-instant` como fallback.

---

## 🗺️ Roadmap

- [x] Bot 1 (Recolector) — Mean Reversion Z-Score
- [ ] Bot 2 (Momentum) — Estrategia de seguimiento de tendencia
- [ ] Bot 3 (Acumulador) — Gestión del 20% de profits
- [ ] Dashboard web de métricas en tiempo real
- [ ] Integración con Telegram para alertas

---

*Ecosistema-Veritasium v1.0.0 — Construido con OpenFang + Groq + Solana*
