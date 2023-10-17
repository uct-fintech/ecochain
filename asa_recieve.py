from algosdk.v2client import algod
import json
from base64 import b64decode
from algosdk import transaction
from algosdk.transaction import PaymentTxn
from utils import algod_details


def asa_recieve (send_add, send_pk, rec_add, created_asset):
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