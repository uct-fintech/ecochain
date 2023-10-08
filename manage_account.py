import accounts_data
from algosdk import account


def get_user_account(user_id):
    # Check if user is in the user_data dictionary
    if user_id in accounts_data.user_data:
        return accounts_data.user_data[user_id]
    else:
        return createUserAccount(user_id)


def createUserAccount(user_id):
    # Generate a new Algorand key pair
    private_key, address = account.generate_account()

    # Store the new user's data in the accounts_data dictionary
    accounts_data.user_data[user_id] = {"address": address, "private_key": private_key}

    return accounts_data.user_data[user_id]
