"""
HayX P2P Protocol Definitions

Standard message types used for communication between nodes.
"""

# Message Types
MSG_GET_CHAIN = 'get_chain'
MSG_CHAIN = 'chain'
MSG_NEW_TRANSACTION = 'new_transaction'
MSG_NEW_BLOCK = 'new_block'
MSG_GET_PEERS = 'get_peers'
MSG_PEER_LIST = 'peer_list'

def create_message(msg_type, data=None):
    """Create a standard protocol message."""
    return {
        'type': msg_type,
        'data': data
    }

def parse_message(message):
    """Parse incoming message and return its type and data."""
    msg_type = message.get('type')
    data = message.get('data')
    return msg_type, data
