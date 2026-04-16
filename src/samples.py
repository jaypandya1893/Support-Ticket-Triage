"""
Hardcoded sample tickets covering the five categories and a range of urgencies/sentiments.
Used in the UI dropdown so evaluators can test without typing.
"""

SAMPLE_TICKETS = {
    "billing_refund": {
        "label": "Billing — Refund Request",
        "text": (
            "Hi, I was charged twice for my subscription this month. "
            "I see two identical charges of $299 on my credit card statement on March 1st. "
            "I need one of them refunded immediately. This is unacceptable — I've been a customer "
            "for two years and this is the third billing error I've experienced. "
            "Please escalate this to your billing team."
        ),
    },
    "bug_report_critical": {
        "label": "Bug Report — Data Not Loading (Critical)",
        "text": (
            "URGENT — Our entire team has been locked out of the dashboard since 9 AM this morning. "
            "We're getting a 500 error on every page load. This is a production issue affecting "
            "all 45 users in our organization. We have a client presentation in 3 hours and we "
            "cannot access any of our reports. If this isn't fixed in the next hour, we will have "
            "no choice but to evaluate other vendors."
        ),
    },
    "feature_request": {
        "label": "Feature Request — CSV Export",
        "text": (
            "Hi team, love the product overall. One thing that would make our workflow much easier "
            "is the ability to export any data table to CSV directly from the UI. Right now we have "
            "to use the API and write custom scripts which takes extra engineering time. "
            "Is this on your roadmap? A lot of our colleagues at other companies have also asked "
            "for this. Happy to jump on a call to share the use case in more detail."
        ),
    },
    "account_issue": {
        "label": "Account Issue — SSO Login Broken",
        "text": (
            "Our SSO login stopped working this afternoon for new users. "
            "Existing users can still log in fine, but anyone trying to create an account "
            "through our Okta integration gets redirected to an error page saying "
            "'Identity provider not configured'. We haven't changed anything on our end. "
            "This is blocking our onboarding of 12 new team members this week."
        ),
    },
    "gdpr_request": {
        "label": "Account Issue — GDPR Data Deletion",
        "text": (
            "I am writing to formally request the deletion of all personal data you hold "
            "about me under Article 17 of the GDPR (Right to Erasure). "
            "My account email is jsmith@example.com. I closed my account 30 days ago "
            "but I have not received confirmation that my data has been deleted. "
            "Please confirm in writing within 72 hours or I will be filing a complaint "
            "with the ICO."
        ),
    },
    "ambiguous_other": {
        "label": "Ambiguous — Unclear Request",
        "text": (
            "Hi, I wanted to reach out about something I noticed in the system. "
            "It might be a bug or maybe I'm doing something wrong, not sure. "
            "When I click the thing in the top right area, sometimes it works and "
            "sometimes it doesn't. It's been happening for a few days. Let me know. Thanks."
        ),
    },
}
