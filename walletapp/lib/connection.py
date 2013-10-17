import bitcoinrpc


def get_connection(node):
    return bitcoinrpc.connect_to_remote(
        node.rpcuser_decrypted,
        node.rpcpass_decrypted,
        host=node.rpchost,
        port=node.rpcport,
        use_https=node.rpchttps,
    )
