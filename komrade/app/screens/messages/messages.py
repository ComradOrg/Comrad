from screens.base import ProtectedScreen
from screens.feed.feed import *
from screens.post.post import *

class MessagesScreen(FeedScreen): 
    def on_pre_enter(self):
        if not super().on_pre_enter(): return

        self.get_posts = self.app.komrade.messages

