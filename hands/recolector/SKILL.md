# SKILL.md — Base de Conocimiento: Recolector
## Estadística Aplicada al Trading de Criptoactivos

> Esta base de conocimiento es el "cerebro teórico" del agente RECOLECTOR.
> Toda decisión debe estar fundamentada en los principios aquí descritos.

---

## 1. FUNDAMENTOS ESTADÍSTICOS

### 1.1 Distribución Normal y la Regla Empírica

En mercados eficientes, los **retornos** (no los precios) tienden a distribuirse aproximadamente de forma normal. Esto nos permite usar la estadística paramétrica:

```
Regla Empírica (68-95-99.7):
  ±1σ  → 68.27% de las observaciones
  ±2σ  → 95.45% de las observaciones
  ±3σ  → 99.73% de las observaciones
```

**Implicación para trading:** Si el precio está a -2σ de la media, estadísticamente solo ocurre el 2.28% del tiempo. La probabilidad de reversión a la media es alta.

> ⚠️ **Caveat crítico:** Los precios de criptoactivos son **leptocúrticos** (colas gordas). Hay más eventos extremos de lo que predice la normal pura. Por eso usamos σ < -2.0 y no -1.5 como umbral.

### 1.2 Z-Score (Puntuación Estándar)

```
Z = (X - μ) / σ

Donde:
  X  = precio actual
  μ  = media de los últimos N periodos (SMA)
  σ  = desviación estándar de los últimos N periodos
```

**Interpretación:**
- Z = 0: precio exactamente en la media → equilibrio
- Z = -2: precio 2 desviaciones por debajo → posible sobreventa
- Z = +2: precio 2 desviaciones por encima → posible sobrecompra

### 1.3 Media Móvil Simple (SMA) vs Exponencial (EMA)

| | SMA | EMA |
|---|---|---|
| Reacción a cambios | Lenta, uniforme | Rápida, pondera más el presente |
| Para mean reversion | ✅ Mejor (evita over-fitting) | ❌ Puede crear señales falsas |
| Lag | Mayor | Menor |

**Usamos SMA-100** porque la mean reversion requiere una media estable que represente el precio "justo" de largo plazo en la ventana de análisis.

### 1.4 Desviación Estándar de la Muestra vs Población

```python
# Población (conoces todos los datos):
σ_población = sqrt(Σ(xi - μ)² / N)

# Muestra (trabajas con un subconjunto):
σ_muestra   = sqrt(Σ(xi - x̄)² / (N-1))  ← USAR ESTA (N-1 = corrección de Bessel)
```

Cuando trabajamos con ventanas de precios, **siempre usamos N-1** porque la muestra (100 velas) es una representación de una distribución subyacente mayor.

---

## 2. ESTRATEGIA MEAN REVERSION: FUNDAMENTOS

### 2.1 ¿Qué es Mean Reversion?

La hipótesis de mean reversion establece que los activos que se desvían significativamente de su valor promedio histórico tienen una tendencia probabilística a regresar a ese promedio. Es el opuesto a las estrategias de momentum.

**Condiciones donde funciona mejor:**
- Mercados con alta liquidez y baja tendencia (ranging)
- Pares con alta correlación con su propio promedio histórico
- Periodos de baja volatilidad macroeconómica

**Condiciones donde FALLA:**
- Mercados en tendencia fuerte (breakouts)
- Eventos de cisne negro (FTX collapse, regulaciones inesperadas)
- Baja liquidez (spreads amplios y manipulación de precios)

### 2.2 El Problema de la No-Estacionariedad

Los precios de criptoactivos NO son estacionarios en el largo plazo. Sin embargo, en ventanas cortas (100 minutos), podemos asumir **quasi-estacionariedad local**.

```
Test de Augmented Dickey-Fuller (ADF):
  - H₀: La serie tiene raíz unitaria (no estacionaria)
  - Si p-valor < 0.05: rechazar H₀ → serie estacionaria → mean reversion válida
  - Si p-valor > 0.05: no rechazar H₀ → cuidado con señales falsas
```

> **Nota práctica:** En ventanas de 100 minutos, SOL/USDC generalmente pasa el test ADF, especialmente en rangos de precios estables.

### 2.3 Half-Life de Mean Reversion

El half-life indica cuánto tiempo tarda el precio en recorrer la mitad de la distancia hacia la media:

```
half_life = -ln(2) / β

Donde β es el coeficiente del proceso de Ornstein-Uhlenbeck:
  ΔPt = α + β * Pt-1 + εt

Si β está entre -0.1 y -0.001:
  → Existe mean reversion
  → half_life = tiempo esperado de la operación
```

Para SOL en periodos de baja volatilidad, el half-life típico es de **15-45 minutos**.

---

## 3. GESTIÓN DE RIESGO

### 3.1 Kelly Criterion

El Kelly Criterion determina el tamaño óptimo de posición que maximiza el crecimiento del capital a largo plazo:

```
Kelly% = W - (1-W)/R

Donde:
  W = Probabilidad de ganancia (win rate)
  R = Razón de ganancia/pérdida (reward/risk ratio)

Kelly fraccional (recomendado para criptoactivos):
  f* = Kelly% * 0.5   ← usar 50% del Kelly para reducir volatilidad
```

**Ejemplo:**
- Win rate = 60%, R = 1.5
- Kelly% = 0.60 - 0.40/1.5 = 0.60 - 0.267 = 0.333 = 33.3%
- Kelly fraccional = 16.65% del capital por operación

### 3.2 Value at Risk (VaR) Simplificado

```
VaR(95%) = μ_retorno - 1.645 * σ_retorno

Interpretación: Con 95% de probabilidad, la pérdida máxima en 
un periodo no superará el VaR calculado.
```

El bot limita operaciones cuando el VaR proyectado supera el `daily_loss_limit_sol`.

### 3.3 Ratio de Sharpe (Aproximado)

```
Sharpe = (Retorno_promedio_por_ciclo - Tasa_libre_riesgo) / σ_retornos

Un Sharpe > 1.0 es aceptable
Un Sharpe > 2.0 es excelente para estrategias intraday
```

El agente calcula una aproximación del Sharpe al final de cada jornada con los datos históricos en SQLite.

---

## 4. LEYES DE POTENCIA EN CRIPTO

### 4.1 Distribuciones de Cola Gorda (Fat Tails)

Los mercados de criptoactivos siguen distribuciones de **ley de potencia** para eventos extremos, no distribuciones normales:

```
P(X > x) ≈ x^(-α)

Donde α (alpha de cola) para BTC/SOL ≈ 2.5 - 3.5
(normal tendría α → ∞)
```

**Implicación directa para RECOLECTOR:**
- Los eventos de -4σ, -5σ ocurren con frecuencia MUCHO mayor de lo esperado
- El stop-loss en -3.5σ es crítico: evita la catástrofe de la cola

### 4.2 La Ley de Pareto en Trading

El 80% de las ganancias suelen venir del 20% de las operaciones. Esto implica:
- No aumentar la frecuencia de operaciones artificialmente
- Dejar correr las ganancias (sell en +2σ, no antes)
- Cortar rápido las pérdidas (stop-loss estricto)

### 4.3 Hipótesis del Mercado Fractal (HMF)

A diferencia de la HME (Hipótesis del Mercado Eficiente), la HMF de Mandelbrot postula que los mercados son autosimilares a diferentes escalas temporales. 

**Aplicación práctica:** Los niveles de soporte y resistencia en marcos temporales mayores (1h, 4h) influyen en las señales de 1m. Al calcular el Z-Score de 100 minutos, estamos capturando la dinámica fractal del mercado a nivel intraday.

---

## 5. COMPORTAMIENTO DE JUPITER DEX

### 5.1 Precio de Impacto (Price Impact)

```
price_impact = |precio_real_swap - precio_referencia| / precio_referencia * 100

Regla del bot: NUNCA ejecutar si price_impact > 1.0%
```

### 5.2 Slippage vs Price Impact

| Concepto | Definición | Control |
|----------|-----------|---------|
| **Slippage** | Diferencia entre precio esperado y ejecutado | `slippageBps = 50` (0.5%) |
| **Price Impact** | Efecto de tu orden en el precio de mercado | Tamaño máximo de operación |
| **Fees** | Comisiones de protocolo y red | ~0.001 SOL por txn en Solana |

### 5.3 Cálculo real de P&L post-fees

```
profit_neto = (precio_venta * cantidad_sol) 
            - (precio_compra * cantidad_sol)
            - (fees_compra + fees_venta)
            - (slippage_compra + slippage_venta)

Umbral de rentabilidad:
  precio_venta > precio_compra * (1 + 2*fee_rate + min_profit_target)
```

Para SOL en Solana: fee_rate ≈ 0.001 SOL (~0.001-0.003% del trade según tamaño).

---

## 6. CONTEXTO DEL MERCADO SOL/USDC

### 6.1 Características del Mercado

- **Liquidez:** Alta en horario UTC 13:00-21:00 (sesión americana), baja en UTC 00:00-08:00
- **Volatilidad diaria:** Típicamente 3-8% (alta estabilidad comparada con altcoins)
- **Correlación con BTC:** ~0.7-0.9 (alta) → los movimientos de BTC afectan SOL
- **Volatilidad implícita:** Aumenta cerca de eventos macro (Fed, CPI, NFP)

### 6.2 Horas de Mayor Efectividad para Mean Reversion

La estrategia funciona mejor en:
- Mercados sin tendencia clara (range-bound)
- Volatilidad moderada (σ entre 0.5% y 3% de SMA)
- Horario: UTC 05:00-09:00 y UTC 14:00-18:00 (transiciones de sesión)

La estrategia tiene MENOR efectividad en:
- Apertura/cierre de mercados de futuros de CME (UTC 22:00)
- Primeros 30 minutos tras datos macro importantes
- Fin de semana (menor liquidez institucional)

### 6.3 Factores de Riesgo Específicos de Solana

1. **Congestión de red:** Solana puede tener transacciones fallidas en momentos de alta demanda. El bot tiene max_retries = 3.
2. **Validators downtime:** Raro pero posible. Verificar que el RPC endpoint responda antes de operar.
3. **Jupiter routing:** El agregador puede no encontrar ruta óptima. Verificar out_amount antes de firmar.
4. **MEV (Maximal Extractable Value):** Bots de front-running pueden afectar el slippage. El límite de 0.5% slippage nos protege.

---

## 7. PRINCIPIOS FILOSÓFICOS DEL TRADING CUANTITATIVO

> "El mercado puede permanecer irracional más tiempo del que puedes permanecer solvente."
> — John Maynard Keynes

**Principios que guían al agente RECOLECTOR:**

1. **Disciplina estadística sobre intuición:** Cada operación tiene un respaldo matemático.
2. **Gestión de riesgo primero:** La supervivencia del capital es la prioridad sobre la ganancia.
3. **Humildad epistémica:** Los modelos son aproximaciones de la realidad. No sobre-optimizar.
4. **Consistencia sobre brillantez:** Un Sharpe de 1.5 sostenido en el tiempo supera a una ganancia única del 100%.
5. **Asimetría del riesgo:** Perder el 50% requiere ganar el 100% para recuperarse. Evitar la ruina es lo primero.

---

*SKILL.md — Última actualización: Veritasium v1.0.0*
*© Ecosistema-Veritasium — Solo para uso educativo y personal*
