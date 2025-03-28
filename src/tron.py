from tronpy import Tron
from tronpy.providers import HTTPProvider

from src.config import load_config

client = Tron(HTTPProvider(load_config().tron.api_url))


def get_tron_account_info(address: str = load_config().tron.base58_address):
    try:
        account_info = client.get_account(address)
        balance = account_info.get('balance', 0)
        bandwidth = account_info.get('free_net_usage', 0)

        frozen_energy = next(
            (item for item in account_info.get('frozenV2') if item.get('type') == 'ENERGY'), None
        )

        energy = frozen_energy.get('amount') if frozen_energy else 0

        return {"balance": balance, "bandwidth": bandwidth, "energy": energy}

    except Exception as e:
        raise e
