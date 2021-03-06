#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_sync.py)
$ python3 test_pytradfri.py <IP> <KEY>

Where <IP> is the address to your IKEA gateway and
<KEY> is found on the back of your IKEA gateway.
"""

import sys
import threading

import time

from pytradfri import Gateway
from pytradfri.api.libcoap_api import api_factory


def observe(api, device):
    def callback(updated_device):
        light = updated_device.light_control.lights[0]
        print("Received message for: %s" % light)

    def err_callback(err):
        print(err)

    def worker():
        api(device.observe(callback, err_callback, duration=120))

    threading.Thread(target=worker, daemon=True).start()
    print('Sleeping to start observation task')
    time.sleep(1)


def run():
    # Assign configuration variables.
    # The configuration check takes care they are present.
    api = api_factory(sys.argv[1], sys.argv[2])

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    tasks_command = gateway.get_smart_tasks()
    tasks = api(tasks_command)

    # Print all lights
    print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    light = lights[0]

    observe(api, light)

    # Example 1: checks state of the light 2 (true=on)
    print(light.light_control.lights[0].state)

    # Example 2: get dimmer level of light 2
    print(light.light_control.lights[0].dimmer)

    # Example 3: What is the name of light 2
    print(light.name)

    # Example 4: Set the light level of light 2
    dim_command = light.light_control.set_dimmer(255)
    api(dim_command)

    # Example 5: Change color of light 2
    # f5faf6 = cold | f1e0b5 = normal | efd275 = warm
    color_command = light.light_control.set_hex_color('efd275')
    api(color_command)

    # Example 6: Return the transition time (in minutes) for task#1
    if tasks:
        print(tasks[0].task_control.tasks[0].transition_time)

        # Example 7: Set the dimmer stop value to 30 for light#1 in task#1
        dim_command_2 = tasks[0].start_action.devices[0].item_controller\
            .set_dimmer(30)
        api(dim_command_2)

    print("Sleeping for 2 min to receive the rest of the observation events")
    print("Try altering the light (%s) in the app, and watch the events!" %
          light.name)
    time.sleep(120)


run()
