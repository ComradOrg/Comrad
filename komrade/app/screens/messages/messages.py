from screens.base import ProtectedScreen
from screens.feed.feed import *
from screens.post.post import *

class MessagesScreen(FeedScreen): 
    def on_pre_enter(self):
        if not self.app.komrade: return

        self.get_posts = self.app.komrade.messages
        super().on_pre_enter()

