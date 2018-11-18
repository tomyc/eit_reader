#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Real time plotting of DeviceHive device' data using kivy
# DeviceHiveDataSource
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
# =============================================================================

from threading import Thread
from devicehive import DeviceHiveApi


class DeviceDataSource(Thread):
    dev_obj = None

    #def __init__(self, url, refresh, dev_id):
    def __init__(self, url, login, password, dev_id):
        self.levels = []
        self.time = 0
        Thread.__init__(self)
        #self.dev_obj = self.get_device_object(url, refresh, dev_id)
        self.dev_obj = self.get_device_object(url, login, password, dev_id)
        self.daemon = True
        self.start()

    # def get_device_object(self, url_ws, r_token, d_id):
    #     device_hive_api = DeviceHiveApi(url_ws, refresh_token=r_token)
    #     device_id = d_id
    #     device_obj = device_hive_api.get_device(device_id)
    #     return device_obj

    def get_device_object(self, url_ws, r_login, r_password, d_id):
        device_hive_api = DeviceHiveApi(url_ws, login = r_login, password=r_password)
        device_id = d_id
        device_obj = device_hive_api.get_device(device_id)
        return device_obj

    def run(self):
        old_id = 0
        while True:
            notifications = self.dev_obj.list_notifications()
            if notifications:
                last_notification = notifications[0] # gdy -1 ostatnia wartość, pojemność bufora wynosi około 1 min 30 sek.
                if old_id != last_notification.id:
                    old_id = last_notification.id
                    state = last_notification.parameters['data']
                    time = last_notification.parameters['timestamp']
                    self.levels = state.get('eit')
                    self.time =time
                    #print(str(self.levels))

    def get_data(self):
        #print(str(self.levels))
        return self.levels

    def get_time(self):
        return self.time