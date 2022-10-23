import os
import meraki
import json
import time
import logging
from pingerobj import Pinger
import texttable as tt

# Defining your API key as a variable in source code is not recommended
API_KEY = os.getenv('API_KEY_RW')

# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/


def timer(seconds, printOnScreen=False):
    for y in range(0, seconds):
        if printOnScreen:
            print(f"Retry in: {seconds-y}")
        time.sleep(1)


def setPings(dashboard, deviceType='any', repeat=2):
    pings = []
    p = {}
    response = dashboard.organizations.getOrganizations()

    logging.info('collecting device serials')

    # of each organization of the user
    for org in response:
        # print id and name
        print(org["id"], org["name"])
        # get device status
        devices = dashboard.organizations.getOrganizationDevicesStatuses(
            org["id"], total_pages='all')
        for device in devices:
            # filter by selected type and online
            # print(device)
            # skip sensors and sig

            if (device["productType"] == deviceType or deviceType == 'any') and device["status"] == 'online':
                try:
                    # set up ping for serial
                    ping = dashboard.devices.createDeviceLiveToolsPingDevice(
                        device["serial"], count=repeat)
                    # write serial number to file
                    #ping = Pinger(device["name"], device["serial"], ping["pingId"])

                    #p['name'] = device["name"]
                    #p['serial'] = device["serial"]
                    #p['pingId'] = ping["pingId"]

                    pings.append(
                        {"name": device["name"], "serial": device["serial"], "pingId": ping["pingId"]})

                except Exception as e:
                    logging.debug(e)
                    print('ping not available for ' +
                          device["productType"] + ' / ' + device["status"])

    # create and print table with ping set up
    tb = tt.Texttable()
    tb.set_cols_dtype(['t', 't', 't'])

    tb.header(["Name", "Serial", " ID"])

    for pi in pings:
        tb.add_row(pi.values())
        # print(repr(ping1))
        #tb.add_row(["serial", " ID"])
    print(tb.draw())
    # return set up pings
    return (pings)


def readPings(dashboard, pings):

    tb = tt.Texttable()
    tb.set_cols_dtype(['t', 't', 't', 't', 't'])
    tb.header(["Name", "Serial", " ID", "sent/rec", "fail %"])

    # for all the line in the file [seria],[pingid]
    for pingJob in pings:

        # print(pingJob)
        device = pingJob['serial']
        pId = pingJob['pingId']

        pingstatus = dashboard.devices.getDeviceLiveToolsPingDevice(
            device, pId)

        # try:
        #    deviceName = dashboard.devices.getDevice(device)['name']
        # except:
        #    deviceName = 'UNKNOWN'

        seconds = 2
        while pingstatus["status"] == 'ready' or pingstatus["status"] == 'running':
            timer(seconds)
            seconds = seconds + 2
            pingstatus = dashboard.devices.getDeviceLiveToolsPingDevice(
                device, pId)

        pingJob['sr'] = str(pingstatus['results']['sent']) + \
            "/" + str(pingstatus['results']['received'])

        pingJob['loss'] = str(pingstatus['results']
                              ['loss']['percentage']) + " %"

        tb.add_row(pingJob.values())

    print(tb.draw())


if __name__ == "__main__":
    repeat = 3
    fileName = 'mylist'
    deviceType = 'any'
    #deviceType = 'any'

    print(API_KEY)

    logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(filename='app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')

    dashboard = meraki.DashboardAPI(
        API_KEY, suppress_logging=True)
    response = dashboard.administered.getAdministeredIdentitiesMe()
    logging.debug(response["name"]+' - '+response["email"])

    pings = setPings(dashboard, deviceType, repeat)
    readPings(dashboard, pings)
