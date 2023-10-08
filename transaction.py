# Example of accesing a remote API with a custom token key.
# (from contribution to: https://github.com/algorand/py-algorand-sdk)
# In this case, the API is expecting the key "X-API-Key" instead of the
# default "X-Algo-API-Token". This is done by using a dict with our custom
# key, instead of a string, as the token.

from algosdk.v2client import algod
import json
from base64 import b64decode
from algosdk import transaction
from algosdk.transaction import PaymentTxn
from utils import algod_details
from manage_account import get_user_account

userID = "user123"


def first_transaction_example(private_key, my_address, rec_address):
    algod_address, algod_token, headers = algod_details()

    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    account_info = algod_client.account_info(my_address)
    print(f"Account balance: {account_info.get('amount')} microAlgos")

    # build a transaction
    params = algod_client.suggested_params()

    # comment out next two lines to use suggested fees
    #params.flat_fee = True
    #params.fee = 1000
    receiver = rec_address

    # Read and parse the JSON file
    with open("metrics.json", "r") as file:
        metrics_data = json.load(file)
        # Assuming you want to encode 'people_metric' for this example
        metric_metadata = metrics_data
        # Convert the list to string and then encode
        all_data = []
        for key, values in metric_metadata.items():
            for value in values:
                all_data.append(f"{key}: {value}")
        # Convert the list to a single string and then encode
        note = ', '.join(all_data).encode()

    unsigned_txn = PaymentTxn(my_address, params, receiver, 0, None, note)

    # sign transaction
    signed_txn = unsigned_txn.sign(private_key)

    # submit the transaction and get back a transaction id
    txid = algod_client.send_transaction(signed_txn)
    print("Successfully submitted transaction with txID: {}".format(txid))

    # wait for confirmation
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
    except Exception as err:
        print(err)
        return

    print(f"Transaction information: {json.dumps(confirmed_txn, indent=4)}")
    print(f"Decoded note: {b64decode(confirmed_txn['txn']['txn']['note'])}")


private_key = "4pGX12svaEoBYqBX7WfriGIhUB3VjkeUofm6IM3Y+6b69JOah+47V6+PX/KeLfpDMv683zGwQ2R83pkdj7FwCA=="
my_address = "7L2JHGUH5Y5VPL4PL7ZJ4LP2IMZP5PG7GGYEGZD432MR3D5ROAEDKWFGRU"
rec_address = get_user_account(userID)['address']

first_transaction_example(private_key, my_address, rec_address)
