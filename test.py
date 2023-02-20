import csv
import json
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc

# Set up the Selenium webdriver
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
options.headless = False

driver = uc.Chrome(options=options)


# Function to extract the XXX value from the ads.txt file for a domain using Selenium
def extract_value(domain):
    try:
        # Load the ads.txt page for the domain in the browser
        driver.get(f"https://{domain}/ads.txt")

        # Wait for the page to load and find the element that contains the text of the page
        wait = WebDriverWait(driver, 8)
        element = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "pre")))

        # Extract the text of the page and convert to lowercase
        response_text = element.text.lower()

        # Split the text into lines and look for the relevant line with the XXX value
        lines = response_text.split("\n")
        xxx_list = []
        for line in lines:
            if "truvid.com," in line and "direct" in line:
                line = line.replace(" ", "")
                if "#" in line:
                    line = line[:line.index("#")]
                try:
                    truvid, xxx, direct = line.split(",")
                    xxx_list.append(xxx)
                except ValueError:
                    return "Err"
        if len(xxx_list) == 0:
            return "Missing"
        elif len(xxx_list) == 1:
            return xxx_list[0]
        else:
            return xxx_list
    except:
        # If there is any other exception, check if it's a 404 error and return "NA"
        status_code = requests.get(f"https://{domain}/ads.txt").status_code
        if status_code == 404:
            return "NA"
        else:
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
recipients = ["ron@truvid.com"]
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
