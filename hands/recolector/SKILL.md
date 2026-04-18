# SKILL.md — Base de Conocimiento: Recolector
## Estadística Aplicada al Trading de Criptoactivos

> Esta base de conocimiento es el "cerebro teórico" del agente RECOLECTOR.
> Toda decisión debe estar fundamentada en los principios aquí descritos.

---

## 1. FUNDAMENTOS ESTADÍSTICOS

### 1.1 Distribución Normal y la Regla Empírica

En mercados eficientes, los **retornos** tienden a distribuirse aproximadamente de forma normal:

```
Regla Empírica (68-95-99.7):
  ±1σ  → 68.27% de las observaciones
  ±2σ  → 95.45% de las observaciones
  ±3σ  → 99.73% de las observaciones
```

> ⚠️ Los precios de criptoactivos son **leptocúrticos** (colas gordas). Por eso usamos -2σ y no -1.5σ.

### 1.2 Z-Score

```
Z = (X - μ) / σ

X = precio actual
μ = SMA de los últimos N periodos
σ = desviación estándar del periodo

Z = 0:  precio en la media → equilibrio
Z = -2: sobreventa probable
Z = +2: sobrecompra probable
```

### 1.3 Desviación Estándar de la Muestra (usar N-1)

```python
# Siempre usar corrección de Bessel para muestras:
σ = sqrt(Σ(xi - x_bar)^2 / (N-1))
```

---

## 2. MEAN REVERSION: FUNDAMENTOS

### 2.1 ¿Qué es?

Activos que se desvían de su media histórica tienden a regresar a ella.

**Funciona mejor en:**
- Mercados ranging (sin tendencia clara)
- Alta liquidez
- Baja volatilidad macro

**FALLA en:**
- Tendencias fuertes (breakouts)
- Cisnes negros
- Baja liquidez

### 2.2 Half-Life de Mean Reversion

```
half_life = -ln(2) / β

β = coeficiente del proceso Ornstein-Uhlenbeck:
  ΔPt = α + β * Pt-1 + εt

Si β entre -0.1 y -0.001 → existe mean reversion
```

Para SOL en baja volatilidad: half-life típico = **15-45 minutos**.

---

## 3. GESTIÓN DE RIESGO

### 3.1 Kelly Criterion

```
Kelly% = W - (1-W)/R

W = win rate
R = reward/risk ratio

Kelly fraccional (recomendado):
  f* = Kelly% * 0.5  ← reducir volatilidad del capital
```

### 3.2 Value at Risk (VaR 95%)

```
VaR(95%) = μ_retorno - 1.645 * σ_retorno
```

### 3.3 Ratio de Sharpe

```
Sharpe = retorno_promedio / σ_retornos

Sharpe > 1.0 = aceptable
Sharpe > 2.0 = excelente (intraday)
```

---

## 4. LEYES DE POTENCIA EN CRIPTO

### 4.1 Fat Tails

```
P(X > x) ≈ x^(-α)

α para BTC/SOL ≈ 2.5 - 3.5
(distribución normal tendría α → ∞)
```

Los eventos de -4σ, -5σ ocurren más frecuentemente de lo esperado.
El stop-loss en -3.5σ es crítico.

### 4.2 Ley de Pareto

80% de las ganancias vienen del 20% de las operaciones:
- No forzar señales
- Dejar correr las ganancias
- Cortar rápido las pérdidas

---

## 5. JUPITER DEX

### 5.1 Price Impact

```
price_impact = |precio_real - precio_ref| / precio_ref * 100
Regla: RECHAZAR si price_impact > 1.0%
```

### 5.2 P&L real post-fees

```
profit_neto = (precio_venta - precio_compra) * cantidad_sol
            - (fees_compra + fees_venta)
            - (slippage_compra + slippage_venta)

fee_rate SOL ≈ 0.001-0.003% por trade
```

---

## 6. CONTEXTO SOL/USDC

- **Alta liquidez:** UTC 13:00-21:00 (sesión americana)
- **Baja liquidez:** UTC 00:00-08:00
- **Volatilidad diaria:** 3-8%
- **Correlación BTC:** ~0.7-0.9

**Mayor efectividad mean reversion:**
- UTC 05:00-09:00 y 14:00-18:00
- Mercado ranging sin noticias macro

**Riesgos Solana:**
1. Congestión de red → max_retries = 3
2. Jupiter sin ruta → verificar out_amount antes de firmar
3. MEV front-running → slippage 0.5% nos protege

---

## 7. PRINCIPIOS DEL TRADING CUANTITATIVO

> "El mercado puede permanecer irracional más tiempo del que puedes permanecer solvente." — Keynes

1. **Disciplina estadística sobre intuición**
2. **Gestión de riesgo primero** — la supervivencia del capital es prioritaria
3. **Humildad epistémica** — los modelos son aproximaciones
4. **Consistencia sobre brillantez** — Sharpe 1.5 sostenido > ganancia única del 100%
5. **Asimetría del riesgo** — perder 50% requiere ganar 100% para recuperarse

---

*SKILL.md — Veritasium v1.0.0*
