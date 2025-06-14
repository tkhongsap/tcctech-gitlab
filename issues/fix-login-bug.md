---
title: Fix Critical Login Bug - Users Unable to Access Accounts
labels: [bug, critical, urgent]
priority: critical
weight: 3
---

## Bug Description

Users are reporting that they cannot login to their accounts. The login form submits successfully but users are redirected back to the login page instead of the dashboard.

## Steps to Reproduce

1. Go to /login
2. Enter valid credentials
3. Click "Login" button
4. Observe: User is redirected back to /login instead of /dashboard

## Expected Behavior

After successful authentication, users should be redirected to their dashboard.

## Actual Behavior

Users are stuck in a login loop and cannot access their accounts.

## Investigation Notes

- Started happening after yesterday's deployment
- Affects approximately 30% of users
- Seems to be related to session cookie handling
- Error in console: "SameSite cookie attribute warning"

## Proposed Fix

Check the session middleware configuration and ensure cookies are being set with proper SameSite and Secure attributes.

#bug #authentication #production