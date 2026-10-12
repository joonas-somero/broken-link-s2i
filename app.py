import subprocess
import smtplib
import os
from email.message import EmailMessage

from parser.report import Report


SITE_URL = os.getenv("SITE_URL")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
EMAIL_SMTP = os.getenv("EMAIL_SMTP")
REPORT_IN_MARKDOWN = os.getenv("REPORT_IN_MARKDOWN", "true").lower() == "true"

OUTPUT_FILENAME = "linkchecker-out.xml"
REPORT_FILENAME = "404.md" if REPORT_IN_MARKDOWN else "404.txt"
ATTACHMENT_FILENAME = "report.md" if REPORT_IN_MARKDOWN else "report.txt"
ATTACHMENT_MIME_SUBTYPE = "markdown" if REPORT_IN_MARKDOWN else "plain"
USER_AGENT = "Mozilla/5.0 (compatible; LinkChecker/9.3; +http://wummel.github.io/linkchecker/)"


def run_checker():
    options = ["--user-agent", USER_AGENT,
               "--file-output", "xml",
               "--check-extern",
               "--quiet"]

    subprocess.run(["linkchecker", *options, SITE_URL], check=False)


def print_report(report: Report):
    results = report.results
    print("BROKEN LINKS REPORT: \n")
    for url, name, parent_url, result in results:
        print(f"URL: {url}\nName: {name}\nParent URL: {parent_url}\nResult: {result}\n")
    print(f"Processed: {len(results)}")


def email_report(report: Report):
    msg = EmailMessage()

    msg["From"] = EMAIL_SENDER
    msg["Subject"] = f"Broken links report for {report.month}"
    msg["To"] = EMAIL_RECIPIENT
    msg.set_content(
        f"You will find attached the broken links report of {SITE_URL} for {report.month}."
    )

    with open(REPORT_FILENAME, "r", encoding="utf-8") as file_attachment:
        msg.add_attachment(file_attachment.read(), subtype=ATTACHMENT_MIME_SUBTYPE,
                                                   filename=ATTACHMENT_FILENAME)

    s = smtplib.SMTP(EMAIL_SMTP)
    s.send_message(msg)
    print("Email sent")


def main():
    if SITE_URL is not None:
        run_checker()

        report = Report(OUTPUT_FILENAME)

        print_report(report)
        report.to_file(REPORT_FILENAME)

        if all(value is not None for value in (EMAIL_SENDER,
                                               EMAIL_RECIPIENT,
                                               EMAIL_SMTP)):
            email_report(report)
        else:
            print("Email not sent: incomplete environment")
    else:
        print("No SITE_URL to check.")


if __name__ == "__main__":
    main()
