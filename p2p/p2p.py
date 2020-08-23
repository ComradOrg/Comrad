import logging
import asyncio
import shelve
from collections import OrderedDict
import pickle,os

NODES_PRIME = [("128.232.229.63",8467), ("68.66.241.111",8467)] 
#68.66.224.46

def logger():
    import logging
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s]\n%(message)s\n')
    handler.setFormatter(formatter)
    logger = logging.getLogger(__file__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

LOG = None

def log(*x):
    global LOG
    if not LOG: LOG=logger().debug

    tolog=' '.join(str(_) for _ in x)
    LOG(tolog)

def boot_lonely_selfless_node(port=8467):
    async def go():
        from api import Api,PORT_LISTEN
        API = Api(log=log)
        await API.connect_forever(8467)
    asyncio.run(go())
    
