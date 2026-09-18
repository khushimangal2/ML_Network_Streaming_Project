
import subprocess
import csv
import os
from datetime import datetime

def get_ping_data():
    result=subprocess.run(["ping","-c","4","google.com"],capture_output=True,text=True)
    output=result.stdout
    print(output)
    return output
def save_ping_data(output):
    data_folder="../data"
    os.makedirs(data_folder,exist_ok=True)
    file_path=os.path.join(data_folder,"network_data.csv")
    timestamp=datetime.now().strftime("%Y-%m-%d%H:%M:%S")
    with open(file_path,"a",newline="")as file:
         writer=csv.writer(file)
         if file.tell()==0:
            writer.writerow(["timestamp","ping_output"])
            writer.writerow([timestamp,output])
    print("\nData saved successfully!")
    print("saved to:",file_path)
ping_output=get_ping_data()
save_ping_data(ping_output)
