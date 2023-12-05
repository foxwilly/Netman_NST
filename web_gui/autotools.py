#!usr/bien/env python3
import subprocess
import sqlite3
import openai
import os
import diffios

#sudo docker exec -it clab-bgp-R5 Cli -c "ping 192.168.12.2"
#result = subprocess.check_output(['sudo', 'docker', 'exec', '-it', 'clab-bgp-R5', 'Cli', '-c','ping '+ip])

def isreachable(ip):
    try:
        output = subprocess.check_output(['sudo', 'docker', 'exec', '-it', 'clab-bgp-R4', 'Cli', '-c','ping '+ip])
        if  "Network is unreachable" in output.decode():
            return False, output.decode()
        return True, output.decode()
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()


def inspector():
    sts="FAIL"
    try:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            is_connected, ping_output = isreachable('192.168.12.1')
            if is_connected:
                sts="PASS"
            cur.execute("UPDATE steps SET status='"+sts+"' WHERE step='1'")
            #cur.execute("UPDATE students SET name='"+nm+"', addr='"+addr+"', city='"+city+"', zip='"+zip+"' WHERE rowid="+rowid)
            con.commit()
        print(ping_output)
#            msg = "Record successfully edited in the database"
    except:
        con.rollback()
        print("Exception in the DB connection")
        #msg = "Error in the Edit: UPDATE routers SET hostname="+host+", type="+type+", file="+file+", interface="+inter+", ip="+ip+", protocol="+proto+" WHERE rowid="+rowid

    finally:
        con.close()
        return "The new status is: "+sts
 #       print("Error in the DB connection")
            # Send the transaction message to result.html
        #return render_template('result.html',msg=msg)


def myopenai():
    api_key = os.getenv("OPENAI_API_KEY")  # Get your API key from environment variable

    openai.api_key = api_key

    prompt_text = "Once upon a time"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_text}
        ],
        temperature=0.5,
        max_tokens=50
    )

    if response and response.choices:
        generated_text = response.choices[0].message['content'].strip()
        print("Generated text:", generated_text)
    else:
        print("Failed to generate text.")


# Function to compare configs
# Return False if files are the same, other wise True
def compare_configs(golden_config, current_config):
    files_path="/home/willy/Netman_NST/web_gui/golden_config/"
    f1=files_path+golden_config
    f2=files_path+current_config
    f3=files_path+"ignore.txt"
    diff = diffios.Compare(f1,f2,f3)
    diff_result = diff.delta()
     # Check if there are differences
    if len(diff_result)>31:
        return diff_result, True  # Differences exist
    else:
        return diff_result, False  # No differences found



if __name__ == '__main__':
    #is_connected, ping_output = isreachable('192.168.12.2')
    #print(is_connected)
    #print(ping_output)
    #print(inspector())
    result, isdiff = compare_configs("test_2023-10-03_21-20-25.cfg","test_2023-10-03_21-20-26.cfg")
    print(result)
    print(isdiff)