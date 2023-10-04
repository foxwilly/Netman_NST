from netmiko import ConnectHandler

# Define the device information (replace with your router's details)
device = {
    'device_type': 'cisco_ios',  # Use the appropriate device type
    'ip': 'clab-bgp-R1',
    'username': 'admin',
    'password': 'admin',
    'secret': 'your_enable_password',  # If you have an enable password
}

# Connect to the router
net_connect = ConnectHandler(**device)

# Enter enable mode if necessary
if not net_connect.check_enable_mode():
    net_connect.enable()

# Retrieve the running configuration
running_config = net_connect.send_command("show running-config")

# Disconnect from the router
net_connect.disconnect()

# Print the running configuration
print(running_config)

