import logging
import asyncio
import shelve
from collections import OrderedDict
import pickle,os

NODES_PRIME = [("128.232.229.63",8467), ("68.66.241.111",8467)] 
#68.66.224.46


def boot_lonely_selfless_node(port=8467):
    async def go():
        from api import Api,PORT_LISTEN
        API = Api()
        await API.connect_forever(8467)
    asyncio.run(go())
    
