from flask import Flask, render_template, request, send_from_directory, render_template_string
from netmiko import ConnectHandler
import datetime
import requests
import json
import sqlite3
import autotools as at

app = Flask(__name__)

# Define a list to store router configurations
router_configs = []

@app.route('/')
def index():
    return render_template('index3.html')

# Here I define the path ute to serve the HTML coverage files
@app.route('/home/willy/htmlcov/<path:filename>')
def serve_coverage(filename):
    directory_path = '/home/willy/htmlcov/'  # Replace with the actual path to your coverage report directory
    return send_from_directory(directory_path, filename)


@app.route("/auto", methods=["GET", "POST"])
def auto():
    result={}
    d5 = {'device_type': 'cisco_ios','ip': 'clab-bgp-R5','username': 'admin','password': 'admin','secret': '',}
    d4 = {'device_type': 'cisco_ios','ip': 'clab-bgp-R4','username': 'admin','password': 'admin','secret': '',}
    d3 = {'device_type': 'cisco_ios','ip': 'clab-bgp-R3','username': 'admin','password': 'admin','secret': '',}
    devices=[d5,d4,d3]
    try:
        for device in devices:
            # Establish an SSH connection to the router
            with ConnectHandler(**device) as ssh_conn:
                # Send the 'show bgp summary' command and capture the output
                if not ssh_conn.check_enable_mode():
                    ssh_conn.enable()
                output = ssh_conn.send_command('show bgp summary')

            # Parse the BGP neighbor information from the command output
            bgp_neighbors = [line.split() for line in output.splitlines() if 'Established' in line]
            result[device['ip']]= bgp_neighbors
        return render_template('auto.html', routers=result)
    except Exception as e:
        return f"Error: {str(e)}"



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




@app.route("/get_ips", methods=["GET", "POST"])
def get_ips():
    if request.method == "POST":
        # Make a GET request to an APIhttp://172.17.0.7/api/myApp/addresses/first_free/9/ 
        ip = request.form.get("ip")
        headers = {'token': 'ak_0sFTHh4o-ak-_C5_k2c75'}
        response = requests.post('http://172.17.0.3/api/myApp/addresses/first_free/9/', headers=headers)
        data = response.json()  # Parse the response as JSON
    else:
    # Make a GET request to an API
        headers = {'token': 'ak_0sFTHh4o-ak-_C5_k2c75'}
        response = requests.get('http://172.17.0.3/api/myApp/subnets/9/first_free', headers=headers)
        data = response.json()  # Parse the response as JSON



    return render_template('get_ips.html', data=data)

   # return render_template("new_rtr.html", router_configs=txt_contents)
    #return render_template("new_rtr.html", router_configs=router_configs, txt_contents=txt_contents)


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

@app.route("/listconfigs")
def listconfigs():
    return render_template("listconfigs.html")

# code to creat and edit router configuration via GUI
# Home Page route
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/tshoot")
def tshoot():
       # Connect to the SQLite3 datatabase and 
    # SELECT rowid and all Rows from the students table.
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM steps")

    rows = cur.fetchall()
    con.close()
    # Send the results of the SELECT to the list.html page
    #return render_template("list.html",rows=rows)
    return render_template("tshoot.html",rows=rows)


# Route to form used to add a new student to the database
@app.route("/enternew")
def enternew():
    return render_template("student.html")

# Route to add a new record (INSERT) student data to the database
@app.route("/addrec", methods = ['POST', 'GET'])
def addrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            host = request.form['host']
            type = request.form['type']
            usr = request.form['usr']
            pwd = request.form['pwd']
            file = request.form['file']
            inter = request.form['inter']
            ip = request.form['ip']
            proto = request.form['proto']


            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO routers (hostname, type, username, password, file, interface, ip, proto) VALUES (?,?,?,?,?,?,?,?)",
                            (host, type, usr, pwd, file, inter, ip, proto))
                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

# Route to SELECT all data from the database and display in a table      
@app.route('/list')
def list():
    # Connect to the SQLite3 datatabase and 
    # SELECT rowid and all Rows from the students table.
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM routers")

    rows = cur.fetchall()
    con.close()
    # Send the results of the SELECT to the list.html page
    return render_template("list.html",rows=rows)

# Route that will SELECT a specific row in the database then load an Edit form 
@app.route("/edit", methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            id = request.form['id']
            # Connect to the database and SELECT a specific rowid
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM routers WHERE rowid = " + id)

            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            # Send the specific record of data to edit.html
            return render_template("edit.html",rows=rows)

# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST','GET'])
def editrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['rowid']
            host = request.form['host']
            type = request.form['type']
            usr = request.form['usr']
            pwd = request.form['pwd']
            file = request.form['file']
            inter = request.form['inter']
            ip = request.form['ip']
            proto = request.form['proto']

            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
              #  cur.execute("UPDATE students SET name='"+nm+"', addr='"+addr+"', city='"+city+"', zip='"+zip+"' WHERE rowid="+rowid)
                cur.execute("UPDATE routers SET hostname='"+host+"', type='"+type+"', username='"+usr+"', password='"+pwd+"', file='"+file+"', interface='"+inter+"', ip='"+ip+"', proto='"+proto+"' WHERE rowid="+rowid)
                con.commit()
                msg = "Record successfully edited in the database"
        except:
            con.rollback()
            msg = "Error in the Edit: UPDATE routers SET hostname="+host+", type="+type+", file="+file+", interface="+inter+", ip="+ip+", protocol="+proto+" WHERE rowid="+rowid

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

# Route used to DELETE a specific record in the database    
@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
             # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['id']
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM routers WHERE rowid="+rowid)

                    con.commit()
                    msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)


# Route to add a new record (INSERT) student data to the database
@app.route("/addsteps", methods = ['POST', 'GET'])
def addsteps():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            name = request.form['name']
            step = request.form['step']
            action = request.form['action']
            status = request.form['status']
            checks = request.form['checks']
            question = request.form['question']

            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO steps (name, step, action, status, checks, question) VALUES (?,?,?,?,?,?)",
                            (name, step, action, status, checks, question))
                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('tshoot.html',msg=msg)
    else:
        return render_template('ts_steps.html')


@app.route("/review", methods=['POST','GET'])
def review():
    if request.method == 'POST':
        try:
            vform = "tshoot.html"
            print(request.form['id'])
            # id 1 means the step1 (connectivity) in the tshoot list
            if request.form['vaction'] =="review" and request.form['id'] =="1":
                msg = at.inspector()
            # id 3 means the step3 (config files) in the tshoot list
            elif request.form['vaction'] =="review" and request.form['id'] =="3":
                result, isdiff = at.compare_configs("test_2023-10-03_21-20-25.cfg","test_2023-10-03_21-20-26.cfg")
                if isdiff:
                    msg=result
                    vform = "result2.html"
                else:
                    msg = "There not difference in the files!"
            else: # if none of the step match its the chatGPT buttom
                msg = "openai.error.RateLimitError: You exceeded your current quota, please check your plan and billing details."
                # Use the hidden input value of id from the form to get the rowid
            id = request.form['id']
            # Connect to the database and SELECT a specific rowid
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT * FROM steps")
            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            # Send the specific record of data to edit.html
            return render_template(vform,rows=rows,msg=msg)
        

@app.route('/diff')
def diff():
    return render_template_string('''
        <form method="post" action="/compare">
            <textarea name="golden" placeholder="Paste Golden Configuration" rows="10" cols="50"></textarea>
            <textarea name="current" placeholder="Paste Current Configuration" rows="10" cols="50"></textarea>
            <input type="submit" value="Compare">
        </form>
    ''')

@app.route('/compare', methods=['POST'])
def perform_comparison():
    golden_config = request.form['golden']
    current_config = request.form['current']

    # Perform comparison
    differences = at.compare_configs(golden_config, current_config)

    return render_template_string('''
        <h2>Differences</h2>
        {% for difference in differences %}
            <p>{{ difference }}</p>
        {% endfor %}
    ''', differences=differences)


if __name__ == "__main__":
    app.run(debug=True)
