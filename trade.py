import json
import requests
from solders.transaction import VersionedTransaction # type: ignore
from solders.keypair import Keypair # type: ignore
from solders.commitment_config import CommitmentLevel # type: ignore
from solders.rpc.requests import SendVersionedTransaction # type: ignore
from solders.rpc.config import RpcSendTransactionConfig # type: ignore
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradeConfig:
    api_key: str
    private_key: str
    public_key: str
    rpc_endpoint: str
    denominated_in_sol: bool
    slippage: int
    priority_fee: float
    pool: str

def read_config(config_file='config.json') -> TradeConfig:
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        return TradeConfig(
            api_key=config_data['api_key'],
            private_key=config_data['private_key'],
            public_key=config_data['wallet_address'],
            rpc_endpoint=config_data['rpc_endpoint'],
            denominated_in_sol=config_data['denominatedInSol'].lower() == 'true',
            slippage=int(config_data['slippage']),
            priority_fee=float(config_data['priorityFee']),
            pool=config_data['pool']
        )
    except Exception as e:
        logger.error(f"Failed to read config file: {e}")
        raise

def get_unsigned_transaction(config: TradeConfig, action: str, mint: str, amount: str) -> bytes:
    url = "https://pumpportal.fun/api/trade-local"
    payload = {
        "publicKey": config.public_key,
        "action": action,
        "mint": mint,
        "amount": amount,
        "denominatedInSol": str(config.denominated_in_sol).lower(),
        "slippage": config.slippage,
        "priorityFee": config.priority_fee,
        "pool": config.pool
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.content

def sign_and_send_transaction(unsigned_tx: bytes, config: TradeConfig) -> str:
    keypair = Keypair.from_base58_string(config.private_key)
    tx = VersionedTransaction(VersionedTransaction.from_bytes(unsigned_tx).message, [keypair])
    
    commitment = CommitmentLevel.Confirmed
    rpc_config = RpcSendTransactionConfig(preflight_commitment=commitment)
    tx_payload = SendVersionedTransaction(tx, rpc_config)

    response = requests.post(
        url=config.rpc_endpoint,
        headers={"Content-Type": "application/json"},
        data=tx_payload.to_json()
    )
    response.raise_for_status()
    response_json = response.json()

    if 'result' in response_json:
        return response_json['result']
    elif 'error' in response_json:
        error_msg = response_json['error'].get('message', 'Unknown error')
        raise ValueError(f"Transaction failed: {error_msg}")
    else:
        raise ValueError(f"Unexpected response format: {response_json}")

def execute_local_trade(config: TradeConfig, action: str, mint: str, amount: str) -> str:
    try:
        unsigned_tx = get_unsigned_transaction(config, action, mint, amount)
        tx_signature = sign_and_send_transaction(unsigned_tx, config)
        logger.info(f"Transaction sent successfully: {tx_signature}")
        return tx_signature
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {e}")
        raise ValueError(f"Network error occurred: {e}")
    except ValueError as e:
        logger.error(f"Transaction error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise ValueError(f"An unexpected error occurred: {e}")


def main():
    try:
        config = read_config()
        action = input("Enter action (buy/sell): ").strip()
        mint = input("Enter token mint address: ").strip()
        amount = input("Enter amount: ").strip()

        tx_signature = execute_local_trade(config, action, mint, amount)
        print(f'Transaction: https://solscan.io/tx/{tx_signature}')
    except Exception as e:
        print(f"Failed to execute trade: {e}")

if __name__ == "__main__":
    main()
