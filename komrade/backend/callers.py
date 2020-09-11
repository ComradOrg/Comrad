import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.cli import *
# from komrade.backend.the_telephone import *

# from komrade.backend.the_telephone import *


class Caller(Operator):
    """
    Variant of an Operator which handles local keys and keymaking.
    """

    def ring_ring(self,msg):
        # stop
        return super().ring_ring(
            msg,
            to_whom=self.op,
            get_resp_from=self.phone.ring_ring
        )



    # @hack: repurposing this for now as a narrator
