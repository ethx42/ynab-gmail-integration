from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import os

load_dotenv()


def setup_langchain():
    llm = ChatOpenAI(openai_api_key = os.getenv('OPENAI_API_KEY'), model="gpt-3.5-turbo-0613")
    output_parser = JsonOutputParser()
    return llm, output_parser


system_prompt = """
As an advanced AI assistant, your expertise lies in interpreting and structuring banking notification messages from Bancolombia. Your mission is to meticulously convert bilingual (English and Spanish) notifications into well-organized, structured information presented in JSON format. This involves extracting and classifying critical information from each transaction accurately. Specifically, your output should maintain a standard format with the following keys:

- "type": Identify if the transaction signifies 'income' (money received) or 'expense' (money spent).
- "amount": State the full monetary value of the transaction, presented as a whole number or a floating-point number without any currency symbols, using a period (.) to denote any decimals.
- "payee": Determine the counterparty in the transaction, excluding the account holder or the originating account.
- "memo": Combine and record the transaction's time, payee, and purpose or description. Format this information as 'time - payee - memo'.
- "date": Log the transaction date in the format YYYY-MM-DD.
- "time": Note the precise time the transaction was executed.
- "product": Ascertain the source account or financial product initiating the transaction. When encountering 'cuenta AHORROS' or 'T.Deb *2551', interpret and report them as 'cta *1560'. This standardization is crucial for consistent analysis and reporting.
Ensure your response uses the specified structure: 'type', 'amount', 'payee', 'memo', 'date', 'time', 'product'. If any data is missing or not pertinent, assign 'null' for those specific fields.

Important Notation in Example Notifications:

The sample messages use symbols to highlight transaction details: origin product by vertical bars (| |), transaction memo by parentheses (), and payee by angle brackets < >. Note, these symbols are not present in actual banking notifications; they serve purely for training purposes. Your task is to deduce the necessary details from the content and context of each message.

Learning Example Notifications:

These examples are intended only for training; actual notifications do not include the illustrative symbols.

"Bancolombia informs you of a (Purchase for $44500 <at GENNY>) at 18:54 on 17/02/2024 |T.Cred *2075|. Concerns to 6045109095/018000931987."
"Bancolombia informs you of a (Transfer for $16000) from |account *1560| (to <account 0000003116271600>) at 13:55 on 15/02/2024. Concerns to 6045109095/018000931987."
"Bancolombia le informa (recepcion de pago de <ACME INC>) por $14197000 en su |cuenta AHORROS| a las 10:24 del 22/02/2024. Dudas al 018000931987."
"Bancolombia le informa (Pago de Tarjeta de Credito) por $138737 |desde cta *1560| a la <tarjeta *2075> a las 20:11 del 04/03/2024. Inquietudes al 6045109095/018000931987."
"Bancolombia le informa de una compra por $44900 en (APPLE.COM/BILL) a las 04:45 del 12/02/2024 (compra afiliada) a |T.Cred *2075|. Inquietudes al 6045109095/01800931987."
"Bancolombia le informa (Retiro por $230000 en <UNICENTRO_1>) a las 10:11 del 06/02/2024 |T.Deb *2551|. Inquietudes al 6045109095/018000931987."
"Bancolombia le informa (Pago de Tarjeta de Credito) por $3000 |desde cta *1560| a la <tarjeta *3099> a las 20:11 del 04/03/2024. Inquietudes al 6045109095/018000931987."

Apply these examples to perfect your method. Your ultimate objective is to extract and detail the subject, type, value, and originating product from real banking notifications, applying the knowledge obtained from these instructional messages.
"""


def analyze_emails(emails, llm, output_parser):
    analyzed_emails = []

    for email in emails:
        print(f"Analyzing email from {email['sender']} with subject '{email['subject']}':")

        specific_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", email['snippet'])
        ])
        specific_chain = specific_prompt | llm | output_parser
        print(email)

        try:
            extracted_info = specific_chain.invoke({})

            if extracted_info:
                print("Processed response:")
                extracted_info['id'] = email['id']
                analyzed_emails.append(extracted_info)

        except Exception as e:
            print(f"Error trying to analyze email: {e}")
        
        print("Analysis completed.\n")

    return analyzed_emails
