from Savoir import Savoir

from MedicalDispenser import settings

rpcuser = settings.MULTICHAIN_USER
rpcpasswd = settings.MULTICHAIN_PASS
rpchost = settings.MULTICHAIN_HOST
rpcport = settings.MULTICHAIN_PORT
chainname = settings.MULTICHAIN_CHAIN

chain = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)


# returns false if api call has error otherwise true
def check_call(test):
    if isinstance(test, dict) and 'error' in test:
        return False
    return True
