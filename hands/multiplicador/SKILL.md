# SKILL.md — Base de Conocimiento: Multiplicador (Bot 2)
## Distribuciones Log-Normales y Momentum

### 1. DISTRIBUCIÓN LOG-NORMAL
A diferencia de los retornos (Bot 1), los precios de los activos financieros no pueden ser negativos, por lo que su distribución tiende a ser log-normal.
- **Ley:** Los cambios en el precio son proporcionales al nivel de precio actual (efecto multiplicativo).
- **Compounding:** La rentabilidad geométrica es lo que realmente importa para el crecimiento del capital a largo plazo.

### 2. MOVIMIENTO BROWNIANO GEOMÉTRICO (GBM)
El Bot 2 asume que el mercado puede entrar en fases de GBM donde la tendencia es la fuerza dominante:
- **Deriva (Drift):** La dirección promedio de la tendencia.
- **Difusión:** El ruido o volatilidad alrededor de la tendencia.

### 3. TREND FOLLOWING: PERSISTENCIA
- **Identificación:** Usamos cruces de medias (SMA 20/50) y volumen creciente.
- **Confirmación:** Buscamos un Hurst Exponent > 0.55 (indicación de serie persistente).
- **Ejecución:** "The trend is your friend until the end". No intentamos adivinar techos; seguimos la ola hasta que el Trailing Stop de 3.5% nos saque.

### 4. GESTIÓN DE RIESGO: VOLATILIDAD DINÁMICA
- Si la volatilidad aumenta, reducimos el tamaño de la posición para mantener el riesgo constante en términos de SOL.
- **Interés Compuesto:** Revertimos las ganancias en la posición activa (pyramiding) solo si el Stop original ya está en "Break Even".

---
*SKILL.md — Unidad LOG_HAND*
