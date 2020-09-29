import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
from comrad.backend import *
from comrad.cli import *
# from comrad.backend.the_telephone import *

# from comrad.backend.the_telephone import *


class Caller(Operator):
    """
    Variant of an Operator which handles local keys and keymaking.
    """

    async def ring_ring(self,msg,**y):
        # stop
        return await super().ring_ring(
            msg,
            to_whom=self.op,
            get_resp_from=self.phone.ring_ring,
            **y
        )



    # @hack: repurposing this for now as a narrator
