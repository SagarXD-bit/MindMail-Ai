"""Realistic demo email data covering all categories and urgency levels.

Each entry is a dict matching the fields needed to create an Email + AIClassification.
This data is clearly flagged as demo (is_demo=True) so users can distinguish it.
"""

from datetime import datetime, timedelta
import random

# Fixed seed for reproducibility within a sync
random.seed(42)

NOW = datetime.utcnow()


def _ts(days_ago: int, hour: int = 9, minute: int = 0) -> datetime:
    """Generate a timestamp N days ago at a given hour."""
    return NOW - timedelta(days=days_ago, hours=0) + timedelta(
        hours=random.randint(0, 3))


DEMO_EMAILS = [
    # ---- CRITICAL ----
    {
        "sender_email": "security@payments-gateway.com",
        "sender_name": "Security Team",
        "subject": "URGENT: Failed payment transactions need immediate attention",
        "body_text": (
            "Hi,\n\n"
            "We've detected 3 failed payment transactions on your account in the last hour. "
            "This may indicate a configuration error or potential fraud. "
            "Please log in to your dashboard immediately to review and resolve these issues. "
            "Failure to act within 24 hours may result in service suspension.\n\n"
            "Transaction IDs: TXN-4892, TXN-4893, TXN-4894\n\n"
            "Please contact support urgently if you need assistance.\n\n"
            "Security Team\nPayments Gateway Inc."
        ),
        "category": "Finance",
        "urgency": "critical",
        "confidence": 0.95,
        "explanation": "Urgent financial alert with failed transactions and 24-hour deadline.",
        "needs_response": True,
        "suggested_followup": True,
    },
    {
        "sender_email": "legal@enterprise-corp.com",
        "sender_name": "Legal Department",
        "subject": "ACTION REQUIRED TODAY: Contract renewal deadline",
        "body_text": (
            "Dear Client,\n\n"
            "This is a final notice regarding your enterprise service contract which expires today. "
            "We have not yet received your signed renewal documents. If we do not receive them by 5:00 PM, "
            "your services will be terminated and all data archived per our retention policy.\n\n"
            "Please review and sign the attached contract immediately.\n\n"
            "Regards,\nLegal Department\nEnterprise Corp"
        ),
        "category": "Work",
        "urgency": "critical",
        "confidence": 0.93,
        "explanation": "Contract deadline today with service termination threat.",
        "needs_response": True,
        "suggested_followup": True,
    },

    # ---- HIGH ----
    {
        "sender_email": "sarah.mitchell@techcorp.com",
        "sender_name": "Sarah Mitchell",
        "subject": "Re: Q4 Project Timeline - Need your input by Thursday",
        "body_text": (
            "Hi,\n\n"
            "Following up on the Q4 project timeline we discussed in yesterday's standup. "
            "I need your input on the backend deliverables by this Thursday EOD. "
            "The client demo is scheduled for next Monday, so we're on a tight schedule.\n\n"
            "Can you review the attached timeline and let me know:\n"
            "1. Are the API endpoints feasible by Friday?\n"
            "2. Do we need additional resources?\n\n"
            "Thanks,\nSarah"
        ),
        "category": "Work",
        "urgency": "high",
        "confidence": 0.90,
        "explanation": "Work project with a Thursday deadline and client demo next week.",
        "needs_response": True,
        "suggested_followup": True,
    },
    {
        "sender_email": "interviews@growthstartups.io",
        "sender_name": "Talent Acquisition",
        "subject": "Interview Invitation: Senior Developer Role",
        "body_text": (
            "Dear Candidate,\n\n"
            "Congratulations! We were impressed by your application for the Senior Developer position "
            "and would like to invite you to a technical interview.\n\n"
            "Proposed times:\n"
            "- Tuesday 2:00 PM\n"
            "- Wednesday 10:00 AM\n"
            "- Thursday 3:30 PM\n\n"
            "The interview will be 90 minutes via video call, covering system design and coding. "
            "Please confirm your preferred slot within 48 hours.\n\n"
            "Best regards,\nTalent Acquisition Team\nGrowthStartups"
        ),
        "category": "Application/Recruitment",
        "urgency": "high",
        "confidence": 0.92,
        "explanation": "Interview invitation requiring response within 48 hours.",
        "needs_response": True,
        "suggested_followup": True,
    },
    {
        "sender_email": "mike.chen@clientcorp.com",
        "sender_name": "Mike Chen",
        "subject": "Production Issue - Login system down for some users",
        "body_text": (
            "Hi Support,\n\n"
            "We're experiencing a critical issue with our login system. "
            "Approximately 30% of our users cannot authenticate since the last deployment. "
            "This is impacting our production environment and customers are complaining.\n\n"
            "Error message: 'AUTH_500: Token validation failed'\n"
            "Started: 2 hours ago\n"
            "Affected: ~500 users\n\n"
            "We need urgent help resolving this. Can someone look into this ASAP?\n\n"
            "Mike Chen\nDevOps Lead, ClientCorp"
        ),
        "category": "Customer Support",
        "urgency": "high",
        "confidence": 0.88,
        "explanation": "Critical production issue affecting customers, needs urgent response.",
        "needs_response": True,
        "suggested_followup": True,
    },
    {
        "sender_email": "alerts@cloudservices.com",
        "sender_name": "Cloud Monitoring",
        "subject": "Security Alert: Unusual login attempt detected",
        "body_text": (
            "We detected a login to your account from an unrecognized device.\n\n"
            "Location: Moscow, Russia\n"
            "Time: 3:42 AM UTC\n"
            "IP Address: 185.220.xxx.xxx\n"
            "Device: Unknown (Chrome on Windows)\n\n"
            "If this was you, no action is needed. If not, please:\n"
            "1. Change your password immediately\n"
            "2. Enable two-factor authentication\n"
            "3. Review your recent activity\n\n"
            "This is an automated security alert. Do not reply."
        ),
        "category": "Notification",
        "urgency": "high",
        "confidence": 0.85,
        "explanation": "Security alert about suspicious login requiring attention.",
        "needs_response": False,
        "suggested_followup": False,
    },

    # ---- MEDIUM ----
    {
        "sender_email": "david.kim@partnerfirm.com",
        "sender_name": "David Kim",
        "subject": "Meeting Request: Q1 Partnership Discussion",
        "body_text": (
            "Hi,\n\n"
            "I hope this message finds you well. I'd like to schedule a meeting to discuss "
            "our Q1 partnership opportunities. I think there's great potential for collaboration "
            "on the new product line.\n\n"
            "Would any of these times work for you?\n"
            "- Monday, Jan 15, 2:00 PM\n"
            "- Tuesday, Jan 16, 10:00 AM\n"
            "- Thursday, Jan 18, 3:00 PM\n\n"
            "I'll send a calendar invite once you confirm. Looking forward to it!\n\n"
            "Best,\nDavid Kim\nPartnership Manager\nPartner Firm"
        ),
        "category": "Meeting",
        "urgency": "medium",
        "confidence": 0.86,
        "explanation": "Meeting request for partnership discussion.",
        "needs_response": True,
        "suggested_followup": False,
    },
    {
        "sender_email": "billing@saasplatform.com",
        "sender_name": "Billing Team",
        "subject": "Your January Invoice - $1,249.00",
        "body_text": (
            "Hi,\n\n"
            "Your subscription has been renewed successfully. Here's your invoice for this billing period:\n\n"
            "Plan: Business Pro (Annual)\n"
            "Amount: $1,249.00\n"
            "Billing Period: Jan 1 - Dec 31, 2026\n"
            "Payment Method: Visa ending 4242\n"
            "Status: Paid\n\n"
            "You can download the full invoice from your account dashboard.\n\n"
            "Thank you for your business!\n"
            "Billing Team"
        ),
        "category": "Finance",
        "urgency": "medium",
        "confidence": 0.82,
        "explanation": "Billing invoice notification.",
        "needs_response": False,
        "suggested_followup": False,
    },
    {
        "sender_email": "proposals@vendingsolutions.com",
        "sender_name": "Lisa Anderson",
        "subject": "Proposal: Enterprise Software Solution for Your Team",
        "body_text": (
            "Hi,\n\n"
            "Following our conversation at the conference last month, I've put together a "
            "proposal for an enterprise software solution tailored to your team's needs.\n\n"
            "Key highlights:\n"
            "- Custom workflow automation\n"
            "- Priority 24/7 support\n"
            "- 30% discount for annual commitment\n"
            "- Dedicated implementation specialist\n\n"
            "I'd love to schedule a demo to walk you through the features. "
            "Are you available sometime next week?\n\n"
            "Best regards,\nLisa Anderson\nAccount Executive\nVendingSolutions"
        ),
        "category": "Sales",
        "urgency": "medium",
        "confidence": 0.80,
        "explanation": "Sales proposal following up on a conference conversation.",
        "needs_response": True,
        "suggested_followup": False,
    },
    {
        "sender_email": "jennifer.park@colleagues.com",
        "sender_name": "Jennifer Park",
        "subject": "Re: Action items from last week's review",
        "body_text": (
            "Hi team,\n\n"
            "Thanks for the productive review meeting last week. Here are the action items we agreed on:\n\n"
            "1. @you — Complete the API documentation by Friday\n"
            "2. @mark — Set up the staging environment\n"
            "3. @sarah — Review the design mockups\n\n"
            "Let me know if I missed anything. I'll send a calendar invite for our next check-in.\n\n"
            "Also, don't forget the team lunch on Thursday!\n\n"
            "Jennifer"
        ),
        "category": "Work",
        "urgency": "medium",
        "confidence": 0.84,
        "explanation": "Work follow-up with action items and deadlines.",
        "needs_response": True,
        "suggested_followup": False,
    },

    # ---- LOW ----
    {
        "sender_email": "newsletter@productivityweekly.com",
        "sender_name": "Productivity Weekly",
        "subject": "🚀 This week: 10 tips to boost your productivity",
        "body_text": (
            "Welcome to this week's Productivity Weekly!\n\n"
            "In this issue:\n"
            "- 10 science-backed productivity tips\n"
            "- Tool review: Notion vs. Obsidian\n"
            "- Reader spotlight: How Jane saved 5 hours/week\n\n"
            "Featured Article: The 2-Minute Rule That Changes Everything\n"
            "If a task takes less than two minutes, do it immediately. This simple rule..."
            "\n\n---\n"
            "You're receiving this email because you subscribed to Productivity Weekly.\n"
            "Manage preferences | Unsubscribe"
        ),
        "category": "Newsletter",
        "urgency": "low",
        "confidence": 0.91,
        "explanation": "Weekly newsletter with unsubscribe link.",
        "needs_response": False,
        "suggested_followup": False,
    },
    {
        "sender_email": "team@socialapp.com",
        "sender_name": "SocialApp",
        "subject": "Mark commented on your post",
        "body_text": (
            "Mark commented on your recent post:\n\n"
            "\"Great insights! Have you considered applying this to remote teams?\"\n\n"
            "View and reply to comments in the app.\n\n"
            "---\n"
            "This is an automated notification. Manage your notification settings.\n"
            "© 2026 SocialApp Inc."
        ),
        "category": "Notification",
        "urgency": "low",
        "confidence": 0.87,
        "explanation": "Automated social media notification.",
        "needs_response": False,
        "suggested_followup": False,
    },
    {
        "sender_email": "emily.wilson@friends.com",
        "sender_name": "Emily Wilson",
        "subject": "Dinner this weekend?",
        "body_text": (
            "Hey!\n\n"
            "It's been a while since we caught up. Are you free for dinner this Saturday? "
            "I was thinking that new Italian place downtown — I heard their pasta is amazing!\n\n"
            "Let me know if Saturday works or if another day is better. "
            "No rush, just whenever you have a moment.\n\n"
            "Miss you!\n\n"
            "Em"
        ),
        "category": "Personal",
        "urgency": "low",
        "confidence": 0.78,
        "explanation": "Personal dinner invitation from a friend.",
        "needs_response": True,
        "suggested_followup": False,
    },
    {
        "sender_email": "rewards@biggestwinner-promo.com",
        "sender_name": "Mega Rewards",
        "subject": "CONGRATULATIONS!!! You've been selected as our WINNER 🎉",
        "body_text": (
            "CONGRATULATIONS!!!\n\n"
            "You have been SELECTED as our GRAND PRIZE WINNER of $1,000,000 USD!!!\n\n"
            "To claim your prize, simply click the link below and provide your "
            "banking details for the transfer. Act now — this offer expires in 24 hours!\n\n"
            "CLICK HERE TO CLAIM YOUR $1,000,000 NOW!!!\n\n"
            "Don't miss this once-in-a-lifetime opportunity!\n"
            "Bitcoin and crypto payments also accepted."
        ),
        "category": "Spam",
        "urgency": "low",
        "confidence": 0.97,
        "explanation": "Classic spam: unrealistic prize, urgent language, requests for banking info.",
        "needs_response": False,
        "suggested_followup": False,
    },
    {
        "sender_email": "no-reply@github.com",
        "sender_name": "GitHub",
        "subject": "[mailmind-ai] PR #42 approved and ready to merge",
        "body_text": (
            "Your pull request #42 \"Add analytics dashboard\" has been approved by 2 reviewers.\n\n"
            "Status: Approved ✓\n"
            "Branch: feature/analytics\n"
            "Reviews: 2 approvals, 0 changes requested\n\n"
            "You can now merge this pull request.\n\n"
            "---\n"
            "You're receiving this because you authored this thread.\n"
            "Manage notification settings | Unsubscribe"
        ),
        "category": "Notification",
        "urgency": "low",
        "confidence": 0.85,
        "explanation": "Automated code review notification from GitHub.",
        "needs_response": False,
        "suggested_followup": False,
    },
    {
        "sender_email": "hr@company.com",
        "sender_name": "HR Department",
        "subject": "Reminder: Annual benefits enrollment closes Friday",
        "body_text": (
            "Hi,\n\n"
            "This is a friendly reminder that the annual benefits enrollment period closes this Friday "
            "at 5:00 PM. If you haven't already, please log in to the benefits portal to review and "
            "update your selections for the upcoming year.\n\n"
            "Key changes this year:\n"
            "- New dental plan option\n"
            "- Increased 401(k) match up to 6%\n"
            "- Updated health savings account limits\n\n"
            "If you have questions, drop by HR during office hours.\n\n"
            "HR Department"
        ),
        "category": "Notification",
        "urgency": "medium",
        "confidence": 0.79,
        "explanation": "HR reminder about benefits enrollment deadline.",
        "needs_response": False,
        "suggested_followup": True,
    },
    {
        "sender_email": "conference@techsummit2026.com",
        "sender_name": "Tech Summit 2026",
        "subject": "Your registration is confirmed! See you at Tech Summit",
        "body_text": (
            "Hi,\n\n"
            "Your registration for Tech Summit 2026 is confirmed! We're excited to have you join us.\n\n"
            "Event Details:\n"
            "Date: March 15-17, 2026\n"
            "Location: Moscone Center, San Francisco\n"
            "Your badge: Attendee (check-in at registration desk)\n\n"
            "Don't miss the keynote on AI in Enterprise at 9 AM on Day 1.\n\n"
            "See you there!\n"
            "Tech Summit Team"
        ),
        "category": "Notification",
        "urgency": "low",
        "confidence": 0.83,
        "explanation": "Event registration confirmation.",
        "needs_response": False,
        "suggested_followup": False,
    },
    {
        "sender_email": "invest@crypto-millionaire.biz",
        "sender_name": "Crypto Investment Opportunity",
        "subject": "Double your Bitcoin in 24 hours - Guaranteed!",
        "body_text": (
            "Dear Investor,\n\n"
            "We are offering an exclusive opportunity to DOUBLE your Bitcoin investment "
            "in just 24 hours! Our AI-powered trading bot guarantees 100% returns.\n\n"
            "Minimum investment: 0.5 BTC\n"
            "Returns: 100% in 24 hours\n"
            "Risk: ZERO (fully guaranteed)\n\n"
            "Send your Bitcoin to the address below and watch your money grow!\n"
            "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh\n\n"
            "Limited spots available! Act NOW!"
        ),
        "category": "Spam",
        "urgency": "low",
        "confidence": 0.98,
        "explanation": "Crypto investment scam with unrealistic guaranteed returns.",
        "needs_response": False,
        "suggested_followup": False,
    },
    {
        "sender_email": "alex.rodriguez@devteam.com",
        "sender_name": "Alex Rodriguez",
        "subject": "Standup notes + quick question about the API",
        "body_text": (
            "Morning!\n\n"
            "Quick standup update from my side:\n"
            "Yesterday: Finished the authentication module, started on the API rate limiter\n"
            "Today: Completing rate limiter, writing tests\n"
            "Blockers: None\n\n"
            "Quick question — for the new /analytics endpoint, should we paginate the results "
            "or return everything at once? The dataset could be large for enterprise accounts.\n\n"
            "Let me know your thoughts when you have a chance. No rush.\n\n"
            "Alex"
        ),
        "category": "Work",
        "urgency": "medium",
        "confidence": 0.81,
        "explanation": "Work standup update with a technical question.",
        "needs_response": True,
        "suggested_followup": False,
    },
    {
        "sender_email": "support@webhosting.com",
        "sender_name": "Customer Support",
        "subject": "Re: Re: Your support ticket #4823 - Website backup issue",
        "body_text": (
            "Hi,\n\n"
            "Thank you for your patience. I've investigated the backup issue you reported "
            "and found that the automated backup process was failing due to insufficient "
            "disk space on your hosting plan.\n\n"
            "I've temporarily increased your storage and triggered a manual backup, which "
            "completed successfully. To prevent this in the future, I recommend:\n\n"
            "1. Upgrading to the Pro plan (100GB storage)\n"
            "2. Setting up automated cleanup of old backups\n\n"
            "Please let me know if the issue is resolved on your end.\n\n"
            "Best regards,\nSupport Team\nWebHosting"
        ),
        "category": "Customer Support",
        "urgency": "medium",
        "confidence": 0.87,
        "explanation": "Support follow-up resolving a technical issue.",
        "needs_response": True,
        "suggested_followup": False,
    },
    {
        "sender_email": "designer@creativeagency.com",
        "sender_name": "Rachel Green",
        "subject": "Logo concepts ready for your review",
        "body_text": (
            "Hi,\n\n"
            "I've completed the initial logo concepts for your brand! We have 5 different "
            "directions to explore, each with a unique personality.\n\n"
            "I've attached the mood board and the concepts as a PDF. "
            "Take your time reviewing them — no rush. When you're ready, we can schedule "
            "a call to discuss which direction resonates most.\n\n"
            "Looking forward to your feedback!\n\n"
            "Rachel\nCreative Agency"
        ),
        "category": "Work",
        "urgency": "medium",
        "confidence": 0.76,
        "explanation": "Work deliverable for review with no urgent deadline.",
        "needs_response": True,
        "suggested_followup": False,
    },
    {
        "sender_email": "random.person@mysterydomain.xyz",
        "sender_name": "Jordan Blake",
        "subject": "Just wanted to share something interesting",
        "body_text": (
            "Hi,\n\n"
            "I came across your profile and thought you might find this interesting. "
            "It's not really work-related or anything specific — just something I've been "
            "thinking about lately that I wanted to share with someone in the field.\n\n"
            "No action needed, just thought I'd pass it along!\n\n"
            "Best,\nJordan"
        ),
        "category": "Other",
        "urgency": "low",
        "confidence": 0.45,
        "explanation": "General message with no clear category signal.",
        "needs_response": False,
        "suggested_followup": False,
    },
]


def get_demo_emails() -> list:
    """Return demo emails with timestamps spread over the past 14 days."""
    result = []
    days_offset = 0
    for i, item in enumerate(DEMO_EMAILS):
        entry = dict(item)
        # Remove non-schema keys that might have typos
        entry.pop("connected", None)
        entry.pop("shared", None)
        # Spread emails across the past 14 days
        days_ago = min(i, 14)
        entry["received_at"] = NOW - timedelta(days=days_ago, hours=random.randint(0, 12))
        result.append(entry)
    return result
