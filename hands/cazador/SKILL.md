# SKILL.md — Base de Conocimiento: Cazador (Bot 3)
## Leyes de Potencia, Criticalidad y Opciones OTM en Zeta Markets

> Esta base de conocimiento es el "cerebro teórico" del agente CAZADOR.
> Opera en el mundo de los eventos extremos. Pierde el 95% del tiempo.
> Existe para el 5% restante.

---

## 1. FUNDAMENTOS: DISTRIBUCIONES DE COLA PESADA (POWER LAW)

### 1.1 Por qué los mercados NO son Gaussianos

El mayor error de la teoría financiera clásica es asumir distribución normal.
Los mercados de criptoactivos siguen leyes de potencia para eventos extremos:

```
Distribución Normal:     P(X > x) ~ exp(-x²/2)     ← colas que decaen rápido
Ley de Potencia:         P(X > x) ~ x^(-α)          ← colas que "no mueren"

Para SOL/BTC: α ≈ 2.5 - 3.5

Comparación práctica (evento de 5σ):
  Normal:     probabilidad = 0.00003% (ocurre "una vez en 3.5 millones de días")
  Power Law:  probabilidad = 0.5-2%   (ocurre varias veces al año en cripto)
```

**Conclusión:** Los Black Swans NO son anomalías — son consecuencias esperadas
de la distribución real del mercado. El Cazador los espera. Los otros bots los temen.

### 1.2 Criticalidad Autoorganizada (SOC)

Los mercados complejos tienden a estados críticos donde una perturbación pequeña
puede desencadenar una avalancha de cualquier tamaño:

```
Modelo de la Pila de Arena (Per Bak, 1987):
  - El sistema acumula "tensión" (posiciones, deuda, euforia, miedo)
  - En el estado crítico, la distribución de tamaños de avalancha es una ley de potencia
  - NO HAY escala característica: un evento puede ser pequeño o catastrófico
  - La pila NO "avisa" cuando está a punto de colapsar... pero hay señales fractales

Señales de criticalidad en mercados:
  1. Hurst cae abruptamente de >0.6 a ~0.5 (pérdida de memoria)
  2. Kurtosis > 5 (colas pesadas emergiendo)
  3. Volatilidad implícita sube bruscamente (mercado nervioso)
  4. Fear & Greed en extremos (<20 o >80)
```

### 1.3 El Exponente de Hurst como Sismógrafo

```
H > 0.6:  Mercado con memoria fuerte → Bot 2 opera, Bot 3 espera
H = 0.5:  Mercado sin memoria → transición, vigilancia
H < 0.45: Mercado anti-persistente → Bot 1 opera (mean reversion)

⚠️  SEÑAL DE CAZADOR:
  Si H_anterior > 0.55 Y H_actual ≤ 0.51 en las últimas 20 velas:
  El mercado acaba de "olvidar" su tendencia.
  El sistema ha perdido su exponente de escala.
  Puede ir a cualquier lado con fuerza extrema. PREPARAR.
```

---

## 2. OPCIONES OTM: EL INSTRUMENTO PERFECTO PARA TAIL RISK

### 2.1 Por qué opciones y no swaps spot

El Bot 3 original operaba con swaps spot buscando ratio 1:20.
Las opciones OTM son matemáticamente superiores para este objetivo:

```
Con swap spot (método anterior):
  Riesgo: 0.1 SOL (puede perder todo si el precio va en contra)
  Ganancia objetivo: 2.0 SOL (ratio 1:20)
  Problema: el precio debe moverse exactamente en tu dirección

Con opción OTM (nuevo método):
  Riesgo: 0.02-0.05 SOL (prima de la opción, pérdida máxima garantizada)
  Ganancia potencial: ilimitada para calls, hasta strike×size para puts
  Ventaja: el tiempo trabaja CONTRA ti normalmente, pero en un Black Swan
           la volatilidad implícita EXPLOTA → la opción vale 10x-100x
           antes de que el precio ni siquiera llegue al strike
```

### 2.2 Las Griegas que importan para opciones OTM baratas

```
DELTA (Δ): Sensibilidad al precio subyacente
  OTM típico: Δ = 0.05 - 0.20
  Interpretación: una opción con Δ=0.10 sube 0.10 SOL por cada 1 SOL que suba el subyacente
  En ZERO_CLAW: el delta explota hacia 1.0 durante el movimiento → ganancia exponencial

VEGA (ν): Sensibilidad a la volatilidad implícita
  ⭐ LA MÁS IMPORTANTE PARA EL CAZADOR ⭐
  Cuando hay un Black Swan, la volatilidad implícita puede pasar de 80% a 300%
  Una opción con Vega alto gana valor MASIVAMENTE solo por el pánico/euforia
  OTM options tienen vega alto en relación a su precio → mejor ratio valor/costo

THETA (θ): Decaimiento temporal (el "enemigo")
  Cada día que pasa, la opción pierde valor por theta
  Por eso compramos opciones con vencimiento CORTO (7-14 días):
    - Theta es alto → pérdida rápida si no pasa nada (aceptable, es el "boleto")
    - Pero si el evento ocurre en los primeros días → ganancia antes de theta destruya valor

GAMMA (Γ): Aceleración del delta
  En opciones OTM durante un movimiento extremo:
  Gamma es altísimo → el delta salta de 0.10 a 0.80 en horas → ganancia no lineal
```

### 2.3 Selección de Strike OTM Óptimo

```
Para una CALL (apuesta a subida extrema):
  Precio actual SOL = P
  Strike objetivo = P × 1.10 a P × 1.20 (10-20% fuera del dinero)
  
  Por qué 10-20%? 
  - <10% OTM: muy caro, no suficientemente asimétrico
  - >25% OTM: delta demasiado bajo, necesita movimiento descomunal

Para una PUT (apuesta a caída extrema / crash):
  Strike objetivo = P × 0.80 a P × 0.90 (10-20% fuera del dinero)
  
Criterio de precio de prima:
  NUNCA pagar más de 0.05 SOL por contrato de opción
  El objetivo es comprar "boletos de lotería" baratos, no opciones caras
  Si la prima > 0.05 SOL → el mercado ya "sabe" algo → no es asimétrico → SKIP
```

### 2.4 Dirección del Trade según Señal

```
ZERO_CLAW con Fear & Greed < 25 (Miedo Extremo):
  → Mercado en pánico → movimiento extremo más probable hacia ABAJO
  → Comprar PUT OTM: strike = precio_actual × 0.85, vencimiento 7-14 días

ZERO_CLAW con Fear & Greed > 75 (Codicia Extrema):
  → Mercado en euforia → movimiento extremo más probable hacia ARRIBA  
  → Comprar CALL OTM: strike = precio_actual × 1.15, vencimiento 7-14 días

ZERO_CLAW con Fear & Greed 40-60 (Neutro):
  → Señal fractal sin confirmación de sentimiento
  → Comprar AMBOS (straddle): call + put OTM simultáneos
  → Costo doble pero captura movimiento en cualquier dirección
```

---

## 3. ZETA MARKETS: PROTOCOLO DE OPCIONES EN SOLANA

### 3.1 Qué es Zeta Markets

Zeta Markets es el protocolo DeFi de opciones y futuros perpetuos en Solana:
- **Programa ID:** `ZETAxsqBRek56DhiGXrn75yj2NHU3aYUnxvHXpkf3aD`
- **Asset soportado:** SOL (principal), BTC, ETH
- **Opciones:** Europeas (ejercicio solo al vencimiento)
- **API REST:** `https://dex.zeta.markets/`
- **Liquidación:** En USDC, colateral en USDC

### 3.2 Flujo de Ejecución en Zeta Markets

```
1. DESCUBRIR mercado disponible:
   GET https://dex.zeta.markets/markets
   → Filtrar por: asset=SOL, type=option, kind=call/put
   → Seleccionar el strike más cercano a P×1.15 (call) o P×0.85 (put)
   → Verificar: open_interest > 0 (hay liquidez)

2. OBTENER COTIZACIÓN:
   GET https://dex.zeta.markets/orderbook/{market_address}
   → Leer ask más bajo (precio al que podemos comprar)
   → Verificar que ask_price ≤ 0.05 SOL equivalente en USDC

3. CALCULAR CANTIDAD:
   balance_risk_hunter_sol = consultar RISK_HUNTER_WALLET
   capital_a_usar = balance_risk_hunter_sol × 0.30 (máximo 30% del colchón por trade)
   cantidad_contratos = floor(capital_a_usar_usdc / ask_price_usdc)
   cantidad_contratos = max(1, min(cantidad_contratos, 10)) ← máximo 10 contratos

4. EJECUTAR ORDEN:
   Usar script: python scripts/zeta_options.py --action buy --market {market_addr}
                --contracts {cantidad} --max_price {ask_price × 1.05}

5. MONITOREO (cada hora mientras la opción esté activa):
   - Si precio opción > precio_compra × 5.0 → TAKE PROFIT (5x es suficiente)
   - Si precio opción < precio_compra × 0.20 → STOP LOSS (80% pérdida, salir)
   - Si quedan < 24h para vencimiento Y profit < 2x → cerrar (theta destruye)
```

### 3.3 Gestión del Colchón (RISK_HUNTER_WALLET)

```
Regla de las 3 posiciones máximas:
  El Cazador NUNCA abre más de 3 posiciones de opciones simultáneas

Capital por posición:
  Posición 1 (señal ACTIVATE):           15% del colchón
  Posición 2 (señal ACTIVATE, 2ª):        10% del colchón
  Posición 3 (señal ZERO_CLAW_ATTACK):    30% del colchón → máxima convicción

Capital mínimo para activar el Cazador:
  0.10 SOL en RISK_HUNTER_WALLET (si menos → esperar a que Bot 1 recargue)

Capital en reserva siempre:
  Mantener SIEMPRE ≥ 50% del colchón en reserva → nunca apostar todo
```

---

## 4. EXPECTED VALUE: LA MATEMÁTICA QUE JUSTIFICA PERDER 95% DEL TIEMPO

```
Escenario realista para una opción OTM comprada a 0.02 SOL por contrato:

Caso A (95% de las veces): Opción expira sin valor
  Pérdida = -0.02 SOL

Caso B (4% de las veces): Movimiento significativo pero no extremo
  Ganancia = 0.02 × 3 = +0.06 SOL (3x)

Caso C (1% de las veces): ZERO_CLAW event — movimiento extremo
  Ganancia = 0.02 × 50 = +1.00 SOL (50x)

Valor Esperado:
  EV = (0.95 × -0.02) + (0.04 × 0.06) + (0.01 × 1.00)
  EV = -0.019 + 0.0024 + 0.010
  EV = -0.0066 SOL por contrato

¿EV negativo? Sí. Pero:
  1. El Bot 1 financia estas pérdidas (transferencias del 20%)
  2. El Caso C inyecta capital masivo que reescala TODO el sistema
  3. El 1% de las veces que ocurre un ZERO_CLAW real, el retorno es 50x-100x
  4. La asimetría hace que UNA victoria compense AÑOS de boletos perdidos

Esto es exactamente lo que hacen los mejores fondos de tail risk (Universa, etc.)
```

---

## 5. PROTOCOLO DE INYECCIÓN DE CAPITAL POST-ZERO_CLAW

Cuando el Cazador cierra una posición con ganancia > 10x:

```
Evento ZERO_CLAW completado:
  ganancia_total = precio_cierre × contratos - precio_compra × contratos

Distribución de la ganancia masiva:
  50% → PROFIT_WALLET (el usuario materializa el evento)
  25% → Wallet Bot 1 (aumentar volumen operativo permanentemente)
  15% → Wallet Bot 2 (aumentar capital de pyramiding disponible)
  10% → Mantener en RISK_HUNTER_WALLET (próximo ciclo del Cazador)

Registro en DB:
  tabla: trades
  action: 'ZERO_CLAW_PROFIT'
  cycle_notes: detallar strike, vencimiento, contratos, IV en entrada/salida
```

---

## 6. PRINCIPIOS FILOSÓFICOS DEL CAZADOR

> "La pérdida pequeña y frecuente ES el precio de la ganancia grande y rara.
>  No es un costo — es la estrategia."
> — Nassim Nicholas Taleb, "Antifragile"

**Los mandamientos del Cazador:**

1. **No mirar el P&L diario.** La estrategia se evalúa en años, no en días.
2. **El aburrimiento es la norma.** 95% del tiempo el Cazador simplemente observa.
3. **Nunca aumentar el tamaño por impaciencia.** La señal manda, no el ego.
4. **El colchón es sagrado.** Si Bot 1 no ha recargado → no operar. Sin colchón, no hay Cazador.
5. **Cuando llegue el ZERO_CLAW, ejecutar sin dudar.** El sistema ya decidió. Solo obedecer.

---

*SKILL.md — Cazador v2.0.0 · SWAN_HAND Unit*
*Ecosistema-Veritasium — Solo para uso educativo y personal*
