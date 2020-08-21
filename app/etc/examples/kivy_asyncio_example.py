"""
Kivy asyncio example app.

Kivy needs to run on the main thread and its graphical instructions have to be
called from there.  But it's still possible to run an asyncio EventLoop, it
just has to happen on its own, separate thread.

Requires Python 3.5+.
"""

import kivy

kivy.require('1.10.0')

import asyncio
import threading

from kivy.app import App
from kivy.clock import mainthread
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout


KV = '''\
<RootLayout>:
    orientation: 'vertical'
    Button:
        id: btn
        text: 'Start EventLoop thread.'
        on_press: app.start_event_loop_thread()
    TextInput:
        multiline: False
        size_hint_y: 0.25
        on_text: app.submit_pulse_text(args[1])
    BoxLayout:
        Label:
            id: pulse_listener    
        Label:
            id: status
'''


class RootLayout(BoxLayout):
    pass


class EventLoopWorker(EventDispatcher):

    __events__ = ('on_pulse',)  # defines this EventDispatcher's sole event

    def __init__(self):
        super().__init__()
        self._thread = threading.Thread(target=self._run_loop)  # note the Thread target here
        self._thread.daemon = True
        self.loop = None
        # the following are for the pulse() coroutine, see below
        self._default_pulse = ['tick!', 'tock!']
        self._pulse = None
        self._pulse_task = None

    def _run_loop(self):
        self.loop = asyncio.get_event_loop_policy().new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._restart_pulse()
        # this example doesn't include any cleanup code, see the docs on how
        # to properly set up and tear down an asyncio event loop
        self.loop.run_forever()

    def start(self):
        self._thread.start()

    async def pulse(self):
        """Core coroutine of this asyncio event loop.

        Repeats a pulse message in a short interval on three channels:

        - using `print()`
        - by dispatching a Kivy event `on_pulse` with the help of `@mainthread`
        - on the Kivy thread through `kivy_update_status()` with the help of
          `@mainthread`

        The decorator `@mainthread` is a convenience wrapper around
        `Clock.schedule_once()` which ensures the callables run on the Kivy
        thread.
        """
        for msg in self._pulse_messages():
            # show it through the console:
            print(msg)

            # `EventLoopWorker` is an `EventDispatcher` to which others can
            # subscribe. See `display_on_pulse()` in `start_event_loop_thread()`
            # on how it is bound to the `on_pulse` event.  The indirection
            # through the `notify()` function is necessary to apply the
            # `@mainthread` decorator (left label):
            @mainthread
            def notify(text):
                self.dispatch('on_pulse', text)

            notify(msg)  # dispatch the on_pulse event

            # Same, but with a direct call instead of an event (right label):
            @mainthread
            def kivy_update_status(text):
                status_label = App.get_running_app().root.ids.status
                status_label.text = text

            kivy_update_status(msg)  # control a Label directly

            await asyncio.sleep(1)


    def set_pulse_text(self, text):
        self._pulse = text
        # it's not really necessary to restart this task; just included for the
        # sake of this example.  Comment this line out and see what happens.
        self._restart_pulse()

    def _restart_pulse(self):
        """Helper to start/reset the pulse task when the pulse changes."""
        if self._pulse_task is not None:
            self._pulse_task.cancel()
        self._pulse_task = self.loop.create_task(self.pulse())

    def on_pulse(self, *_):
        """An EventDispatcher event must have a corresponding method."""
        pass

    def _pulse_messages(self):
        """A generator providing an inexhaustible supply of pulse messages."""
        while True:
            if isinstance(self._pulse, str) and self._pulse != '':
                pulse = self._pulse.split()
                yield from pulse
            else:
                yield from self._default_pulse


class AsyncioExampleApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_loop_worker = None

    def build(self):
        return RootLayout()

    def start_event_loop_thread(self):
        """Start the asyncio event loop thread. Bound to the top button."""
        if self.event_loop_worker is not None:
            return
        self.root.ids.btn.text = ("Running the asyncio EventLoop now...\n\n\n\n"
                                  "Now enter a few words below.")
        self.event_loop_worker = worker =  EventLoopWorker()
        pulse_listener_label = self.root.ids.pulse_listener

        def display_on_pulse(instance, text):
            pulse_listener_label.text = text

        # make the label react to the worker's `on_pulse` event:
        worker.bind(on_pulse=display_on_pulse)
        worker.start()

    def submit_pulse_text(self, text):
        """Send the TextInput string over to the asyncio event loop worker."""
        worker = self.event_loop_worker
        if worker is not None:
            loop = self.event_loop_worker.loop
            # use the thread safe variant to run it on the asyncio event loop:
            loop.call_soon_threadsafe(worker.set_pulse_text, text)


if __name__ == '__main__':
    Builder.load_string(KV)
    AsyncioExampleApp().run()
