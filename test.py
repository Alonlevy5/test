import csv
import json
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders

# Function to extract the XXX value from the ads.txt file for a domain


def extract_value(domain):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(
            f"https://www.{domain}/ads.txt", headers=headers)
        if response.status_code == 404:
            return "NA"
        response_text = response.text.lower()
        lines = response_text.split("\n")
        xxx_list = []
        for line in lines:
            if "truvid.com," in line and "direct" in line:
                line = line.replace(" ", "")
                if "#" in line:
                    line = line[:line.index("#")]
                truvid, xxx, direct = line.split(",")
                xxx_list.append(xxx)
        if len(xxx_list) == 0:
            return "Missing"
        elif len(xxx_list) == 1:
            return xxx_list[0]
        else:
            return xxx_list
    except requests.exceptions.RequestException:
        return "Err"


# Define the list of domains
domains = ["unotv.com", "cnn.com", "aseannow.com", "calcalist.co.il", "rionegro.com.ar",
           "inf.news", "gametimeprime.com", "full-novel.com", "shichengbbs.com", "fastnovels.net"]

# Initialize the data list
data = []

# Loop through the domains and extract the XXX value for each domain
for domain in domains:
    xxx = extract_value(domain)
    data.append({"Domain": domain, "XXX": xxx})

# Save the data to a JSON file
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)

# Save the data to a CSV file
with open("data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Domain", "XXX"])
    writer.writeheader()
    writer.writerows(data)

# Send the data files as email attachments

sender = "truvidtest123@gmail.com"
password = "rgstecazspugyszi"
recipients = ["Ron@truvid.com"]
subject = "Values for Domains"
body = "Please find the attached files containing the values for the specified domains."
files = ["data.json", "data.csv"]

msg = MIMEMultipart()
msg["From"] = sender
msg["To"] = COMMASPACE.join(recipients)
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

for file in files:
    with open(file, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={file}")
        msg.attach(part)

smtp_server = "smtp.gmail.com"
smtp_port = 587
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(sender, password)
server.sendmail(sender, recipients, msg.as_string())
server.quit()
