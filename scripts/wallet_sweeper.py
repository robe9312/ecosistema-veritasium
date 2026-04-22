import os
import json
try:
    import base58
except ImportError:
    pass
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solana.transaction import Transaction

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────
LAMPORTS_PER_SOL     = 1_000_000_000
THRESHOLD_OPERATIVO  = 0.55    # Mantener este mínimo en Bot 1
SWEEP_PCT            = 0.20    # 20% del exceso → RISK_HUNTER_WALLET (Bot 3)
MIN_SWEEP_SOL        = 0.01    # Mínimo para justificar fees de red


def load_keypair(priv_key: str) -> Keypair | None:
    """Decodifica keypair desde Base58 o array JSON."""
    try:
        byte_array = bytes(json.loads(priv_key))
        return Keypair.from_bytes(byte_array)
    except Exception:
        try:
            import base58
            return Keypair.from_bytes(base58.b58decode(priv_key))
        except Exception as e:
            print(f"❌ Fallo al decodificar SOLANA_PRIVATE_KEY: {e}")
            return None


def send_sol(client: Client, kp: Keypair, dest_str: str,
             amount_sol: float, label: str) -> str | None:
    """Envía SOL y retorna la signature de la transacción."""
    try:
        dest_pubkey  = Pubkey.from_string(dest_str)
        lamports     = int(amount_sol * LAMPORTS_PER_SOL)
        recent_bh    = client.get_latest_blockhash().value
        txn = Transaction().add(transfer(TransferParams(
            from_pubkey=kp.pubkey(),
            to_pubkey=dest_pubkey,
            lamports=lamports
        )))
        txn.recent_blockhash = recent_bh.blockhash
        txn.sign(kp)
        resp = client.send_transaction(txn)
        sig  = str(resp.value)
        print(f"   ✅ {label}: {amount_sol:.5f} SOL → {dest_str[:8]}... | sig: {sig[:12]}...")
        return sig
    except Exception as e:
        print(f"   ❌ {label}: Error en transferencia — {e}")
        return None


def sweep():
    print("🧹 Iniciando Veritasium Wallet Sweeper v2.0 ...")

    # ── Variables de entorno ──────────────────────────────────
    rpc_url          = os.environ.get("SOLANA_RPC_URL")
    priv_key         = os.environ.get("SOLANA_PRIVATE_KEY")
    risk_wallet      = os.environ.get("RISK_HUNTER_WALLET")  # Colchón del Bot 3
    profit_wallet    = os.environ.get("PROFIT_WALLET")       # Acumulación del usuario
    main_wallet      = os.environ.get("MAIN_WALLET")         # Wallet principal Bot 1 (self)
    bot_mode         = os.environ.get("BOT_MODE", "dry-run")

    # MAIN_WALLET puede ser la misma que la que firmamos — es la referencia para
    # recibir refuerzos del Bot 2. Si no está definida, no hay feedback loop Bot2→Bot1.
    has_feedback_target = main_wallet is not None

    if not all([rpc_url, priv_key, risk_wallet]):
        print("❌ Faltan variables de entorno (RPC, PRIVATE_KEY o RISK_HUNTER_WALLET).")
        return

    kp = load_keypair(priv_key)
    if not kp:
        return

    client  = Client(rpc_url)
    pubkey  = kp.pubkey()

    # ── Consultar balance actual ──────────────────────────────
    balance_resp = client.get_balance(pubkey)
    sol_balance  = balance_resp.value / LAMPORTS_PER_SOL
    print(f"\n💰 Wallet Bot 1: {sol_balance:.5f} SOL")
    print(f"   Umbral operativo:  {THRESHOLD_OPERATIVO} SOL")
    print(f"   Modo:              {bot_mode}")

    # ── SWEEP BOT 1 → BOT 3 (lógica original mejorada) ───────
    if sol_balance > THRESHOLD_OPERATIVO:
        exceso       = sol_balance - THRESHOLD_OPERATIVO
        sweep_amount = round(exceso * SWEEP_PCT, 5)

        print(f"\n📤 SWEEP BOT1 → BOT3:")
        print(f"   Exceso detectado: {exceso:.5f} SOL")
        print(f"   A transferir (20%): {sweep_amount:.5f} SOL → RISK_HUNTER_WALLET")

        if sweep_amount >= MIN_SWEEP_SOL:
            if bot_mode == "dry-run":
                print(f"   🔬 DRY-RUN: transferencia simulada de {sweep_amount:.5f} SOL")
            else:
                send_sol(client, kp, risk_wallet, sweep_amount,
                         "SWEEP Bot1→Bot3 colchón")
        else:
            print(f"   ⏳ Monto ({sweep_amount:.5f} SOL) menor que mínimo — ahorrando para siguiente ciclo.")
    else:
        print(f"\n🛡️  Balance por debajo del umbral operativo. No se requiere sweep.")

    # ── RECEPCIÓN DE REFUERZO BOT 2 → BOT 1 ─────────────────
    # Este bloque documenta el flujo inverso: el Bot 2, cuando cierra una
    # posición ganadora, envía el 30% a MAIN_WALLET. El sweeper lo detecta
    # como balance > THRESHOLD y lo distribuye en el siguiente ciclo.
    # No hay acción explícita aquí — la recepción es pasiva.
    if has_feedback_target:
        print(f"\n🔄 FEEDBACK LOOP Bot2→Bot1:")
        print(f"   MAIN_WALLET configurada: {main_wallet[:8]}...")
        print(f"   El Bot 2 enviará 30% de sus profits aquí automáticamente.")
        print(f"   Balance actual refleja acumulado de ambos bots.")

    # ── REPORTE FINAL ─────────────────────────────────────────
    # Consultar balance del colchón Bot 3 para reporte
    try:
        rh_balance = client.get_balance(
            Pubkey.from_string(risk_wallet)
        ).value / LAMPORTS_PER_SOL
        pct_lleno  = min(100, int(rh_balance / 0.5 * 100))
        bar        = "█" * (pct_lleno // 10) + "░" * (10 - pct_lleno // 10)
        print(f"\n📊 Estado del Ecosistema:")
        print(f"   Bot 1 wallet:       {sol_balance:.5f} SOL")
        print(f"   Bot 3 colchón:      {rh_balance:.5f} SOL  [{bar}] {pct_lleno}%")
        if rh_balance >= 0.5:
            print(f"   🟢 Tanque lleno — próximo sweep va a PROFIT_WALLET")
        elif rh_balance >= 0.1:
            print(f"   🟡 Tanque cargando — próximos sweeps van a RISK_HUNTER_WALLET")
        else:
            print(f"   🔴 Tanque bajo — Bot 3 en espera, acumulando colchón")
    except Exception as e:
        print(f"   ⚠️  No se pudo consultar balance RISK_HUNTER_WALLET: {e}")


if __name__ == "__main__":
    sweep()
