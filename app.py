import subprocess
import smtplib
import os
from email.message import EmailMessage

from parser.report import Report


OUTPUT_IN_MARKDOWN = os.environ['OUTPUT_IN_MARKDOWN'].lower() == "true"
EMAIL_RECIPIENT = os.environ['EMAIL_RECIPIENT']
INPUT_FILENAME = "linkchecker-out.xml"
OUTPUT_FILENAME = "404.md" if OUTPUT_IN_MARKDOWN else "404.txt"
ATTACHMENT_FILENAME = "report.md" if OUTPUT_IN_MARKDOWN else "report.txt"
ATTACHMENT_MIME_SUBTYPE = "markdown" if OUTPUT_IN_MARKDOWN else "plain"
SITE_URL = os.environ['SITE_URL']


subprocess.run(["linkchecker", "--check-extern", "--user-agent", "Mozilla/5.0 (compatible; LinkChecker/9.3; +http://wummel.github.io/linkchecker/)", "-F", "xml", "-q", SITE_URL], check=False)

print("BROKEN LINKS REPORT: \n")
report = Report(INPUT_FILENAME)
results = report.results
for url, name, parent_url, result in results:
    print(f"URL: {url}\nName: {name}\nParent URL: {parent_url}\nResult: {result}\n")
print(f"Processed: {len(results)}")
report.to_file(OUTPUT_FILENAME)

msg = EmailMessage()
msg["From"] = "noreply@csc.fi"
msg["Subject"] = f"Broken links report for {report.month}"
msg["To"] = os.getenv('EMAIL_RECIPIENT')
msg.set_content(f"You will find attached the broken links report of {SITE_URL} for {report.month}.")
msg.add_attachment(open(OUTPUT_FILENAME, "r", encoding="utf-8").read(),
                   subtype=ATTACHMENT_MIME_SUBTYPE,
                   filename=ATTACHMENT_FILENAME)

s = smtplib.SMTP('smtp.pouta.csc.fi')
s.send_message(msg)
print("Email sent")
