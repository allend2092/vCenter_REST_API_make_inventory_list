# This script will gather a sorted list of datacentere, esxi hosts and VMS
# from vCenter 172.17.0.100. The information will be put into a text file
#
# Author: Daryl Allen

import requests
import time
import datetime
import os
import getpass

username = input('Type your username: ')
password = getpass.getpass()

# Sometimes DNS does not provide consistent resolution. Sometimes its best to use ip address, or create a host file.
vcenter_url = 'https://172.17.0.100'

# This script makes many API calls and we don't want to overwhelm the interface. Throttle API calls here:
API_call_interval = .25

## Authentication request
response = requests.post(f'{vcenter_url}/rest/com/vmware/cis/session', auth=(username, password), verify=False)
token = response.json()
cookie = response.cookies
time.sleep(API_call_interval)

# Define header for making API calls that will hold authentication data
headersAPI = {
    'Accept': 'application/json',
    'Authorization': 'Bearer '+ token['value'],
    'Cookie': 'vmware-api-session-id=' + cookie.values()[0]
}

# This block of code was used to understand the various datastructures being returned from VC
# I request all Datacenter objects, all ESXi host objects, all VM objects to understand and manipulate later
# Request Datacenter info from vCenter
response = requests.get(f'{vcenter_url}/api/vcenter/datacenter',
                        headers=headersAPI,
                        verify=False)
datacenter_response = response.json()
time.sleep(API_call_interval)

# Get information from vCenter. Request ESXi host information
response = requests.get(f'{vcenter_url}/api/vcenter/host',
                        headers=headersAPI,
                        verify=False)
esxi_response = response.json()
time.sleep(API_call_interval)

# Get information from vCenter. Request ESXi host information
response = requests.get(f'{vcenter_url}/api/vcenter/vm',
                        headers=headersAPI,
                        verify=False)
vm_response = response.json()
time.sleep(API_call_interval)

# Print the information vCenter gave me
print(datacenter_response)
print(esxi_response)
print(vm_response)

# These variables are for counting the datacenter, ESXi hosts and VMs returned from VC
count_dcs = 0
count_esxi = 0
count_vm = 0

# These datastructures are needed for sorting the datacenter dictionary
dc_list_by_name = []
dc_list_by_moid = []

# I populate a list with data from a dictionary so that I can sort the dictionary
for record in datacenter_response:
    dc_list_by_name.append(record['name'])
    dc_list_by_moid.append(record['datacenter'])
    count_dcs += 1

# diagnostic code for checking the lists I have
# i = 0
# while i < count_dcs:
#     print(dc_list_by_name[i] + ' ' + dc_list_by_moid[i])
#     i +=1
# print()

# Creating a new list so that I can compare it to my old list in my sorting algorithm
sorted_dc_list = []

# Populating my new list
for item in dc_list_by_name:
    sorted_dc_list.append(item)

# Sorting my new list
sorted_dc_list.sort()

# Printing my list for diagnostic purposes
# i = 0
# while i < count_dcs:
#     print(dc_list_by_name[i] + ' ' + dc_list_by_moid[i])
#     i += 1

# Preparing a new list to file with sorted info
sorted_list_by_moid = []

# Here I am sorting the list of vCenter moid objects which represent the datacenters
i = 0
j = 0
print()
while i < count_dcs:
    while j < count_dcs:
        if sorted_dc_list[i] == dc_list_by_name[j]:
            sorted_list_by_moid.append(dc_list_by_moid[j])
        j = j + 1
    i = i + 1
    j = 0

# More diagnostic print statements
# i = 0
# while i < count_dcs:
#     print(sorted_dc_list[i] + ' ' + sorted_list_by_moid[i])
#     i += 1

# Here im creating a sorted dictionary to use for fetching info from vCenter
i = 0
for record in datacenter_response:
    record['name'] = sorted_dc_list[i]
    record['datacenter'] = sorted_list_by_moid[i]
    i = i + 1

# Opening a file to store the info retrieved from vCenter
resp = os.popen('mkdir DC-ESXi-VM-Info')
print(resp)
time.sleep(1)
f = open("./DC-ESXi-VM-Info/DC-ESXi-VM-Status.txt", "w")

x = datetime.datetime.now()
print('This data was collected: ' + str(x) + '\n')

f.write('This data was collected: ' + str(x) + ' MT\n\n')

# Fetch information and store it in my text file. Formatting included
for datacenters in datacenter_response:
    # Get information from vCenter. Request DATACENTER  information
    response = requests.get(f"{vcenter_url}/api/vcenter/host?datacenters={datacenters['datacenter']}",
                            headers=headersAPI,
                            verify=False)
    esxis_in_this_dc = response.json()
    time.sleep(API_call_interval)
    print('Datacenter: ' + datacenters['name'] + '\n')
    f.write('Datacenter: ' + datacenters['name'] + '\n')
    print('*******************************************')
    f.write('*******************************************')
    for single_esxi in esxis_in_this_dc:
        # Get information from vCenter. Request ESXi host information
        response = requests.get(f"{vcenter_url}/api/vcenter/vm?hosts={single_esxi['host']}",
                                headers=headersAPI,
                                verify=False)
        vm_on_this_host = response.json()
        time.sleep(API_call_interval)
        print('\n  Host: ' + single_esxi['name'] + ' ' + single_esxi['connection_state'] + '\n')
        f.write('\n  Host: ' + single_esxi['name'] + ' ' + single_esxi['connection_state'] + '\n')
        for vm in vm_on_this_host:
            print("    VM: " + vm['name'] + ' ' + vm['power_state'] +'\n')
            f.write("    VM: " + vm['name'] + ' ' + vm['power_state'] +'\n')
        print('\n')
    print('\n\n')
    f.write('\n\n')

f.close()

















