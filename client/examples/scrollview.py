from kivy.uix.scrollview import ScrollView


class EndEventScroll(ScrollView):

    def on_scroll_stop(self, *args, **kwargs):
        result = super(EndEventScroll, self).on_scroll_stop(*args, **kwargs)

        if self.scroll_y < 0 and hasattr(self, 'on_end_event'):
            self.on_end_event()
        return result


if __name__ == '__main__':
    from kivy.app import App

    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button
    from kivy.properties import ObjectProperty


    class CustomScrollView(EndEventScroll):

        layout1 = ObjectProperty(None)

        def on_end_event(self):
            height = 0.0

            for i in range(40):
                btn = Button(text=str(i), size_hint=(None, None),
                             size=(200, 100))
                self.layout1.add_widget(btn)
                height += btn.height
            height = float(height / self.layout1.cols)
            procent = (100.0 * height)/float(self.layout1.height)
            self.scroll_y += procent/100.0


    class ScrollViewApp(App):

        def build(self):
            layout1 = GridLayout(cols=4, spacing=10, size_hint=(None, None))
            layout1.bind(minimum_height=layout1.setter('height'),
                         minimum_width=layout1.setter('width'))
            for i in range(40):
                btn = Button(text=str(i), size_hint=(None, None),
                             size=(200, 100))
                layout1.add_widget(btn)
            scrollview1 = CustomScrollView(bar_width='2dp', layout1=layout1)
            scrollview1.add_widget(layout1)

            layout2 = GridLayout(cols=4, spacing=10, size_hint=(None, None))
            layout2.bind(minimum_height=layout2.setter('height'),
                         minimum_width=layout2.setter('width'))
            for i in range(40):
                btn = Button(text=str(i), size_hint=(None, None),
                             size=(200, 100))
                layout2.add_widget(btn)
            scrollview2 = ScrollView(scroll_type=['bars'],
                                     bar_width='9dp',
                                     scroll_wheel_distance=100)
            scrollview2.add_widget(layout2)

            root = GridLayout(cols=2)
            root.add_widget(scrollview1)
            root.add_widget(scrollview2)
            return root

    ScrollViewApp().run()