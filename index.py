# Define the network client
import json
import locale
from locale import currency

import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountNFTs
from xrpl.models.transactions import Memo, NFTokenCancelOffer, NFTokenMint
from xrpl.transaction import (safe_sign_and_autofill_transaction,
                              send_reliable_submission)
from xrpl.utils import drops_to_xrp, hex_to_str, str_to_hex
from xrpl.wallet import Wallet

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)





from xrpl.wallet import generate_faucet_wallet

cold_wallet = generate_faucet_wallet("rphGDfRgiFpMsqbF1KW6H9m2j9dva4ZRXp", debug=True)
hot_wallet = generate_faucet_wallet("r8k9a3RTfHfH6bNKnL4cvUQLsx2YB1hSrT", debug=True)

hot_settings_tx = xrpl.models.transactions.AccountSet(
    account=hot_wallet.classic_address,
    set_flag=xrpl.models.transactions.AccountSetFlag.ASF_REQUIRE_AUTH,
)

hst_prepared = xrpl.transaction.safe_sign_and_autofill_transaction(
    transaction=hot_settings_tx,
    wallet=hot_wallet,
    client=client,
)

print("Sending hot address AccountSet transaction...")
response = xrpl.transaction.send_reliable_submission(hst_prepared, client)
print(response)

cold_settings_tx = xrpl.models.transactions.AccountSet(
    account=cold_wallet,
    transfer_rate=0,
    tick_size=5,
    domain=bytes.hex("www.oaksfamilyfilms.com".encode("ASCII")),
    set_flag=xrpl.models.transactions.AccountSetFlag.ASF_DEFAULT_RIPPLE,
)

cst_prepared = xrpl.transaction.safe_sign_and_autofill_transaction(
    transaction=cold_settings_tx,
    wallet=cold_wallet,
    client=client,
)


print("Sending Cold Address AccountSet transaction...")
response = xrpl.transaction.send_reliable_submission(cst_prepared, client)
print(response)


currency_code = "FOO"
trust_set_tx = xrpl.models.transactions.TrustSet (
    account=hot_wallet.classic_address,
    limit_amount=xrpl.models.amount.issued_currency_amount.IssuedCurrencyAmount(
        currency=currency_code,
        issuer=cold_wallet.classic_address,
        value="100000000",
    )
)

ts_prepared = xrpl.transaction.safe_sign_and_autofill_transaction(
    transaction=trust_set_tx,
    wallet=hot_wallet,
    client=client,
)

print("Creating trust line from hot address to the issuer..")
response = xrpl.transaction.send_reliable_submission(ts_prepared,client)
print(response)


issue_quantity = "25000"
send_token_tx = xrpl.models.transactions.Payment(
    account=cold_wallet.classic_address,
    destination=hot_wallet.classic_address,
    amount=xrpl.mmodels.amounts.issued_currency_amount.IssuedCurrencyAmount(
        currency=currency_code,
        issuer=cold_wallet.classic_address,
        value=issue_quantity
    )
)

pay_prepared = xrpl.transaction.safe_sign_and_autofill_transaction(
    transaction=send_token_tx,
    wallet=cold_wallet,
    client=client,
)

print(f"Sending {issue_quantity} {currency_code} to {hot_wallet.classic_address}...")
response = xrpl.transaction.send_reliable_submission(pay_prepared, client)
print(response)


print("Getting hot address balances...")
response = client.request(xrpl.models.requests.AccountLines(
    account=hot_wallet.classic_address,
    ledger_index="validated",
))

print(response)

print("Getting Cold Wallet Balances...")
response = client.request(xrpl.models.requests.GatewayBalances(
    account=cold_wallet.classic_address,
    ledger_index="validated",
    hotwallet=[hot_wallet.classic_address]
))
print(response)



from xrpl.core import addresscodec

hot_xwallet = addresscodec.classic_address_to_xaddress(hot_wallet, tag=12345, is_test_network=True)
print("\nClassic address:\n\n", hot_wallet)
print("X-address:\n\n", hot_xwallet)


from xrpl.models.requests.account_info import AccountInfo

acct_info = AccountInfo(
    account=cold_wallet,
    ledger_index="validated",
    strict=True,
)
response = client.request(acct_info)
result = response.result
print("response.status: ", response.status)



print(json.dumps(response.result, indent=4, sort_keys=True))

