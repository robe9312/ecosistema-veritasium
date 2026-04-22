# SKILL.md — Base de Conocimiento: Multiplicador (Bot 2)
## Distribuciones Log-Normales, Trend Following y Compounding Dinámico

> Esta base de conocimiento es el "cerebro teórico" del agente MULTIPLICADOR.
> Opera bajo la ley de efectos multiplicativos: captura tendencias persistentes
> y aplica interés compuesto para generar el crecimiento real de la cuenta.

---

## 1. FUNDAMENTOS MATEMÁTICOS: DISTRIBUCIÓN LOG-NORMAL

### 1.1 Por qué los precios son Log-Normales (no Normales)

El Bot 1 trabaja con **retornos** (que son aproximadamente normales).
El Bot 2 trabaja con **precios**, que no pueden ser negativos y siguen:

```
Si los retornos r_t ~ N(μ, σ²)
Entonces los precios P_t ~ LogNormal(μ_LN, σ_LN²)

P_t = P_0 · exp(μ·t + σ·W_t)

Donde W_t es un movimiento Browniano estándar.
```

**Implicación directa para trading:**
- Los movimientos de precio son *multiplicativos*, no aditivos
- Una subida del 10% seguida de una bajada del 10% NO regresa al precio inicial
  - Subida: 100 → 110 (+10%)
  - Bajada: 110 → 99 (-10%)
  - **Pérdida neta de 1%** — la asimetría multiplicativa es real

### 1.2 Retorno Geométrico vs Aritmético

```
Retorno aritmético (Bot 1 lo usa):  r_a = (P_t - P_0) / P_0
Retorno geométrico (Bot 2 lo usa):  r_g = ln(P_t / P_0)

Relación: r_g = ln(1 + r_a)

Para compounding: r_g = μ - σ²/2  ← el término σ²/2 es el "costo de la volatilidad"
```

**Regla de oro del Multiplicador:**
> La volatilidad destruye el rendimiento compuesto. Reducir la posición cuando
> sube la volatilidad no es cobardía — es matemática pura.

### 1.3 Movimiento Browniano Geométrico (GBM)

El modelo de tendencia que sigue el Multiplicador:

```
dP = μ·P·dt + σ·P·dW

Donde:
  μ  = drift (tendencia esperada por unidad de tiempo)
  σ  = volatilidad (difusión)
  dW = ruido Browniano

Solución discreta (implementable):
  P_{t+1} = P_t · exp((μ - σ²/2)·Δt + σ·√Δt·ε_t)
  donde ε_t ~ N(0,1)
```

---

## 2. IDENTIFICACIÓN DE TENDENCIA: EL SISTEMA DE CONFIRMACIÓN TRIPLE

Para entrar, el Multiplicador requiere **los tres** factores alineados:

### 2.1 Factor 1 — Cruce de Medias (Dirección)

```
SMA_20 = media de los últimos 20 cierres horarios
SMA_50 = media de los últimos 50 cierres horarios

Señal ALCISTA:  SMA_20 > SMA_50 AND precio > SMA_20
Señal BAJISTA:  SMA_20 < SMA_50 AND precio < SMA_20

Señal INVÁLIDA: SMA_20 ≈ SMA_50 (diferencia < 0.3%) → mercado en rango → no operar
```

### 2.2 Factor 2 — Exponente de Hurst (Persistencia)

El Exponente de Hurst mide si una serie temporal tiene memoria:

```
H > 0.55  →  Serie PERSISTENTE (tendencia) ← OPERAR
H = 0.50  →  Caminata aleatoria (ruido)    ← NO OPERAR
H < 0.45  →  Serie ANTIPERSISTENTE (mean reversion) ← TERRITORIO DEL BOT 1
```

**Cálculo con método R/S:**
```python
def hurst_rs(prices, min_lag=10, max_lag=None):
    n = len(prices)
    max_lag = max_lag or n // 2
    lags = np.logspace(1, np.log10(max_lag), 20).astype(int)
    rs_values = []
    for lag in lags:
        chunks = [prices[i:i+lag] for i in range(0, n-lag, lag)]
        rs_per_chunk = []
        for chunk in chunks:
            mean_c = np.mean(chunk)
            deviations = np.cumsum(chunk - mean_c)
            R = np.max(deviations) - np.min(deviations)
            S = np.std(chunk, ddof=1)
            if S > 0:
                rs_per_chunk.append(R / S)
        if rs_per_chunk:
            rs_values.append(np.mean(rs_per_chunk))
    if len(rs_values) >= 2:
        slope, _ = np.polyfit(np.log(lags[:len(rs_values)]), np.log(rs_values), 1)
        return slope
    return 0.5
```

### 2.3 Factor 3 — Volumen Creciente (Confirmación)

```
Volumen_promedio_20h = media de volumen de las últimas 20 velas horarias
Condición: volumen_actual > Volumen_promedio_20h × 1.2
(Al menos 20% por encima del promedio para confirmar la tendencia)
```

---

## 3. GESTIÓN DE POSICIÓN: PYRAMIDING SEGURO

El pyramiding (agregar a una posición ganadora) es la técnica que transforma
trend following en compounding real. Pero tiene reglas estrictas:

### 3.1 Regla de las 3 Entradas Máximas

```
Entrada 1 (Inicial):     0.25 SOL  →  solo si las 3 condiciones están alineadas
Entrada 2 (Pyramid 1):   0.15 SOL  →  solo si:
                                        a) Tendencia persiste (H > 0.55)
                                        b) Posición 1 en BREAK EVEN (stop movido al precio de entrada)
                                        c) Precio ≥ entrada_1 × 1.015 (al menos +1.5%)
Entrada 3 (Pyramid 2):   0.10 SOL  →  solo si:
                                        a) Posición 2 también en break even
                                        b) Precio ≥ entrada_2 × 1.015
                                        c) H sigue > 0.58

Total máximo: 0.50 SOL en posición completa (piramidada)
```

**Regla de hierro:** Nunca agregar a una posición perdedora.
**Regla de hierro:** Solo pyramid si el stop de la entrada anterior ya está en break even.

### 3.2 ATR para Dimensionamiento Dinámico

El Average True Range (ATR) es la medida correcta de volatilidad para position sizing:

```
True Range(t) = max(
    High(t) - Low(t),
    |High(t) - Close(t-1)|,
    |Low(t) - Close(t-1)|
)

ATR(n) = media móvil exponencial del True Range de los últimos n periodos

Tamaño de posición ajustado por ATR:
  riesgo_fijo_sol = 0.025 SOL (1% del capital de 2.5 SOL objetivo)
  distancia_stop  = 2 × ATR(14)
  tamaño_ajustado = riesgo_fijo_sol / distancia_stop (en precio)
```

Si la volatilidad sube, el tamaño baja automáticamente.
Si la volatilidad baja, el tamaño puede subir hasta el máximo configurado.

---

## 4. GESTIÓN DE SALIDA: TRAILING STOP DINÁMICO

### 4.1 El Trailing Stop de 3.5%

```
Para posición LARGA:
  stop_inicial     = precio_entrada × (1 - 0.035)
  stop_actualizado = max(stop_anterior, precio_actual × (1 - 0.035))

El stop SOLO sube, NUNCA baja.
Cuando precio_actual × (1 - 0.035) > stop_anterior → actualizar.
```

### 4.2 Señales de Salida Anticipada (Trend Exhaustion)

Salir ANTES del trailing stop si se detecta:

1. **Divergencia de volumen:** precio sube pero volumen cae > 30% vs media
2. **Hurst cae:** H baja de 0.55 hacia 0.50 en la última ventana de 20 periodos
3. **SMA crossover inverso:** SMA_20 empieza a cruzar hacia abajo SMA_50
4. **Kurtosis explota:** Si fractal_engine.py devuelve kurtosis > 7, hay riesgo de
   cisne negro inmediato — cerrar posición y ceder territorio al Cazador

---

## 5. DISTRIBUCIÓN DE GANANCIAS: EL FEEDBACK LOOP

### 5.1 Destino del Capital (Regla de las Tres Partes)

Al cerrar una posición ganadora:

```
profit_neto = ganancia - fees - slippage

Distribución:
  40% → PROFIT_WALLET (acumulación real del usuario)
  30% → Wallet operativa del Bot 1 (refuerza su margen)
  30% → Reserva del Multiplicador (para próximo ciclo de pyramiding)
```

### 5.2 Lógica del Feedback hacia Bot 1

**¿Por qué reforzar a Bot 1?**
El Bot 1 opera con capital pequeño (max 0.25 SOL en riesgo). Cuando el Bot 2
acumula ganancias significativas, aumentar el capital operativo del Bot 1 multiplica
su generación de "colchón" para el Cazador — sin que el Recolector aumente su riesgo
unitario por operación.

```
Condición de transferencia al Bot 1:
  IF profit_neto > 0.05 SOL:
    transferir = profit_neto × 0.30
    destino    = MAIN_WALLET (wallet principal del Bot 1)
    LOG en SQLite: tabla pending_transfers con dst='BOT1_REINFORCE'
```

---

## 6. CONTEXTO DE MERCADO PARA TREND FOLLOWING EN SOL

### 6.1 Mejores condiciones para el Multiplicador

- **Tendencias post-breakout:** Las primeras 4-8 horas tras un breakout de nivel clave
- **Momentum institucional:** SOL tiende a mantener tendencias durante sesiones americanas (UTC 13:00-22:00)
- **Correlación BTC:** Si BTC rompe un nivel clave Y SOL confirma (H > 0.6), las tendencias son más limpias

### 6.2 Condiciones que invalidan trend following

- **Rango estrecho:** ATR < 0.5% del precio → sin suficiente movimiento para cubrir fees
- **Evento macro:** Fed, CPI, NFP en las próximas 2 horas → salir o no entrar
- **Bot 3 activo:** Si fractal_engine.py devuelve `ACTIVATE` o `ZERO_CLAW_ATTACK`,
  el mercado está en criticalidad — el trend following en este punto es ruleta rusa.
  **Ceder el terreno al Cazador. Cerrar o no abrir posiciones.**

### 6.3 Ventanas de Tiempo Óptimas

```
ALTA efectividad:   UTC 13:00 - 16:00  (apertura NY + momentum)
                    UTC 08:00 - 11:00  (apertura Londres + overlap Asia)
BAJA efectividad:   UTC 00:00 - 06:00  (sesión asiática, menor volumen)
                    UTC 21:00 - 23:00  (cierre NY, reversiones frecuentes)
```

---

## 7. PRINCIPIOS FILOSÓFICOS DEL TREND FOLLOWING

> "Los mercados son más tendenciales de lo que la teoría eficiente predice,
> y más antipersistentes de lo que el momentum ingenuo asume."
> — Benoit Mandelbrot, "The Misbehavior of Markets"

**Los cinco mandamientos del Multiplicador:**

1. **La tendencia no se predice, se sigue.** No anticipar techos ni suelos.
2. **El tamaño correcto es el que te deja dormir.** Si dudas del tamaño, reduce a la mitad.
3. **El trailing stop es sagrado.** Una vez configurado, no se mueve hacia abajo por ninguna razón.
4. **Pyramid solo sobre ganancias, nunca sobre esperanza.**
5. **Cuando el Cazador despierta, el Multiplicador duerme.** El ecosistema tiene jerarquía de señales.

---

*SKILL.md — Multiplicador v2.0.0 · LOG_HAND Unit*
*Ecosistema-Veritasium — Solo para uso educativo y personal*
