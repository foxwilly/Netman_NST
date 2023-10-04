from flask import Flask, render_template, request
from netmiko import ConnectHandler
import datetime

app = Flask(__name__)

# Define a list to store router configurations
router_configs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        # Get configuration parameters from the form
        hostname = request.form.get("hostname")
        username = request.form.get("username")
        password = request.form.get("password")
        config = request.form.get("config")

        # Store the router configuration in the list
        router_configs.append({
            "hostname": hostname,
            "username": username,
            "password": password,
            "config": config
        })

    txt_contents = []
    with open("config.cfg", 'r') as txt_file:
        txt_contents = txt_file.readlines()

   # return render_template("new_rtr.html", router_configs=txt_contents)
    return render_template("new_rtr.html", router_configs=router_configs, txt_contents=txt_contents)


@app.route("/get_config", methods=["GET", "POST"])
def get():
    txt_contents = []
    if request.method == "POST":
        # Get configuration parameters from the form
        file_name = request.form.get("file_name")
        # Generate a timestamp string
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Specify the original filename
        original_filename =  file_name 
        # Extract the file extension (if any)
        file_extension = original_filename.split(".")[-1] if "." in original_filename else ""
        name = original_filename.split(".")[0] if "." in original_filename else ""
        # Create a new filename with the timestamp
        path = "/home/willy/adv_netman/lab4/golden_config"
        new_filename = f"{path}/{name}_{timestamp}.{file_extension}" if file_extension else timestamp
        #open file
        contents = ""
        with open("config.cfg", 'r') as txt_file:
            contents = txt_file.read()
        # Save the file with the new filename
        with open(new_filename, "w") as file:
            file.write(contents)  # Replace with your file content

        print(f"File saved as {new_filename}")
        # Store the router configuration in the list
        txt_contents.append({
            "filename": f"{name}_{timestamp}.{file_extension}",
        })
        return render_template("get_conf.html", router_configs=txt_contents)
    else:
        if request.method == "GET":
            router = request.args.get('device')
        else:
            router = "2"
        device = {
        'device_type': 'cisco_ios',  # Use the appropriate device type
        'ip': 'clab-bgp-R'+""+router,
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
        with open("config.cfg",'w') as f: 
            f.write(running_config)
        
        
        with open("config.cfg", 'r') as txt_file:
            txt_contents = txt_file.readlines()


        return render_template("get_conf.html", router_configs=txt_contents)


if __name__ == "__main__":
    app.run(debug=True)
