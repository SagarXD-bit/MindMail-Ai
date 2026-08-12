# MailMind AI — Schema

## Database Tables

### users
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AI | |
| name | VARCHAR(100) | |
| email | VARCHAR(255) | unique |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### email_accounts
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AI | |
| user_id | INT FK→users.id | |
| email_address | VARCHAR(255) | |
| imap_server | VARCHAR(255) | |
| imap_port | INT | default 993 |
| imap_ssl | BOOLEAN | default true |
| smtp_server | VARCHAR(255) | nullable |
| smtp_port | INT | nullable |
| encrypted_password | TEXT | Fernet-encrypted |
| status | VARCHAR(20) | connected / error / demo / disconnected |
| last_sync_at | DATETIME | nullable |
| created_at / updated_at | DATETIME | |

### emails
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AI | |
| user_id | INT FK | |
| account_id | INT FK→email_accounts.id | nullable |
| message_id | VARCHAR(255) | for dedup / threading |
| thread_id | VARCHAR(255) | nullable |
| sender_email | VARCHAR(255) | |
| sender_name | VARCHAR(255) | nullable |
| recipient_email | VARCHAR(255) | |
| subject | VARCHAR(500) | |
| body_text | MEDIUMTEXT | plain-text body |
| body_html | MEDIUMTEXT | nullable |
| preview | VARCHAR(300) | first ~150 chars |
| received_at | DATETIME | |
| status | VARCHAR(20) | unread / read / responded / archived |
| is_demo | BOOLEAN | default false |
| created_at | DATETIME | |

### ai_classifications
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AI | |
| email_id | INT FK→emails.id | unique |
| category | VARCHAR(40) | one of 11 categories |
| urgency | VARCHAR(20) | critical/high/medium/low |
| confidence | FLOAT | 0.0–1.0 |
| explanation | TEXT | nullable, AI reasoning |
| needs_response | BOOLEAN | AI flag |
| suggested_followup | BOOLEAN | AI flag |
| is_manual_override | BOOLEAN | default false |
| created_at | DATETIME | |

### reply_suggestions
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AI | |
| email_id | INT FK→emails.id | |
| tone | VARCHAR(20) | professional/friendly/concise |
| content | MEDIUMTEXT | |
| status | VARCHAR(20) | draft / used / discarded |
| created_at | DATETIME | |

### follow_ups
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AI | |
| user_id | INT FK | |
| email_id | INT FK→emails.id | |
| reminder_at | DATETIME | |
| note | TEXT | nullable |
| status | VARCHAR(20) | pending / completed / snoozed |
| completed_at | DATETIME | nullable |
| created_at | DATETIME | |

### user_feedback
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AI | |
| email_id | INT FK→emails.id | |
| original_category | VARCHAR(40) | |
| corrected_category | VARCHAR(40) | |
| original_urgency | VARCHAR(20) | |
| corrected_urgency | VARCHAR(20) | |
| created_at | DATETIME | |

## Relationships
```
users 1—* email_accounts 1—* emails
emails 1—1 ai_classifications
emails 1—* reply_suggestions
emails 1—* follow_ups
emails 1—* user_feedback
```

## API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | /api/health | health check |
| GET | /api/settings | get settings |
| PUT | /api/settings | update settings |
| GET | /api/accounts | list accounts |
| POST | /api/accounts | create + test IMAP connection |
| DELETE | /api/accounts/{id} | disconnect |
| POST | /api/accounts/{id}/test | test connection |
| POST | /api/sync | fetch new emails (IMAP or demo) |
| GET | /api/emails | list (search, filter, sort, paginate) |
| GET | /api/emails/{id} | detail (classification, replies, follow-ups) |
| PATCH | /api/emails/{id}/status | update status (read/responded) |
| PATCH | /api/emails/{id}/classification | manual override |
| POST | /api/emails/{id}/replies | generate reply (tone) |
| PATCH | /api/emails/{id}/replies/{rid} | edit / mark used / discard |
| POST | /api/emails/{id}/send | send reply via SMTP (confirm) |
| GET | /api/follow-ups | list (status filter) |
| POST | /api/follow-ups | create |
| PATCH | /api/follow-ups/{id} | complete / snooze / edit |
| DELETE | /api/follow-ups/{id} | delete |
| GET | /api/analytics | aggregate metrics + distributions |
