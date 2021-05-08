"""Kivy Demo app for retrieving the current weather."""
import requests
from kivy.app import App
from kivy.lang.builder import Builder
from textwrap import dedent
from kivy.clock import Clock


KV = dedent('''
BoxLayout:
    orientation: 'vertical'
    Label:
        canvas.before:
            Color:
                rgba: 0.2, 0.2, 0.6, 1
            Rectangle:
                pos: self.pos
                size: self.size
        size_hint_y: None
        height: "40dp"
        text: 'Weather fetcher'
        font_size: '20dp'
    Label:
        canvas.before:
            Color:
                rgba: 0.2, 0.2, 0.2, 1
            Rectangle:
                pos: self.pos
                size: self.size
        id: output_label
        text: 'Enter your city below and tap "Run" to start.'
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: "40dp"
        Button:
            id: button_run
            text: 'Get weather'
            on_press: app.start_check()
        TextInput:
            id: text_city
            text: 'Johannesburg'
        Button:
            text: 'Close'
            on_press: app.stop()
''')


class WeatherApp(App):
    """The Kivy Weather Application object."""

    def build(self):
        """Build and return our root widget."""
        return Builder.load_string(KV)

    def start_check(self):
        """Fetch the current weather details."""
        label = self.root.ids.output_label
        city = self.root.ids.text_city.text
        # The URL seems pretty arb, but it works. And this is just a demo :-)
        api_address = 'https://api.openweathermap.org/data/2.5/weather?' \
                      'q=Sydney,au&appid=a10fd8a212e47edf8d946f26fb4cdef8&q='
        units_format = "&units=metric"
        final_url = api_address + city + units_format
        json_data = requests.get(final_url).json()
        weather_details = get_weather_data(json_data, city)
        label.text = weather_details


def get_temperature(json_data):
    """Return the temperature in degrees celsius."""
    return json_data['main']['temp']


def get_weather_type(json_data):
    """Return a description of the weather type."""
    return json_data['weather'][0]['description']


def get_wind_speed(json_data):
    """Return the windspeed."""
    return json_data['wind']['speed']


def get_weather_data(json_data, city):
    """Return an English description of the weather details."""
    # description_of_weather = json_data['weather'][0]['description']
    weather_type = get_weather_type(json_data)
    temperature = get_temperature(json_data)
    wind_speed = get_wind_speed(json_data)
    weather_details = ''
    return weather_details + (
        "The weather in {} is currently {} with a temperature of {} degrees "
        "and wind speeds reaching {} km/ph".format(city, weather_type,
                                                   temperature, wind_speed))

WeatherApp().run()
