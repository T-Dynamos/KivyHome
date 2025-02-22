from kivy.animation import Animation
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, ListProperty, NumericProperty,
                             ObjectProperty, StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.utils import platform

from libs.android_launchapps import launch_app
from libs.utils import importer

__all__ = ('Applications', 'AppContainer', 'AppList', )

GetApps = importer(f'libs.icons.{platform}', 'GetPackages')
Builder.load_string('''
<ProgressHolder>:
    auto_dismiss: False
    background_color: .2, .2, .5, 0
    canvas.before:
        Color:
            rgba: 0, 0, 0, self.opacity
        RoundedRectangle:
            size: self.size
            pos: self.pos

    Image:
        size_hint: None, None
        source: 'assets/images/loading.gif'
        anim_delay: 1/20
        canvas.before:
            Color:
                rgba: 0, 0, 0, .5
            BoxShadow:
                pos: self.pos
                size: self.size
                offset: 0, 0
                spread_radius: -dp(20), -dp(20)
                border_radius: [dp(30), ] * 4
                blur_radius: dp(50)

<AppContainer>:
    padding: 0, dp(10), 0, app.cutout_height + dp(5) + dp(10)
    canvas.before:
        Color:
            rgba: 0, 0, 0, .3
        RoundedRectangle:
            pos: self.pos
            radius: [dp(15), ]
            size: self.size

    AppList:
        bar_width: dp(3)
        do_scroll_x: False
        BoxLayout:
            height: self.minimum_height
            padding: [dp(5), ] * 4
            size_hint_y: None
            Applications:
                size_hint_y: None
                height: self.minimum_height

''')

class ProgressHolder(ModalView):
    isbusy = BooleanProperty(None)
    opacity = NumericProperty(.6)

    def on_isbusy(self, *largs):
        if self.isbusy:
            self.open()
        else:
            a = Animation(opacity=0, d=1)
            a.bind(on_complete=self.dismiss)
            a.start(self)


class DesktopApplications(StackLayout):
    direction = StringProperty('up')
    initial = NumericProperty()
    target = StringProperty('all_apps')
    
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        self.initial = touch.x

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if all([
            self.collide_point(*touch.pos),
            touch.x > self.initial
        ]):
            App.get_running_app().change_target(self.direction,
                                                self.target)

            return True

        return False


class Applications(GetApps, StackLayout):  # type: ignore
    isbusy = BooleanProperty(False)
    padding = ListProperty([dp(10), ] * 4)
    popup = ObjectProperty()
    spacing = ListProperty([dp(10), ] * 2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = ProgressHolder()


class AppList(ScrollView):
    direction = StringProperty('down')
    event = BooleanProperty(False)
    scroll_distance = NumericProperty('40dp')
    scroll_timeout = NumericProperty(350)
    target = StringProperty('main')

    def on_scroll_y(self, *largs):
        if self.scroll_y > 1.22:
            self.event = not self.event

    def on_event(self, *largs):
        App.get_running_app().change_target(self.direction,
                                            self.target)

class AppContainer(BoxLayout):
    pass
