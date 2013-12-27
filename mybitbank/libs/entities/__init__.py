from coinwallet import CoinWallet


def getWallets(connector):
    '''
    Return a list of wallets
    '''
    wallets = []
    for provider_id , wallet_config in connector.config.items():
        wallet_config['provider_id'] = provider_id
        wallets.append(CoinWallet(wallet_config))
    return wallets

def getWalletByProviderId(connector, provider_id):
    '''
    Return the wallet for the provider_id
    '''
    wallets = getWallets(connector)
    for wallet in wallets:
        if wallet.provider_id == provider_id:
            return wallet
    else:
        return None
