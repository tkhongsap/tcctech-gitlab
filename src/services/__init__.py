"""Business logic services."""

from .issue_service import IssueService
from .branch_service import BranchService
from .analytics import GitLabAnalytics
from .nlp_issue_service import NLPIssueService

# Weekly reports available conditionally
try:
    from .weekly_reports import WeeklyProductivityReporter
    from .email_service import EmailService, WeeklyReportEmailSender
    __all__ = ['IssueService', 'BranchService', 'GitLabAnalytics', 'NLPIssueService', 'WeeklyProductivityReporter', 'EmailService', 'WeeklyReportEmailSender']
except ImportError:
    __all__ = ['IssueService', 'BranchService', 'GitLabAnalytics', 'NLPIssueService']