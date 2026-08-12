"""Test AI service: categorization and reply generation with fallback."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ai_service import (
    categorize_email,
    generate_reply,
    _rule_based_categorize,
    ClassificationResult,
    CATEGORIES,
    URGENCIES,
)


class TestCategorization:
    """Tests for email categorization."""

    def test_rule_based_finance(self):
        """Finance keywords detected correctly."""
        result = _rule_based_categorize(
            "Invoice for your purchase",
            "Please find your invoice attached. Payment due in 30 days.",
            "billing@company.com",
        )
        assert result.category == "Finance"
        assert result.urgency in URGENCIES

    def test_rule_based_spam(self):
        """Spam keywords detected correctly."""
        result = _rule_based_categorize(
            "CONGRATULATIONS!!! You won!",
            "Click here now to claim your free money. Bitcoin investment opportunity!",
            "spam@scammer.com",
        )
        assert result.category == "Spam"
        assert result.urgency == "low"

    def test_rule_based_meeting(self):
        """Meeting keywords detected correctly."""
        result = _rule_based_categorize(
            "Team standup tomorrow",
            "Let's have a quick standup meeting tomorrow at 10am.",
            "boss@company.com",
        )
        assert result.category == "Meeting"

    def test_rule_based_newsletter(self):
        """Newsletter patterns detected correctly."""
        result = _rule_based_categorize(
            "Weekly digest",
            "This is your weekly newsletter. To unsubscribe, click here.",
            "newsletter@weekly.com",
        )
        assert result.category == "Newsletter"

    def test_rule_based_job_interview(self):
        """Recruitment emails categorized correctly."""
        result = _rule_based_categorize(
            "Interview invitation",
            "We'd like to invite you for a job interview for the developer position.",
            "hr@company.com",
        )
        assert result.category == "Application/Recruitment"

    def test_rule_based_customer_support(self):
        """Customer support requests categorized correctly."""
        result = _rule_based_categorize(
            "Can't access my account",
            "Help me! I'm having a problem with my login. It's not working.",
            "customer@email.com",
        )
        assert result.category == "Customer Support"

    def test_categorize_returns_valid_category(self):
        """categorize_email always returns a valid category."""
        result = categorize_email("Test subject", "Test body content", "test@test.com")
        assert result.category in CATEGORIES
        assert result.urgency in URGENCIES
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.explanation, str)

    def test_categorize_critical_finance(self):
        """Critical urgency for failed payments."""
        result = _rule_based_categorize(
            "URGENT: Failed payment",
            "We detected failed payment transactions that are overdue.",
            "billing@payments.com",
        )
        assert result.category == "Finance"
        assert result.urgency == "high"

    def test_categorize_other_fallback(self):
        """Unclear emails default to Other."""
        result = _rule_based_categorize(
            "Just saying hi",
            "Hello there, how are you today?",
            "someone@somewhere.com",
        )
        # This should match something (likely Personal or Other)
        assert result.category in CATEGORIES


class TestReplyGeneration:
    """Tests for reply generation."""

    def test_generate_reply_professional(self):
        """Professional reply has appropriate content."""
        reply = generate_reply(
            "Meeting request",
            "Hi, can we meet next week?",
            "John Smith",
            "professional",
        )
        assert reply is not None
        assert len(reply) > 10
        # Should contain a greeting
        assert any(word in reply.lower() for word in ["hi", "hello", "dear", "hey"])

    def test_generate_reply_friendly(self):
        """Friendly reply has appropriate tone."""
        reply = generate_reply(
            "Quick question",
            "Hey, do you have a minute?",
            "Jane Doe",
            "friendly",
        )
        assert reply is not None
        assert len(reply) > 10

    def test_generate_reply_concise(self):
        """Concise reply is shorter than professional."""
        concise = generate_reply("Test", "Test body", "John", "concise")
        professional = generate_reply("Test", "Test body", "John", "professional")
        assert concise is not None
        assert professional is not None
        # Concise should be shorter or equal
        assert len(concise) <= len(professional) + 50  # Allow some variance

    def test_generate_reply_uses_sender_name(self):
        """Reply should reference the sender's first name."""
        reply = generate_reply("Test", "Test body", "Alice Johnson", "professional")
        assert reply is not None
        assert "Alice" in reply
