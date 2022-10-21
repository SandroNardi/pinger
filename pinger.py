import os
import meraki
import json
import time
import apikey
import logging

# Defining your API key as a variable in source code is not recommended
API_KEY = apikey.API_KEY_RW

# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/


def timer(seconds, printOnScreen=False):
    for y in range(0, seconds):
        if printOnScreen:
            print(f"Retry in: {seconds-y}")
        time.sleep(1)


def setPings(dashboard, fileName, deviceType='any', repeat=2):
    response = dashboard.organizations.getOrganizations()
    # open file
    pingId = open(fileName + '.txt', "w")

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
                    pingId.write(device["serial"]+",")
                    # write ping id to file
                    pingId.write(ping["pingId"]+"\n")
                except Exception as e:
                    logging.error(e)
                    print('ping not available for ' +
                          device["productType"] + ' / ' + device["status"])
    # close file
    pingId.close()


def readPings(dashboard, fileName):
    # read ping results
    pingId = open(fileName + '.txt', "r")
    pingResults = open('pingResults.txt', "w")
    # for all the line in the file [seria],[pingid]
    for pingJob in pingId:
        # strip new line
        pingJob = pingJob.rstrip('\n')
        pingObj = pingJob.split(",")
        # print(x)
        device = pingObj[0]
        pId = pingObj[1]

        pingstatus = dashboard.devices.getDeviceLiveToolsPingDevice(
            device, pId)
        # print(dashboard.devices.getDevice(device))
        try:
            deviceName = dashboard.devices.getDevice(device)['name']
        except:
            deviceName = 'UNKNOWN'
        seconds = 2
        while pingstatus["status"] == 'ready' or pingstatus["status"] == 'running':

            timer(seconds)
            seconds = seconds + 2
            pingstatus = dashboard.devices.getDeviceLiveToolsPingDevice(
                device, pId)

        pingResults.write(
            deviceName+' , '+pingstatus["status"]+' , '+json.dumps(pingstatus["results"])+'\n')
    pingId.close()
    pingResults.close()


if __name__ == "__main__":
    repeat = 3
    fileName = 'mylist'
    deviceType = 'any'

    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(filename='app.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')

    dashboard = meraki.DashboardAPI(
        API_KEY, suppress_logging=True)
    response = dashboard.administered.getAdministeredIdentitiesMe()
    logging.debug(response["name"]+' - '+response["email"])

    setPings(dashboard, fileName, deviceType, repeat)
    readPings(dashboard, fileName)
    results = open('pingResults.txt', "r")

    print(results.read())
    results.close()
