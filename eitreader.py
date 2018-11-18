#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Real time plotting of DeviceHive device' data using kivy
# Main Module
# 
# Copyright (C) 2018 Tomasz Cieplak
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# https://stackoverflow.com/questions/10762454/load-image-from-memory-in-kivy
# https://stackoverflow.com/questions/42328063/how-can-i-reload-a-image-in-kivy-python
# https://stackoverflow.com/questions/47778527/real-time-plotting-using-matplotlib-and-kivy-in-python
# https://github.com/jeysonmc/kivy_matplotlib
#
# =============================================================================
#import matplotlib

#matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')

from kivy.lang import Builder
from kivy.app import App
from kivy.core.image import Image as CoreImage

from io import BytesIO

from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.settings import SettingsWithTabbedPanel  # typ panelu ustawien

from config import json  # plik config.py zawiera wygląd interfejsu okna ustawień
from datasource import DeviceDataSource  # calosc obslugi zwiazanej z pozyskiwaniem danych z urzadzenia
from Reconstruction.greit import * #klasa do rekonstrukcji z algorytmem GREIT
import pandas as pd
import datetime

class EitReader(App):
    levels = []  # umieść dane przekazane z urządzenia

    #tworzenie interfejsu użytkownika
    def build(self):
        self.settings_cls = MySettingsWithTabbedPanel  # zaladowanie klasy panelu ustawien
        root = Builder.load_file("EitReader.kv")
        return root

    def build_config(self, config):
        """
        W sekcji Settings ustawiam pola url... i ich domyslne wartosci na ''.
        Gdy plik konfiguracyjny .ini nie istnieje w katalogu aplikacji
        """
        # config.setdefaults('Settings', {'url': '',
        #                                 'refresh_token': '',
        #                                 'device_id': '',
        #                                 'f0_references': ''
        #                                 })
        config.setdefaults('Settings', {'url': '',
                                        'login': '',
                                        'password':'',
                                        'device_id': '',
                                        'f0_references': ''
                                        })

    def build_settings(self, settings):
        """
        Dodaje okno ustawien zdefiniowane jako JSON w pliku config.py
        do obiektu okna ustawien konfiguracji
        """
        settings.add_json_panel('Settings', self.config, data=json)

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        Logger.info("eitreader.py App.on_config_change: {0}, {1}, {2}, {3}".format(
            config, section, key, value))

        # if section == "Settings":
        #    for led in range(8):
        #        if key == 'led%s' %led:
        #            if 'arduino' in globals():
        #                arduino.write(chr(led + 48).encode("ascii") + b'@' + chr(int(value) + 48).encode("ascii"))
        #            print(chr(led + 48).encode("ascii") + b'@' + chr(int(value) + 48).encode("ascii"))

    def close_settings(self, settings=None):
        """
        The settings panel has been closed.
        """
        Logger.info("EitReaderpy: App.close_settings: {0}".format(settings))
        super(EitReader, self).close_settings(settings)

    def on_start(self):
        url = self.config.get('Settings', 'url')  # 'http://91.232.58.246/api/rest'
        refresh_token = self.config.get('Settings',
                                        'refresh_token')  # 'eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjp7ImEiOlsyLDMsNCw1LDYsNyw4LDksMTAsMTEsMTIsMTUsMTYsMTddLCJlIjoxNTI1MDM5MjAwMDAwLCJ0IjowLCJ1IjoxOTQwLCJuIjpbIjE5MjEiXSwiZHQiOlsiKiJdfX0.HEjWzGRW5darX1KFe7R-WeWWlMTpXsh_MF8e493VkQA'
        refresh_token = self.config.get('Settings',
                                        'refresh_token')
        device_id = self.config.get('Settings', 'device_id')  # 'eit-device-0'
        #print(self.config.get('Settings', 'f0_references'))
        #try:
        #   ref_val = map(float, self.config.get('Settings', 'f0_references'))
        #except ValueError:
        #   print('Line {i} is corrupt!'.format())
        #   pass
        list = self.config.get('Settings', 'f0_references').split(",")
        f0_ref = pd.Series(list).astype(float) #pierwszy wiersz z pliku danych, typ danych float, sepraracja miejsc dzięsiętnych z kropką, separacja rekordów za pomoca przecinka
        app = App.get_running_app()
        app.eit_greit = GreitReconstruction(f0_ref) # tutaj ok, reszta od zmiany

#https://stackoverflow.com/questions/51806100/display-pil-image-on-kivy-canvas
class Window(BoxLayout):
    def __init__(self):
        super(Window, self).__init__()
        self.app = App.get_running_app()
        url = self.app.config.get('Settings', 'url')  # 'http://91.232.58.246/api/rest'
        #refresh_token = self.app.config.get('Settings',
        #                               'refresh_token')  # 'eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjp7ImEiOlsyLDMsNCw1LDYsNyw4LDksMTAsMTEsMTIsMTUsMTYsMTddLCJlIjoxNTI1MDM5MjAwMDAwLCJ0IjowLCJ1IjoxOTQwLCJuIjpbIjE5MjEiXSwiZHQiOlsiKiJdfX0.HEjWzGRW5darX1KFe7R-WeWWlMTpXsh_MF8e493VkQA'
        login = self.app.config.get('Settings', 'login')
        password = self.app.config.get('Settings','password')
        device_id = self.app.config.get('Settings', 'device_id')  # 'eit-device-0'

        #devicedata = DeviceDataSource(url, refresh_token, device_id)  # instancja obiektu, w ktorej ciagle dziala watek
        devicedata = DeviceDataSource(url, login, password, device_id)  # instancja obiektu, w ktorej ciagle dziala watek

        self.app.levels = devicedata.get_data()  # get_data przesyla strumien danych z instancji DataSource
        self.app.devicedata = devicedata


    def reset_plots(self):
        self.app.levels = []

    def start(self):
        self.ids.label1.text = 'Trwa rekonstrukcja...'
        self.ids.btn_start.enabled = False
        self.ids.btn_stop.enabled = True
        Clock.schedule_interval(self.get_value, 0.1)

    def stop(self):
        self.ids.label1.text = 'Czekam...'
        self.ids.btn_start.enabled = True
        self.ids.btn_stop.enabled = False
        Clock.unschedule(self.get_value)

    def get_value(self, dt):
        values = self.app.devicedata.get_data()
        time = self.app.devicedata.get_time()
        #self.ids.label_test.text = str(values[:])
        recon = self.app.eit_greit
        recon.f1 = pd.Series(values[:]).astype(float)
        recon.solve_ds()
        canvas_img = recon.image
        data = BytesIO()
        canvas_img.save(data, format='png')
        data.seek(0)  # yes you actually need this
        im = CoreImage(BytesIO(data.read()), ext='png')
        readable = datetime.datetime.fromtimestamp(time)
        self.ids.image.texture = im.texture
        self.ids.label2.text = readable.strftime('%Y-%m-%d %H:%M:%S')

class MySettingsWithTabbedPanel(SettingsWithTabbedPanel):
    """
    It is not usually necessary to create subclass of a settings panel. There
    are many built-in types that you can use out of the box
    (SettingsWithSidebar, SettingsWithSpinner etc.).

    You would only want to create a Settings subclass like this if you want to
    change the behavior or appearance of an existing Settings class.
    """

    def on_close(self):
        Logger.info("eitreader.py MySettingsWithTabbedPanel.on_close")

    def on_config_change(self, config, section, key, value):
        Logger.info(
            "EitReaderpy: MySettingsWithTabbedPanel.on_config_change: "
            "{0}, {1}, {2}, {3}".format(config, section, key, value))


'''
   Temp
'''

if __name__ == "__main__":
    EitReader().run()
