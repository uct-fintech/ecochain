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

def createASA(private_key, my_address, transID1):
    algod_address, algod_token, headers = algod_details()
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    account_info = algod_client.account_info(my_address)
    print(f"Account balance: {account_info.get('amount')} microAlgos")

    # build a transaction
    params = algod_client.suggested_params()

    # comment out next two lines to use suggested fees
    #params.flat_fee = True
    #params.fee = 1000
    txn = transaction.AssetConfigTxn(
    sender=my_address,
    sp=params,
    default_frozen=False,
    unit_name="rug",
    asset_name="Really Useful Gift",
    manager=my_address,
    reserve=None,
    freeze=None,
    clawback=None,
    url="https://testnet.algoexplorer.io/tx/" + transID1,
    strict_empty_address_check=False,
    total=1,
    decimals=0,
    )
    
        # Sign with secret key of creator
    signed_txn = txn.sign(private_key)
    # Send the transaction to the network and retrieve the txid.
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent asset create transaction with txid: {txid}")

    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
    except Exception as err:
        print(err)
        return 

    # grab the asset id for the asset we just created
    created_asset = confirmed_txn["asset-index"]
    print(f"Asset ID created: {created_asset}")

    return txid, confirmed_txn, created_asset


def optinASA(acct2_address,acct2_privatekey,created_asset):   
    algod_address, algod_token, headers = algod_details()
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    sp = algod_client.suggested_params()
    # Create opt-in transaction
    # asset transfer from me to me for asset id we want to opt-in to with amt==0
    optin_txn = transaction.AssetOptInTxn(
        sender=acct2_address, sp=sp, index=created_asset
    )
    signed_optin_txn = optin_txn.sign(acct2_privatekey)
    signed_optin_txid = algod_client.send_transaction(signed_optin_txn)
    print(f"Sent opt in transaction with txid: {signed_optin_txid}")

    # wait for confirmation
    try:
        results = transaction.wait_for_confirmation(algod_client, signed_optin_txid, 4)
    except Exception as err:
        print(err)
        return signed_optin_txid

    print(f"Result confirmed in round: {results['confirmed-round']}")

    return signed_optin_txid, results


def transferASA (send_add, send_pk, rec_add, created_asset):
    algod_address, algod_token, headers = algod_details()
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)
    sp = algod_client.suggested_params()
    # Create opt-in transaction
    # asset transfer from me to me for asset id we want to opt-in to with amt==0
    xfer_txn  = transaction.AssetTransferTxn(
        sender=send_add,
        sp=sp,
        receiver=rec_add,
        amt=1,
        index=created_asset,
    )
    signed_xfer_txn = xfer_txn.sign(send_pk)
    txid = algod_client.send_transaction(signed_xfer_txn)
    print(f"Sent transfer transaction with txid: {txid}")

 # wait for confirmation
    try:
        results = transaction.wait_for_confirmation(algod_client, txid, 4)
    except Exception as err:
        print(err)
        return txid
    
    print(f"Result confirmed in round: {results['confirmed-round']}")

    return txid, results
