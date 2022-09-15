import os
import meraki
import json
import time

# Defining your API key as a variable in source code is not recommended
API_KEY = os.getenv('MK_API_RW_HOME')


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
                except:
                    print('ping not available for ' + device["productType"])
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

    dashboard = meraki.DashboardAPI(
        API_KEY, suppress_logging=True)
    response = dashboard.administered.getAdministeredIdentitiesMe()
    print(response["name"]+' - '+response["email"])

    setPings(dashboard, fileName, deviceType, repeat)
    readPings(dashboard, fileName)
    results = open('pingResults.txt', "r")

    print(results.read())
    results.close()
