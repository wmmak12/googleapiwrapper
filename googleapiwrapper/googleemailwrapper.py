from __future__ import print_function
from googleapiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename
import base64
from google.oauth2 import service_account


class GoogleEmail:
    def __init__(self, serviceAccountFile, emailFrom: str, serviceAccountType="path"):
        """
        Instantiate the service account
        Parameters:
            serviceAccountFile: Either the path to the json file or its a json object
            emailFrom: the email alias which you want it to be from
            serviceAccountType: the default is the path to the json file, if not specify it as 'json'
            if it is an object
        Returns:
            An object of the service: Authorized Gmail API service instance.
        """
        self.serviceAccountFile = serviceAccountFile
        self.emailFrom = emailFrom
        self.serviceAccountType = serviceAccountType
        self.service = self.__service_account_login(
            self.serviceAccountFile, self.emailFrom, self.serviceAccountType
        )

    def __service_account_login(
        self, serviceAccountFile, emailFrom, serviceAccountType
    ):
        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        if serviceAccountType == "path":
            credentials = service_account.Credentials.from_service_account_file(
                serviceAccountFile, scopes=SCOPES
            )
        elif serviceAccountType == "json":
            credentials = service_account.Credentials.from_service_account_info(
                serviceAccountFile, scopes=SCOPES
            )

        delegated_credentials = credentials.with_subject(emailFrom)

        service = build("gmail", "v1", credentials=delegated_credentials)

        return service

    def create_message(self, to, subject, message_text, attachment_list=False):
        """
        Create a message for an email.
        Paremeters:
            to: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.
            attachment_list: attachment file if any. (optional)
        Returns:
            An object containing a base64url encoded email object.
        """

        message = MIMEMultipart()
        message.attach(MIMEText(message_text))
        message["from"] = self.emailFrom
        message["to"] = to
        message["subject"] = subject

        if attachment_list:
            for f in attachment_list:
                with open(f, "rb") as fil:
                    message.attach(
                        MIMEApplication(
                            fil.read(),
                            Content_Disposition=f"attachment; filename='{basename(f)}'",
                            Name=basename(f),
                        )
                    )

        self.encode_message = {
            "raw": base64.urlsafe_b64encode(message.as_string().encode("UTF-8")).decode(
                "ascii"
            )
        }

        return self.encode_message

    def send_message(self, user_id="me"):
        """
        Send an email message.
        Parameters:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message: Message to be sent.
        Returns:
            Sent Message.
        """

        try:
            message = (
                self.service.users()
                .messages()
                .send(userId=user_id, body=self.encode_message)
                .execute()
            )
            print("Message Id: %s" % message["id"])
            return message
        except errors.HttpError as error:
            print("An error occurred: %s" % error)
