# # tasks.py
from mail_service import send_email
from celery import shared_task
import flask_excel as excel
from modal import *
# from flask_mail import Message
# from app import create_app, celery

# app = create_app()
# def send_email(recipient, subject, message):
#     msg = Message(subject, recipients=[recipient], body=message)
#     mail.send(msg)

# def send_chat_message(chat_webhook_url, message):
#     import requests
#     data = {"text": message}
#     requests.post(chat_webhook_url, json=data)

# def generate_csv_file(campaigns):
#     import csv
#     import os
#     file_path = os.path.join('/path/to/save', 'campaigns.csv')
#     with open(file_path, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["Description", "Start Date", "End Date", "Budget", "Visibility", "Goals"])
#         for campaign in campaigns:
#             writer.writerow([campaign.description, campaign.start_date, campaign.end_date, campaign.budget, campaign.visibility, campaign.goals])
#     return file_path

# @shared_task
# def send_daily_reminder():
#     with app.app_context():
#         # Fetch influencers with pending ad requests
#         influencers = get_influencers_with_pending_requests()
        
#         for influencer in influencers:
#             # Prepare the reminder message
#             message = f"Dear {influencer.name}, you have pending ad requests. Please visit the platform to review them."
            
#             # Send the reminder via Google Chat Webhooks, SMS, or email
#             if influencer.preferred_contact_method == 'chat':
#                 send_chat_message(influencer.chat_webhook_url, message)
#             elif influencer.preferred_contact_method == 'sms':
#                 send_sms(influencer.phone_number, message)
#             elif influencer.preferred_contact_method == 'email':
#                 send_email(influencer.email, "Ad Request Reminder", message)

# @shared_task
# def send_monthly_activity_report():
#     with app.app_context():
#         sponsors = get_all_sponsors()
        
#         for sponsor in sponsors:
#             # Generate the monthly activity report
#             report = generate_monthly_report(sponsor)
            
#             # Send the report via email
#             send_email(sponsor.email, "Monthly Activity Report", report)


# @shared_task
# def export_campaigns_to_csv(sponsor_id):
#     with app.app_context():
#         sponsor = get_sponsor_by_id(sponsor_id)
#         campaigns = get_campaigns_by_sponsor(sponsor_id)
        
#         # Generate CSV file
#         csv_file_path = generate_csv_file(campaigns)
        
#         # Notify the sponsor via email
#         message = f"Dear {sponsor.name}, your campaign details export is ready. You can download it from {csv_file_path}."
#         send_email(sponsor.email, "Campaign Details Export", message)


@shared_task(ignore_result=False)
def create_camp_csv():
    camp_res = Campaign.query.with_entities(Campaign.description,Campaign.start_date,
                                            Campaign.end_date,Campaign.budget,Campaign.visibility
                                            ,Campaign.goals).all()
    csv_output = excel.make_response_from_query_sets(query_sets=camp_res,column_names=["description","start_date","end_date","budget","visibility","goals"],file_type="csv")
    filename="campaign.csv"
    with open(filename,'wb') as f:
        f.write(csv_output.data)
    return filename


@shared_task(ignore_result=True)
def send_daily_rem(to, subject, name):
    # Prepare the HTML email body
    text = f"""
    <html>
        <body>
            <p>Hi {name},</p>
            <p>Just a friendly reminder to check your ad requests.</p>
            <p>Please review and accept any pending requests or check out the public ad requests.</p>
            <p>Thank you!</p>
        </body>
    </html>
    """
    
    # Send the email
    send_email(to, subject, text)
    
    return "OK! Email SENT!"

@shared_task(ignore_result=True)
def generate_monthly_report():
    # Get the current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Fetch sponsors
    sponsors = Sponsor.query.all()

    for sponsor in sponsors:
        # Fetch campaigns for the sponsor in the current month
        campaigns = Campaign.query.filter(
            Campaign.sponsor_id == sponsor.id,
            Campaign.year == current_year,
            Campaign.month == current_month
        ).all()
        
        # Aggregate data for the sponsor
        total_ads = sum(len(c.ads) for c in campaigns)  # Assuming `ads` is a relationship in `Campaign`
        sales_growth = sum(c.sales_growth for c in campaigns) if campaigns else 0  # Example field
        budget_used = sum(c.budget_used for c in campaigns) if campaigns else 0  # Example field
        budget_remaining = sponsor.budget - budget_used  # Assuming sponsor's budget is not used up

        # Create HTML report
        report_html = f"""
        <html>
            <body>
                <h1>Monthly Activity Report - {current_month}/{current_year}</h1>
                <p><strong>Company:</strong> {sponsor.company_name}</p>
                <p><strong>Total Advertisements Done:</strong> {total_ads}</p>
                <p><strong>Growth in Sales:</strong> ${sales_growth}</p>
                <p><strong>Budget Used:</strong> ${budget_used}</p>
                <p><strong>Budget Remaining:</strong> ${budget_remaining}</p>
                <p>Thank you for your continued support!</p>
            </body>
        </html>
        """

        # Send the report via email
        send_email(sponsor.email, f"Monthly Activity Report - {current_month}/{current_year}", report_html)
    
    return "Monthly Report Sent"


# @shared_task(ignore_result=True)
# def send_daily_rem(to,subject):
#     influ=Influencer.query.filter_by(email=to).first()
#     name=influ.name
#     text="""
#         Hi """+name+""",\n\n
#         Just a friendly reminder to check your ad requests.
#         Please review and accept any pending requests or check out the public ad requests.\n\n
#         Thank you!
#     """
#     send_email(to,subject,text)
#     return "Email Sent to Influencer!!"