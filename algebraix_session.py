"""Define AlgebraixSession object with methods."""

import os
import re

from seleniumrequests import Firefox


class AlgebraixSession(object):
    """Launch an Algebraix session."""

    def __init__(self):
        """Initialise the session by opening the web browser."""
        self.browser = Firefox()
        self.browser.get("https://c1-liceodelvalle.algebraix.com/")
        self.regex = re.compile(r"(.+\.\w{3,4}) \(\d+\.?\d+[KM]\)")

    def set_sender_name(self):
        """Find and sets current message’s sender’s name."""
        self.senderName = self.browser.find_element_by_class_name(
            "material-card__text--primary").text

    def replace_sender_name(self, names):
        """
        Check if parent’s name can be substituted with student’s.

        Inputs: names, a dictionary of various data types.
        """
        for student, v in names.items():
            if self.senderName in v[1]:
                self.senderName = student

    def set_group(self, names):
        """
        Check student’s group if possible.

        Inputs: names, a dictionary of various data types.
        """
        self.group = names.get(self.senderName, [""])[0]

    def set_body_text(self):
        """Find and set current message’s body text."""
        self.bodyText = self.browser.find_element_by_class_name(
            "material-card__body--paragraph." +
            "material-card__body--respect-lines.text-break"
        ).text

    def set_attachments(self):
        """Set a list of attachments for current message."""
        self.attachments = [
            link
            for link in self.browser.find_elements_by_tag_name("a")
            if self.regex.search(link.text)
        ]

    def create_download_directory(self):
        """Create download directory for current sender."""
        self.targetPath = os.path.expanduser(
            os.path.join(
                "~", "Downloads", "AlgebraixInbox",
                f"{self.group}{self.senderName.replace(' ', '')}"
            )
        )
        os.makedirs(self.targetPath, exist_ok=True)

    def download_files(self):
        """Download and save current body text and attachments."""
        n = 1
        while os.path.isfile(os.path.join(self.targetPath, f"{n:02}.txt")):
            n += 1

        file = open(os.path.join(self.targetPath, f"{n:02}.txt"), "w")
        file.write(self.bodyText)
        file.close()

        for link in self.attachments:
            res = self.browser.request("GET", link.get_attribute("href"))
            res.raise_for_status()
            file = open(os.path.join(
                self.targetPath,
                f"{n:02}_{self.regex.search(link.text).group(1)}"), "wb")
            for chunk in res.iter_content(10000):
                file.write(chunk)
            file.close()

    def find_next(self):
        """
        Find and returns the link to the next message.

        Returns False if it is the last message.

        Returns: a Selenium object or a bool.
        """
        links = self.browser.find_elements_by_class_name("X_LOAD.action-item")
        for link in links:
            if link.get_attribute("data-original-title") == "Next":
                return link
        return False

    def browser_close(self):
        """Close the web browser."""
        self.browser.close()