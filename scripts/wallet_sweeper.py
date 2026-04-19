import os
import json
try:
    import base58
except ImportError:
    # Solved by ensuring base58 is installed in GH Actions
    pass
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solana.transaction import Transaction

def sweep():
    print("🧹 Iniciando Veritasium Wallet Sweeper...")
    rpc_url = os.environ.get("SOLANA_RPC_URL")
    priv_key = os.environ.get("SOLANA_PRIVATE_KEY")
    risk_wallet = os.environ.get("RISK_HUNTER_WALLET")
    
    if not all([rpc_url, priv_key, risk_wallet]):
        print("❌ Faltan variables de entorno requeridas (RPC, PRIVATE_KEY o RISK_HUNTER_WALLET).")
        return

    # Decode private key (Base58 or JSON Array)
    kp = None
    try:
        # Intenta primero como arreglo de bytes JSON
        byte_array = bytes(json.loads(priv_key))
        kp = Keypair.from_bytes(byte_array)
    except Exception:
        try:
            # Intenta como Base58
            import base58
            kp = Keypair.from_bytes(base58.b58decode(priv_key))
        except Exception as e:
            print(f"❌ Fallo al decodificar la SOLANA_PRIVATE_KEY: {e}")
            return
            
    client = Client(rpc_url)
    pubkey = kp.pubkey()
    
    # Obtener balance actual
    balance_resp = client.get_balance(pubkey)
    lamports = balance_resp.value
    sol_balance = lamports / 10**9
    
    print(f"💰 Balance actual (Bot 1): {sol_balance} SOL")
    
    # Regla: Mantener 0.50 SOL (Operativo) + 0.05 SOL (Reserva de seguridad)
    THRESHOLD = 0.55
    if sol_balance > THRESHOLD:
        excess = sol_balance - 0.50
        sweep_amount = round(excess * 0.20, 5) # 20% del exceso
        
        if sweep_amount >= 0.01:
            print(f"🔥 Exceso detectado. Enviando {sweep_amount} SOL a RISK_HUNTER_WALLET...")
            dest_pubkey = Pubkey.from_string(risk_wallet)
            sweep_lamports = int(sweep_amount * 10**9)
            
            txn = Transaction().add(transfer(TransferParams(
                from_pubkey=pubkey,
                to_pubkey=dest_pubkey,
                lamports=sweep_lamports
            )))
            
            try:
                # Obtener blockhash reciente
                recent_blockhash_item = client.get_latest_blockhash().value
                txn.recent_blockhash = recent_blockhash_item.blockhash
                txn.sign(kp)
                
                resp = client.send_transaction(txn)
                print(f"✅ Sweep exitoso. Signature: {resp.value}")
            except Exception as e:
                print(f"❌ Falló la transferencia del Sweep: {e}")
        else:
            print(f"⏳ El 20% del exceso ({sweep_amount} SOL) es demasiado bajo para justificar fees. Ahorrando...")
    else:
        print("🛡️ Balance por debajo del umbral operativo (0.55 SOL). No se requiere Sweep.")

if __name__ == "__main__":
    sweep()
