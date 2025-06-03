import hashlib
import hmac
from collections import OrderedDict

def validate_telegram_data(data: dict, bot_token: str) -> bool:
    received_hash = data.pop("hash")
    check_dict = {k: v for k, v in data.items() if v is not None}
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(check_dict.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return calculated_hash == received_hash