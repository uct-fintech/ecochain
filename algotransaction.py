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



def first_transaction_example(private_key, my_address, rec_address, specAmount, metric_metadata):
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


    all_data = []
    for key, value in metric_metadata.items():
        all_data.append(f"{key}: {value}")
        # Convert the list to a single string and then encode
    note = ', '.join(all_data).encode()

    unsigned_txn = PaymentTxn(
        sender=my_address,
        sp=params,
        receiver=rec_address,
        amt=specAmount,
        note=note,
    )

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
        return txid
    
    print(f"Transaction information: {json.dumps(confirmed_txn, indent=4)}")
    print(f"Decoded note: {b64decode(confirmed_txn['txn']['txn']['note'])}")
    
    return txid, confirmed_txn


