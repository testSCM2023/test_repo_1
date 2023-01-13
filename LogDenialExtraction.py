import os
import re
import pandas as pd
import csv
#please add your log file location
path = r"C:\mandy\task\LicenseManger\TaskingLM\nlnhsrk-ap108"

def cut_text(text,lenth):
 textArr = re.findall('.{'+str(lenth)+'}', text)
 textArr.append(text[(len(textArr)*lenth):])
 return textArr

reason_a = []
reason_a.append("license count exceeded")
reason_a.append("denied due to access list")
reason_a.append("refused by this server")

csv_list = []

##If we can find the reason in third line
def two_line(l1,l2):
    csv = []
    time = "'" + cut_text(l1,20)[0]
  
    if not re.search(r"Connect from ", l1):
        return csv
    ip_user_host = l1.split("Connect from ")[1]
    ip = ip_user_host.split("(")[0].strip()
    username = ip_user_host.split("(")[1].split("/")[0]
    if not re.search(r"/", ip_user_host.split("(")[1]):
        hostname = ""
    else:
        hostname = ip_user_host.split("(")[1].split("/")[1].split(")")[0]
    if re.search(r"key ", l1):
        feature = l1.split("key ")[1].split(" - ")[1]
    else:
        feature = ""
    if re.search(r"key ", l1):
        license = l1.split("key ")[1].split("- ")[0]
    elif re.search(r"key ", l2):
        license = l2.split("key ")[1].split(", ")[0]

    else:
        license = ""
    csv.append(time.strip())
    csv.append(ip.strip())
    csv.append(username.strip())
    csv.append(hostname.strip())
    csv.append(feature.strip())
    csv.append(license.strip())
    csv.append(reason(l2))
    return csv
#If we can find the denail reason in third line
def three_line(l1,l2,l3):
    csv = []
    time = "'" + cut_text(l1,20)[0]
    l1_check = re.search(r"Connect from ", l1)
    if not l1_check:
        l1 = l2
        l2 = l3
        return two_line(l1,l2)
    ip_user_host = l1.split("Connect from ")[1]
    ip = ip_user_host.split("(")[0].strip()
    username = ip_user_host.split("(")[1].split("/")[0]
    if not re.search(r"/", ip_user_host.split("(")[1]):
        hostname = ""
    else:
        hostname = ip_user_host.split("(")[1].split("/")[1].split(")")[0]
  
    l2_check = re.search(r"changed to ", l2)
    if l2_check:
        license = l2.split("changed to ")[1].split("due to")[0]
    else:
        if re.search(r"key ", l3):
            license = l3.split("key ")[1].split(", ")[0]
        else:
            license = ""
    if re.search(r"key ", l1):
        feature = l1.split("key ")[1].split(" - ")[1]
    else:
        feature = ""
    csv.append(time.strip())
    csv.append(ip.strip())
    csv.append(username.strip())
    csv.append(hostname.strip())
    csv.append(feature.strip())
    csv.append(license.strip())
    csv.append(reason(l3))
    return csv

def reason(line):
    for reason1 in reason_a:
        matchObj1 = re.search(reason1, line)
        if matchObj1:
            return reason1

for root, dirs, files in os.walk(path):
    for fn in files:
        if fn.endswith(".log"):
            fh = os.path.join(root,fn)
            print("filename:", fh)
            with open(fh, 'r', encoding='utf-8') as fileObj:
                r1 = ""
                r2 = ""
                r3 = ""
                lines = fileObj.readlines()
                for aline in lines:
                    if r1 == "":
                        r1 = aline
                        continue
                    if r2 == "":
                        r2 = aline
                        continue
                    r3 = aline
                    matchObj2 = re.search('license count exceeded|denied due to access list|refused by this server', r2)
                    matchObj3 = re.search('license count exceeded|denied due to access list|refused by this server', r3)
                    if None != matchObj3 or None != matchObj2:
                        if matchObj3:
                            csv_line = three_line(r1,r2,r3)
                            r1 = ""
                            r2 = ""
                            r3 = ""
                        else:
                            csv_line = two_line(r1,r2)
                            r1 = r3
                            r2 = ""
                            r3 = ""
                        if len(csv_line):
                            csv_list.append(csv_line)
                    else:
                        r1 = r2
                        r2 = r3

#define the output CSV file name
with open('outputtest.csv', 'w', encoding='utf-8', newline='') as file_obj:
    writer = csv.writer(file_obj)
    header = []
    header.append("time")
    header.append("ip")
    header.append("username")
    header.append("hostname")
    header.append("feature")
    header.append("license")
    header.append("reason")

#Print message once the log data exceeds the max lines of CSV
    writer.writerow(header)
    number = 0
    for p in csv_list:
        number = number + 1
        if number >65534:
            csv_line = []
            csv_line.append("Exceed the max lines of CSV file")
            csv_line.append("")
            csv_line.append("")
            csv_line.append("")
            csv_line.append("")
            csv_line.append("")
            csv_line.append("")
            csv_list.append(csv_line)
            writer.writerow(csv_line)
            break
        writer.writerow(p)

#below are used to remove the duplicate records (duplicate means all the fields are keep the same value)
frame = pd.read_csv('C:\mandy\pytest\outputtest.csv', engine='python')
data = frame.drop_duplicates(keep = "first")
data.to_csv ('C:\mandy\pytest\outputtest.csv', encoding= 'utf-8', index=False)