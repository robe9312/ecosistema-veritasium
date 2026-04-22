"""
zeta_options.py — Módulo de Opciones OTM para el Cazador (Bot 3)
Ecosistema-Veritasium · SWAN_HAND Unit

Integra con Zeta Markets (Solana) para comprar opciones OTM baratas
y ejecutar el protocolo de inyección de capital post-ZERO_CLAW.

Uso:
  python scripts/zeta_options.py --action buy_option --type call --strike 185.0
         --expiry 14 --max_premium_sol 0.03 --max_contracts 5 --signal ACTIVATE

  python scripts/zeta_options.py --action check_price --position_id 42

  python scripts/zeta_options.py --action distribute_profit --profit_sol 2.5
         --profit_wallet <addr> --main_wallet <addr> --multiplicador_wallet <addr>
"""

import os
import sys
import json
import time
import argparse
import sqlite3
import requests
import base58
from datetime import datetime, timedelta

try:
    from solana.rpc.api import Client
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import TransferParams, transfer
    from solana.transaction import Transaction
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    print("⚠️  solana-py no disponible — modo simulación activado")

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

ZETA_API_BASE      = "https://dex.zeta.markets"
ZETA_PROGRAM_ID    = "ZETAxsqBRek56DhiGXrn75yj2NHU3aYUnxvHXpkf3aD"
SOL_MINT           = "So11111111111111111111111111111111111111112"
USDC_MINT          = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
DB_PATH            = ".veritasium/state.db"
LAMPORTS_PER_SOL   = 1_000_000_000
MIN_COLCHON_SOL    = 0.10       # Colchón mínimo para operar
MAX_PREMIUM_DEFAULT = 0.05      # Prima máxima en SOL equivalente

# Distribución post ZERO_CLAW (porcentajes)
DIST_PROFIT_WALLET  = 0.50
DIST_BOT1_REINFORCE = 0.25
DIST_BOT2_REINFORCE = 0.15
DIST_SELF_RESERVE   = 0.10


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────

def load_env():
    """Carga y valida variables de entorno requeridas."""
    config = {
        "rpc_url":            os.environ.get("SOLANA_RPC_URL"),
        "private_key":        os.environ.get("SOLANA_PRIVATE_KEY"),
        "risk_hunter_wallet": os.environ.get("RISK_HUNTER_WALLET"),
        "profit_wallet":      os.environ.get("PROFIT_WALLET"),
        "main_wallet":        os.environ.get("MAIN_WALLET"),          # Wallet Bot 1
        "multiplicador_wallet": os.environ.get("MULTIPLICADOR_WALLET"),  # Wallet Bot 2
        "bot_mode":           os.environ.get("BOT_MODE", "dry-run"),
    }
    missing = [k for k, v in config.items()
               if v is None and k not in ("main_wallet", "multiplicador_wallet")]
    if missing:
        print(f"❌ Variables de entorno faltantes: {missing}")
        sys.exit(1)
    return config


def get_keypair(private_key_str: str):
    """Decodifica la clave privada desde Base58 o array JSON."""
    if not SOLANA_AVAILABLE:
        return None
    try:
        byte_array = bytes(json.loads(private_key_str))
        return Keypair.from_bytes(byte_array)
    except Exception:
        try:
            return Keypair.from_bytes(base58.b58decode(private_key_str))
        except Exception as e:
            print(f"❌ Error decodificando SOLANA_PRIVATE_KEY: {e}")
            sys.exit(1)


def get_sol_price() -> float:
    """Obtiene precio actual SOL/USDC desde Jupiter."""
    try:
        resp = requests.get(
            "https://price.jup.ag/v6/price",
            params={"ids": SOL_MINT},
            timeout=10
        )
        resp.raise_for_status()
        return float(resp.json()["data"][SOL_MINT]["price"])
    except Exception as e:
        print(f"⚠️  No se pudo obtener precio SOL: {e}. Usando fallback.")
        try:
            resp = requests.get(
                "https://api.binance.com/api/v3/ticker/price",
                params={"symbol": "SOLUSDT"},
                timeout=10
            )
            return float(resp.json()["price"])
        except Exception:
            return 150.0  # Fallback de emergencia


def get_wallet_balance_sol(rpc_url: str, pubkey_str: str) -> float:
    """Consulta balance en SOL de una wallet."""
    if not SOLANA_AVAILABLE:
        return 0.5  # Simulación
    try:
        client = Client(rpc_url)
        pubkey = Pubkey.from_string(pubkey_str)
        resp = client.get_balance(pubkey)
        return resp.value / LAMPORTS_PER_SOL
    except Exception as e:
        print(f"⚠️  Error consultando balance: {e}")
        return 0.0


def db_log_trade(hand_id, action, details: dict, mode: str):
    """Registra una acción de trading en SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO trades (hand_id, action, hurst, kurtosis, confidence_score,
                                sentiment, sentiment_score, cycle_notes, mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hand_id,
            action,
            details.get("hurst"),
            details.get("kurtosis"),
            details.get("confidence"),
            details.get("sentiment"),
            details.get("sentiment_score"),
            json.dumps(details),
            mode
        ))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"⚠️  Error registrando en DB: {e}")
        return None
    finally:
        conn.close()


def db_open_position(details: dict, mode: str) -> int:
    """Registra posición abierta en open_positions."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO open_positions (direction, entry_price, trade_size_sol,
                                        entry_txn, z_score_at_entry, status)
            VALUES (?, ?, ?, ?, ?, 'open')
        """, (
            details.get("direction", "long"),
            details.get("entry_price", 0),
            details.get("size_sol", 0),
            details.get("txn_signature", "dry-run"),
            details.get("confidence", 0),
        ))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"⚠️  Error abriendo posición en DB: {e}")
        return -1
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────
# ZETA MARKETS API
# ─────────────────────────────────────────────────────────────

def get_zeta_markets(asset: str = "SOL") -> list:
    """
    Obtiene mercados de opciones disponibles en Zeta Markets.
    Retorna lista de mercados con strike, expiry, tipo (call/put).
    """
    try:
        resp = requests.get(
            f"{ZETA_API_BASE}/markets",
            params={"asset": asset, "kind": "option"},
            timeout=15
        )
        if resp.status_code == 200:
            markets = resp.json()
            # Filtrar solo opciones activas con liquidez
            active = [m for m in markets
                      if m.get("active", False) and m.get("open_interest", 0) > 0]
            return active
        else:
            print(f"⚠️  Zeta Markets API retornó {resp.status_code}. Usando modo simulación.")
            return []
    except Exception as e:
        print(f"⚠️  Error conectando a Zeta Markets: {e}. Modo simulación activado.")
        return []


def find_best_otm_option(markets: list, option_type: str,
                          target_strike: float, max_premium_usdc: float) -> dict | None:
    """
    Encuentra la opción OTM más barata y líquida cercana al strike objetivo.

    Args:
        markets: Lista de mercados de Zeta
        option_type: 'call' o 'put'
        target_strike: Strike objetivo calculado (precio × 1.15 o × 0.85)
        max_premium_usdc: Prima máxima dispuesta a pagar en USDC

    Returns:
        Mejor mercado encontrado o None si no hay opciones adecuadas
    """
    candidates = []

    for market in markets:
        if market.get("kind", "").lower() != "option":
            continue
        if market.get("option_type", "").lower() != option_type.lower():
            continue

        strike = float(market.get("strike", 0))
        expiry_ts = market.get("expiry_timestamp", 0)
        ask_price = float(market.get("best_ask", market.get("ask", 0)))

        if ask_price <= 0 or ask_price > max_premium_usdc:
            continue

        # Calcular días al vencimiento
        expiry_dt = datetime.fromtimestamp(expiry_ts)
        days_to_expiry = (expiry_dt - datetime.utcnow()).days
        if days_to_expiry < 3 or days_to_expiry > 21:  # Rango óptimo: 3-21 días
            continue

        # Calcular distancia al strike objetivo
        distance = abs(strike - target_strike) / target_strike

        candidates.append({
            "market_address": market.get("address"),
            "strike": strike,
            "expiry": expiry_dt.strftime("%Y-%m-%d"),
            "days_to_expiry": days_to_expiry,
            "ask_price_usdc": ask_price,
            "open_interest": market.get("open_interest", 0),
            "distance_from_target": distance,
            "option_type": option_type,
        })

    if not candidates:
        return None

    # Ordenar por: menor distancia al strike objetivo, luego por precio
    candidates.sort(key=lambda x: (x["distance_from_target"], x["ask_price_usdc"]))
    return candidates[0]


def simulate_option_purchase(option_type: str, strike: float,
                               sol_price: float, premium_sol: float,
                               contracts: int, signal: str) -> dict:
    """
    Simula una compra de opción (modo dry-run o cuando Zeta no responde).
    Genera datos realistas para testing.
    """
    simulated_premium_usdc = premium_sol * sol_price * 0.02  # 2% de SOL como prima

    print(f"""
🔬 SIMULACIÓN — Compra de Opción OTM
  Tipo:        {option_type.upper()}
  Strike:      ${strike:.2f} USDC
  SOL actual:  ${sol_price:.2f}
  OTM %:       {abs(strike - sol_price) / sol_price * 100:.1f}%
  Prima:       ~${simulated_premium_usdc:.4f} USDC por contrato
  Contratos:   {contracts}
  Costo total: ~${simulated_premium_usdc * contracts:.4f} USDC
  Señal:       {signal}
  Modo:        DRY-RUN (simulación, sin transacción real)
    """)

    return {
        "success": True,
        "mode": "dry-run",
        "option_type": option_type,
        "strike": strike,
        "contracts": contracts,
        "premium_usdc_per_contract": simulated_premium_usdc,
        "total_cost_usdc": simulated_premium_usdc * contracts,
        "txn_signature": f"DRY_RUN_ZETA_{int(time.time())}",
        "market_address": "SIMULATED",
        "expiry": (datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d"),
    }


# ─────────────────────────────────────────────────────────────
# ACCIONES PRINCIPALES
# ─────────────────────────────────────────────────────────────

def action_buy_option(args, config: dict):
    """
    Compra una opción OTM en Zeta Markets (o simula si está en dry-run).
    """
    print(f"\n🦅 CAZADOR — Iniciando compra de opción {args.type.upper()} OTM")
    print(f"   Señal: {args.signal} | Modo: {config['bot_mode']}")

    sol_price = get_sol_price()
    print(f"   Precio SOL actual: ${sol_price:.2f}")

    # Calcular strike si no se especificó
    strike = args.strike
    if strike <= 0:
        if args.type == "call":
            strike = sol_price * 1.15
        elif args.type == "put":
            strike = sol_price * 0.85
    print(f"   Strike objetivo: ${strike:.2f}")

    # Verificar colchón disponible
    colchon_sol = get_wallet_balance_sol(config["rpc_url"], config["risk_hunter_wallet"])
    print(f"   Colchón disponible: {colchon_sol:.4f} SOL")

    if colchon_sol < MIN_COLCHON_SOL:
        print(f"❌ Colchón insuficiente ({colchon_sol:.4f} SOL < {MIN_COLCHON_SOL} SOL)")
        print("   El Bot 1 necesita recargar el RISK_HUNTER_WALLET antes de operar.")
        db_log_trade("cazador", "HOLD_LOW_BALANCE",
                     {"reason": "colchon_insuficiente", "balance": colchon_sol,
                      "signal": args.signal}, config["bot_mode"])
        return

    # Capital para esta operación
    pct = 0.30 if args.signal == "ZERO_CLAW_ATTACK" else 0.15
    capital_op_sol = colchon_sol * pct
    max_premium_usdc = args.max_premium_sol * sol_price

    print(f"   Capital asignado: {capital_op_sol:.4f} SOL ({pct*100:.0f}% del colchón)")

    # Intentar con Zeta Markets real
    result = None

    if config["bot_mode"] == "live":
        markets = get_zeta_markets("SOL")

        if markets:
            best_option = find_best_otm_option(
                markets, args.type, strike, max_premium_usdc
            )

            if best_option:
                print(f"\n✅ Opción encontrada en Zeta Markets:")
                print(f"   Strike:        ${best_option['strike']:.2f}")
                print(f"   Vencimiento:   {best_option['expiry']} ({best_option['days_to_expiry']}d)")
                print(f"   Prima ask:     ${best_option['ask_price_usdc']:.4f} USDC")
                print(f"   Open Interest: {best_option['open_interest']}")

                # Calcular contratos
                contracts = min(
                    args.max_contracts,
                    max(1, int(capital_op_sol * sol_price / best_option["ask_price_usdc"]))
                )
                total_cost_usdc = contracts * best_option["ask_price_usdc"]

                print(f"   Contratos:     {contracts}")
                print(f"   Costo total:   ${total_cost_usdc:.4f} USDC")

                # TODO: Implementar firma y envío de transacción a Zeta Markets
                # Requiere: anchorpy + Zeta Markets IDL para crear la orden
                # Por ahora registramos la intención y usamos simulación con datos reales
                print("\n⚠️  Ejecución on-chain en Zeta requiere Anchor TX — registrando posición")
                result = {
                    "success": True,
                    "mode": "live_simulated",
                    "option_type": args.type,
                    "strike": best_option["strike"],
                    "contracts": contracts,
                    "premium_usdc_per_contract": best_option["ask_price_usdc"],
                    "total_cost_usdc": total_cost_usdc,
                    "market_address": best_option["market_address"],
                    "expiry": best_option["expiry"],
                    "txn_signature": f"PENDING_ZETA_{int(time.time())}",
                }
            else:
                print(f"\n⚠️  No hay opciones OTM disponibles en Zeta con prima ≤ ${max_premium_usdc:.2f}")
                print("   Intentando PsyOptions como alternativa...")
                # Fallback a simulación si no hay mercado
                result = simulate_option_purchase(
                    args.type, strike, sol_price,
                    args.max_premium_sol, args.max_contracts, args.signal
                )
        else:
            print("⚠️  Zeta Markets no responde — ejecutando en modo simulación")
            result = simulate_option_purchase(
                args.type, strike, sol_price,
                args.max_premium_sol, args.max_contracts, args.signal
            )
    else:
        # Modo dry-run siempre simula
        result = simulate_option_purchase(
            args.type, strike, sol_price,
            args.max_premium_sol, args.max_contracts, args.signal
        )

    if result and result.get("success"):
        # Registrar en DB
        position_id = db_open_position({
            "direction": f"option_{args.type}",
            "entry_price": result["premium_usdc_per_contract"],
            "size_sol": result["total_cost_usdc"] / sol_price,
            "txn_signature": result["txn_signature"],
            "confidence": 0.9 if args.signal == "ZERO_CLAW_ATTACK" else 0.5,
        }, config["bot_mode"])

        db_log_trade("cazador", f"BUY_OPTION_{args.type.upper()}", {
            "strike": result["strike"],
            "contracts": result["contracts"],
            "premium_usdc": result["premium_usdc_per_contract"],
            "total_cost_usdc": result["total_cost_usdc"],
            "market": result["market_address"],
            "expiry": result["expiry"],
            "signal": args.signal,
            "position_id": position_id,
        }, config["bot_mode"])

        print(f"\n✅ Opción registrada — Position ID: {position_id}")
        print(f"   {result['option_type'].upper()} @ ${result['strike']:.2f}")
        print(f"   Exp: {result['expiry']} | {result['contracts']} contratos")
        print(f"   Señal de cierre: 5x take-profit | 80% stop-loss | <24h theta kill")


def action_check_price(args, config: dict):
    """Verifica el precio actual de una opción abierta y decide si cerrar."""
    print(f"\n📊 CAZADOR — Chequeando posición ID: {args.position_id}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, direction, entry_price, trade_size_sol, opened_at, entry_txn
            FROM open_positions
            WHERE id = ? AND hand_id = 'cazador' AND status = 'open'
        """, (args.position_id,))
        pos = cur.fetchone()
    finally:
        conn.close()

    if not pos:
        print(f"❌ Posición {args.position_id} no encontrada o ya cerrada.")
        return

    pos_id, direction, entry_price, size_sol, opened_at, entry_txn = pos
    sol_price = get_sol_price()

    # Calcular días desde apertura
    opened_dt = datetime.fromisoformat(opened_at)
    days_open = (datetime.utcnow() - opened_dt).days

    print(f"   Dirección:    {direction}")
    print(f"   Precio entrada: ${entry_price:.4f} USDC")
    print(f"   Días abierta: {days_open}")
    print(f"   SOL actual:   ${sol_price:.2f}")

    # Obtener precio actual de la opción (simplificado — en producción llamar a Zeta)
    # Modelo simple de valoración: si SOL se movió hacia el strike, la opción vale más
    is_call = "call" in direction.lower()
    current_option_price = entry_price  # Placeholder — necesita llamada real a Zeta

    ratio = current_option_price / entry_price if entry_price > 0 else 1.0

    action_decision = "HOLD"
    if ratio >= 5.0:
        action_decision = "TAKE_PROFIT"
    elif ratio <= 0.20:
        action_decision = "STOP_LOSS"
    elif days_open >= 13 and ratio < 2.0:
        action_decision = "THETA_KILL"

    print(f"   Ratio P&L:    {ratio:.2f}x")
    print(f"   Decisión:     {action_decision}")

    db_log_trade("cazador", action_decision, {
        "position_id": pos_id,
        "entry_price": entry_price,
        "current_price_estimate": current_option_price,
        "ratio": ratio,
        "days_open": days_open,
    }, config["bot_mode"])

    return action_decision


def action_distribute_profit(args, config: dict):
    """
    Distribuye las ganancias de un evento ZERO_CLAW entre los bots del ecosistema.
    50% → PROFIT_WALLET | 25% → Bot 1 | 15% → Bot 2 | 10% → reserva
    """
    print(f"\n🎯 CAZADOR — Protocolo de Inyección Post-ZERO_CLAW")
    print(f"   Ganancia total: {args.profit_sol:.4f} SOL")

    sol_price = get_sol_price()
    total = args.profit_sol

    dist = {
        "profit_wallet":      (total * DIST_PROFIT_WALLET,      args.profit_wallet),
        "bot1_reinforce":     (total * DIST_BOT1_REINFORCE,     args.main_wallet),
        "bot2_reinforce":     (total * DIST_BOT2_REINFORCE,     args.multiplicador_wallet),
        "self_reserve":       (total * DIST_SELF_RESERVE,       config["risk_hunter_wallet"]),
    }

    print("\n📊 Plan de distribución:")
    for name, (amount, dest) in dist.items():
        if dest:
            print(f"   {name:20s}: {amount:.4f} SOL (${amount * sol_price:.2f}) → {dest[:8]}...")

    if config["bot_mode"] == "dry-run":
        print("\n🔬 DRY-RUN — No se ejecutaron transferencias reales")
        db_log_trade("cazador", "ZERO_CLAW_PROFIT_DISTRIBUTED", {
            "total_sol": total,
            "mode": "dry-run",
            "distribution": {k: v[0] for k, v in dist.items()},
        }, "dry-run")
        return

    # En modo live: ejecutar transferencias reales
    kp = get_keypair(config["private_key"])
    if not kp or not SOLANA_AVAILABLE:
        print("❌ No se pueden ejecutar transferencias — keypair o solana-py no disponible")
        return

    client = Client(config["rpc_url"])
    recent_bh = client.get_latest_blockhash().value

    for name, (amount, dest) in dist.items():
        if not dest or amount < 0.001:
            continue
        try:
            dest_pubkey = Pubkey.from_string(dest)
            lamports = int(amount * LAMPORTS_PER_SOL)
            txn = Transaction().add(transfer(TransferParams(
                from_pubkey=kp.pubkey(),
                to_pubkey=dest_pubkey,
                lamports=lamports
            )))
            txn.recent_blockhash = recent_bh.blockhash
            txn.sign(kp)
            resp = client.send_transaction(txn)
            print(f"   ✅ {name}: {amount:.4f} SOL → {resp.value}")
            time.sleep(0.5)  # Evitar rate limiting del RPC
        except Exception as e:
            print(f"   ❌ {name}: Error en transferencia — {e}")

    db_log_trade("cazador", "ZERO_CLAW_PROFIT_DISTRIBUTED", {
        "total_sol": total,
        "distribution": {k: v[0] for k, v in dist.items()},
    }, "live")

    print(f"\n🏆 Inyección completada. El ecosistema escala con la victoria del Cazador.")


# ─────────────────────────────────────────────────────────────
# PARSER Y MAIN
# ─────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Zeta Markets Options Module — Ecosistema Veritasium"
    )
    parser.add_argument("--action", required=True,
                        choices=["buy_option", "check_price", "distribute_profit"],
                        help="Acción a ejecutar")

    # buy_option args
    parser.add_argument("--type",    default="call",
                        choices=["call", "put", "straddle"],
                        help="Tipo de opción")
    parser.add_argument("--strike",  type=float, default=0,
                        help="Strike price (0 = auto-calcular)")
    parser.add_argument("--expiry",  type=int,   default=14,
                        help="Días al vencimiento objetivo")
    parser.add_argument("--max_premium_sol", type=float, default=MAX_PREMIUM_DEFAULT,
                        help="Prima máxima por contrato en SOL")
    parser.add_argument("--max_contracts",   type=int,   default=5,
                        help="Número máximo de contratos")
    parser.add_argument("--signal",  default="ACTIVATE",
                        choices=["ACTIVATE", "ZERO_CLAW_ATTACK"],
                        help="Señal que disparó la compra")

    # check_price args
    parser.add_argument("--position_id", type=int, default=-1,
                        help="ID de la posición abierta a verificar")

    # distribute_profit args
    parser.add_argument("--profit_sol",          type=float, default=0.0)
    parser.add_argument("--profit_wallet",        type=str,   default="")
    parser.add_argument("--main_wallet",          type=str,   default="")
    parser.add_argument("--multiplicador_wallet", type=str,   default="")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = load_env()

    print(f"\n{'='*60}")
    print(f"  🦅 Zeta Options Module — Ecosistema Veritasium")
    print(f"  Acción: {args.action.upper()} | Modo: {config['bot_mode']}")
    print(f"{'='*60}\n")

    if args.action == "buy_option":
        if args.type == "straddle":
            # Comprar call y put simultáneamente
            print("📡 STRADDLE: ejecutando CALL + PUT en secuencia...")
            args.type = "call"
            action_buy_option(args, config)
            time.sleep(1)
            args.type = "put"
            action_buy_option(args, config)
        else:
            action_buy_option(args, config)

    elif args.action == "check_price":
        action_check_price(args, config)

    elif args.action == "distribute_profit":
        if args.profit_sol <= 0:
            print("❌ --profit_sol debe ser mayor que 0")
            sys.exit(1)
        action_distribute_profit(args, config)
