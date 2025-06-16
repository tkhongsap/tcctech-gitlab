# Simple script to create GitLab issues
# Using project ID 1037 that we found from the successful creation

Write-Host "Creating Dashboard Service Issue..." -ForegroundColor Green

python scripts/create_issues.py 1037 `
  --title "Create Dashboard Service with REST API and Modern Web Interface" `
  --description "Build a complete dashboard solution with both backend API and frontend interface for our GitLab analytics.

**Backend API Service:**
- REST API exposing existing analytics from /scripts
- Key endpoints: /api/projects/{id}/metrics, /api/groups/{id}/analytics, /api/dashboard/summary
- Use FastAPI framework with existing analytics code

**Frontend Dashboard:**
- Modern web interface showing project health, team metrics, and trends
- Real-time updates and interactive charts
- Clean, professional design (similar to existing shadcn/ui styling in generate_executive_dashboard.py)
- Mobile-responsive layout
- Use existing HTML/CSS patterns from our current dashboard generation

**Features:**
- Project health scores with visual indicators
- Team activity charts and contributor rankings  
- Issue and MR analytics with trends
- Group-wide overviews and comparisons
- Export capabilities (PDF, Excel)

Leverage all existing analytics logic from /scripts directory." `


Write-Host "`nCreating Weekly Updates Issue..." -ForegroundColor Green  

python scripts/create_issues.py 1037 `
  --title "Create Automated Weekly Team Update System" `
  --description "Build scheduled weekly update system that sends team performance summaries every Monday and Friday morning.

**Schedule:**
- Monday mornings: Weekly kickoff with project health overview and priorities
- Friday mornings: Weekly wrap-up with accomplishments and areas needing attention

**Update Content:**
- Project health scores and changes from previous week
- Team activity summary (commits, MRs, issues)
- Projects needing attention (health score < 60, stale activity)
- Top contributors and achievements
- Upcoming deadlines and overdue items

**Delivery Channels:**
- Email reports (use existing email service from /scripts)
- MS Teams channel updates
- Optional: Post to dashboard for historical viewing

**Implementation:**
- Extend existing weekly_reports.py and send_report_email.py
- Add cron job/scheduler for Monday and Friday mornings
- Use existing analytics and health scoring logic
- Template-based email formatting (leverage existing templates)
- MS Teams webhook integration for channel notifications

Build on existing weekly reporting infrastructure in /scripts directory." `

Write-Host "Done! Both issues should be created." -ForegroundColor Green 