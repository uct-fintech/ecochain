from algosdk import asset, transaction, account, algod

creator_address = "YOUR_CREATOR_ADDRESS"
asset_name = "MyNFT"
unit_name = "NFT"
total_supply = 1  # This can be changed depending on how many NFTs you want to mint.

txn = asset.AssetConfigTxn(
    creator=creator_address,
    name=asset_name,
    unit_name=unit_name,
    total=total_supply,
    decimals=0,
    default_frozen=False,
    manager=creator_address,
    reserve=None,
    freeze=None,
    clawback=None,
    url="https://example.com/my-nft-metadata.json",
    strict_empty_address_check=False,
    metadata_hash=None
)

# Your Algorand Wallet's private key
creator_private_key = "YOUR_CREATOR_PRIVATE_KEY"

# Initialize the Algorand client
algod_client = algod.AlgodClient(algod_token="YOUR_ALGOD_API_KEY", algod_address="YOUR_ALGOD_ADDRESS")

# Retrieve the creator's account from the private key
creator_account = account.Account(creator_private_key)

# Sign the transaction
signed_txn = creator_account.sign_transaction(txn)

# Send the transaction to the Algorand network
tx_id = algod_client.send_transaction(signed_txn)



