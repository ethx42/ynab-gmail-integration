from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import base64
import json
import os


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def get_gmail_service():
    creds = None
    token_info = os.getenv('GOOGLE_TOKEN')
    if token_info:
        token_binary = base64.b64decode(token_info.encode('utf-8'))
        creds = pickle.loads(token_binary)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_info = os.getenv('GOOGLE_CREDENTIALS')
            if credentials_info:
                credentials_dict = json.loads(credentials_info)
                flow = InstalledAppFlow.from_client_config(credentials_dict, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                raise ValueError("No se encontraron las credenciales de Google.")
    
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def fetch_emails(service):
    query = "from:alertasynotificaciones@notificacionesbancolombia.com subject:\"Alertas y Notificaciones\" is:unread"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    emails = []
    if not messages:
        print('No emails found.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            sender = next(header['value'] for header in headers if header['name'] == 'From')
            snippet = msg['snippet']
            message_id = message['id']
            email_data = {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'snippet': snippet
            }
            emails.append(email_data)
        print(f'{len(emails)} emails found and ready for analysis.')
    return emails


def mark_email_as_read(service, user_id, message_id):
    try:
        service.users().messages().modify(userId=user_id, id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
        print(f"Email with ID: {message_id} has been marked as read.")
    except Exception as e:
        print(f"An error occurred: {e}")


def add_label_to_email(service, user_id, message_id, label_id):
    try:
        service.users().messages().modify(userId=user_id, id=message_id, body={'addLabelIds': [label_id]}).execute()
        print(f"Label added to email with ID: {message_id}.")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_label(service, user_id, label_name):
    existing_labels = service.users().labels().list(userId=user_id).execute().get('labels', [])
    
    for label in existing_labels:
        if label['name'].lower() == label_name.lower():
            return label
        
    label_body = {'name': label_name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    created_label = service.users().labels().create(userId=user_id, body=label_body).execute()

    return created_label
