from screens.base import ProtectedScreen
from screens.map import MapWidget
import asyncio


class RefreshScreen(ProtectedScreen):

    def on_pre_enter(self):
        if not super().on_pre_enter(): return

        async def go():    
            self.log(f'REFRESH: {self.app.is_logged_in}, {self.app.comrad.name}')
            if not hasattr(self.app,'map') or not self.app.map:
                self.app.map=MapWidget()
            self.app.map.open()
            await self.app.comrad.get_updates()
            self.app.map.dismiss()
            self.app.map=None
            self.app.go_back()

        asyncio.create_task(go())

