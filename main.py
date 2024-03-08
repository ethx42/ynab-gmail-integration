from app.gmail_tools import get_gmail_service, fetch_emails, mark_email_as_read, create_label, add_label_to_email
from app.langchain_tools import setup_langchain, analyze_emails

if __name__ == '__main__':
    gmail_service = get_gmail_service()
    llm, output_parser = setup_langchain()
    emails = fetch_emails(gmail_service)
    analyzed_emails = analyze_emails(emails, llm, output_parser)
    
    label_name = "YNAB ✅"
    label = create_label(gmail_service, 'me', label_name)
    
    print("Datos analizados:")
    print(len(analyzed_emails))
    for email in analyzed_emails:
        print(email)
        mark_email_as_read(gmail_service, 'me', email['id'])
        add_label_to_email(gmail_service, 'me', email['id'], label['id'])