# import logging
# import asyncio

# from kademlia.network import Server
# from kademlia.storage import *
# import shelve
# from collections import OrderedDict
# import pickle,os

# class HalfForgetfulStorage(ForgetfulStorage):
#     def __init__(self, ttl=604800):
#         """
#         By default, max age is a week.
#         """
#         self.fn='sto.dat'
#         if not os.path.exists(self.fn):
#             self.data={}
#         else:
#             with open(self.fn,'rb') as f:
#                 self.data=pickle.load(f)


#         print('loaded:',self.data)

#         #self.data = pickle.open('sto.dat','rb') #,writeback=True)
#         # self.data = self.store.get('OrderedDict',OrderedDict())
#         self.ttl = ttl

#     def __setitem__(self, key, value):
#         self.data[key] = (time.monotonic(), value)
#         self.write()

#     def write(self):
#         with open(self.fn,'wb') as f:
#             pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)

#     def get(self, key, default=None):
#         # self.cull()
#         if key in self.data:
#             print('????',self.data[key])
#             return self[key]
#         return default

#     def __getitem__(self, key):
#         return self.data[key][1]

#     def __repr__(self):
#         return repr(self.data)

#     def iter_older_than(self, seconds_old):
#         min_birthday = time.monotonic() - seconds_old
#         zipped = self._triple_iter()
#         matches = takewhile(lambda r: min_birthday >= r[1], zipped)
#         return list(map(operator.itemgetter(0, 2), matches))

#     def _triple_iter(self):
#         ikeys = self.data.keys()
#         ibirthday = map(operator.itemgetter(0), self.data.values())
#         ivalues = map(operator.itemgetter(1), self.data.values())
#         return zip(ikeys, ibirthday, ivalues)

#     def __iter__(self):
#         ikeys = self.data.keys()
#         ivalues = map(operator.itemgetter(1), self.data.values())
#         return zip(ikeys, ivalues)


# # handler = logging.StreamHandler()
# # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # handler.setFormatter(formatter)
# # log = logging.getLogger('kademlia')
# # log.addHandler(handler)
# # log.setLevel(logging.DEBUG)


# loop = asyncio.get_event_loop()
# loop.set_debug(True)


# shelf = HalfForgetfulStorage()

# server = Server(storage=shelf)
# loop.run_until_complete(server.listen(8468))

# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass
# finally:
#     server.stop()
#     loop.close()
