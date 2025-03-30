from tronpy import AsyncTron
from tronpy.providers import AsyncHTTPProvider

from src.config import load_config

config = load_config()
endpoint = config.tron.api_url
client_address = config.tron.base58_address

client = AsyncTron(AsyncHTTPProvider(endpoint))


async def get_tron_account_info(address: str = client_address):
    account_info = await client.get_account(address)
    balance = account_info.get('balance', 0)
    bandwidth = account_info.get('free_net_usage', 0)
    frozen_energy = next(
        (item for item in account_info.get('frozenV2', []) if item.get('type') == 'ENERGY'), None
    )
    energy = frozen_energy.get('amount') if frozen_energy else 0

    return {"balance": balance, "bandwidth": bandwidth, "energy": energy}
