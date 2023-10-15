from algosdk.v2client import algod
import json
from base64 import b64decode
from algosdk import transaction
from algosdk.transaction import PaymentTxn
from utils import algod_details


def asa_opt_in (acct2_address,acct2_privatekey,created_asset):   
    algod_address, algod_token, headers = algod_details()
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    sp = algod_client.suggested_params()
    # Create opt-in transaction
    # asset transfer from me to me for asset id we want to opt-in to with amt==0
    optin_txn = transaction.AssetOptInTxn(
        sender=acct2_address, sp=sp, index=created_asset
    )
    signed_optin_txn = optin_txn.sign(acct2_privatekey)
    txid = algod_client.send_transaction(signed_optin_txn)
    print(f"Sent opt in transaction with txid: {txid}")

    # Wait for the transaction to be confirmed
    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")