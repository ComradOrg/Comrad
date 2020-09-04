from screens.base import ProtectedScreen
from screens.feed.feed import *
from screens.post.post import *

class MessagesScreen(FeedScreen): 
    def on_pre_enter(self):
        if not self.app.username: return

        self.app.uri = '/inbox/'+self.app.username
        super().on_pre_enter()

