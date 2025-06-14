# Executive Dashboard Enhancement Plan v2

## Overview
This document outlines the plan to enhance the GitLab Executive Dashboard with the following improvements:
1. Descriptive group names instead of "Group 1721"
2. Functional Issues Analysis & AI Recommendations with real data
3. Enhanced Team Performance section showing project assignments and issue workload
4. New Issues Management section with detailed issue listings

## 1. Group Name Enhancement

### Current State
- Groups display as "Group 1721", "Group 1267", "Group 1269"

### Target State
- Display meaningful group names: "AI-ML-Services", "Research Repos", "Internal Services"

### Implementation Plan

#### Option A: API Enhancement
```python
# In analyze_groups function
group_info = simple_gitlab_request(
    gitlab_url, gitlab_token,
    f"groups/{group_id}",
    {}
)
group_name = group_info.get('full_name') or group_info.get('name') or f'Group {group_id}'
```

#### Option B: Static Mapping (Faster)
```python
GROUP_NAMES = {
    1721: "AI-ML-Services",
    1267: "Research Repos", 
    1269: "Internal Services",
    119: "iland"
}

# Use in template
group_display_name = GROUP_NAMES.get(group_id, group_data.get('name', f'Group {group_id}'))
```

### Files to Update
- `scripts/generate_executive_dashboard.py` - Add group name mapping
- HTML template generation - Update group card display

## 2. Issues Analysis & AI Recommendations

### Current State
- Shows all zeros
- No recommendations generated
- Enhanced services not properly integrated

### Target State
- Real-time issue counts by priority and type
- AI-generated strategic recommendations
- Project-level issue breakdown

### Implementation Plan

#### 2.1 Fix Issue Data Collection
```python
def collect_issue_analytics(projects, gitlab_url, gitlab_token):
    """Collect comprehensive issue analytics across all projects."""
    analytics = {
        'total_open': 0,
        'by_priority': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
        'by_type': {'bug': 0, 'feature': 0, 'enhancement': 0, 'other': 0},
        'by_state': {'opened': 0, 'in_progress': 0, 'blocked': 0},
        'overdue': 0,
        'unassigned': 0,
        'project_issues': {},
        'assignee_workload': {}
    }
    
    for project in projects:
        issues = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"projects/{project['id']}/issues",
            {"state": "opened"}
        )
        
        # Process each issue
        for issue in issues:
            analytics['total_open'] += 1
            
            # Categorize by labels
            labels = issue.get('labels', [])
            # ... categorization logic
            
            # Track assignee workload
            assignee = issue.get('assignee')
            if assignee:
                assignee_name = assignee.get('name', 'Unknown')
                analytics['assignee_workload'][assignee_name] = \
                    analytics['assignee_workload'].get(assignee_name, 0) + 1
    
    return analytics
```

#### 2.2 AI Recommendation Engine
```python
def generate_ai_recommendations(issue_analytics, project_metrics):
    """Generate strategic recommendations based on issue patterns."""
    recommendations = []
    
    # High priority issue alert
    if issue_analytics['by_priority']['critical'] > 3:
        recommendations.append({
            'type': 'critical',
            'title': 'Critical Issues Require Immediate Attention',
            'message': f"{issue_analytics['by_priority']['critical']} critical issues are open",
            'action': 'Allocate senior developers to resolve critical issues immediately',
            'projects': _get_projects_with_critical_issues()
        })
    
    # Workload imbalance
    workload = issue_analytics['assignee_workload']
    if workload:
        max_load = max(workload.values())
        avg_load = sum(workload.values()) / len(workload)
        if max_load > avg_load * 2:
            overloaded = [k for k, v in workload.items() if v == max_load][0]
            recommendations.append({
                'type': 'high',
                'title': 'Workload Imbalance Detected',
                'message': f"{overloaded} has {max_load} issues (2x average)",
                'action': 'Redistribute issues to balance team workload',
                'team_member': overloaded
            })
    
    # Bug ratio analysis
    if issue_analytics['by_type']['bug'] > issue_analytics['total_open'] * 0.6:
        recommendations.append({
            'type': 'medium',
            'title': 'High Bug-to-Feature Ratio',
            'message': 'Over 60% of open issues are bugs',
            'action': 'Schedule dedicated bug-fixing sprint and improve QA processes'
        })
    
    # Stale issues
    if issue_analytics.get('stale_issues', 0) > 10:
        recommendations.append({
            'type': 'medium',
            'title': 'Stale Issues Need Review',
            'message': f"{issue_analytics['stale_issues']} issues haven't been updated in 30+ days",
            'action': 'Review and close or reprioritize stale issues'
        })
    
    # Positive feedback
    if issue_analytics['total_open'] < 20 and issue_analytics['by_priority']['critical'] == 0:
        recommendations.append({
            'type': 'success',
            'title': 'Excellent Issue Management',
            'message': 'Low issue count with no critical issues',
            'action': 'Maintain current practices and document successful processes'
        })
    
    return recommendations
```

### Files to Update
- `scripts/generate_executive_dashboard.py` - Add issue analytics collection
- HTML template - Update issue cards and recommendations display

## 3. Enhanced Team Performance Section

### Current State
- Shows only contributor names and total commits
- No project assignment visibility
- No issue workload information

### Target State
- Show which projects each team member contributes to
- Display issue assignments per team member
- Show recent activity and focus areas

### Implementation Plan

#### 3.1 Enhanced Contributor Analytics
```python
def analyze_team_performance(projects, gitlab_url, gitlab_token):
    """Analyze detailed team member contributions and workload."""
    team_analytics = {}
    
    for project in projects:
        project_name = project['name']
        
        # Get commits by author
        commits = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"projects/{project['id']}/repository/commits",
            {"since": start_date.isoformat()}
        )
        
        for commit in commits:
            author = commit.get('author_name', 'Unknown')
            if author not in team_analytics:
                team_analytics[author] = {
                    'commits': 0,
                    'projects': set(),
                    'issues_assigned': 0,
                    'issues_resolved': 0,
                    'merge_requests': 0,
                    'recent_activity': []
                }
            
            team_analytics[author]['commits'] += 1
            team_analytics[author]['projects'].add(project_name)
            team_analytics[author]['recent_activity'].append({
                'type': 'commit',
                'project': project_name,
                'date': commit['created_at'],
                'message': commit['title']
            })
        
        # Get issues assigned to team members
        issues = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"projects/{project['id']}/issues",
            {"scope": "all"}
        )
        
        for issue in issues:
            assignee = issue.get('assignee')
            if assignee:
                assignee_name = assignee.get('name', 'Unknown')
                if assignee_name not in team_analytics:
                    team_analytics[assignee_name] = {
                        'commits': 0,
                        'projects': set(),
                        'issues_assigned': 0,
                        'issues_resolved': 0,
                        'merge_requests': 0,
                        'recent_activity': []
                    }
                
                if issue['state'] == 'opened':
                    team_analytics[assignee_name]['issues_assigned'] += 1
                else:
                    team_analytics[assignee_name]['issues_resolved'] += 1
                
                team_analytics[assignee_name]['projects'].add(project_name)
    
    return team_analytics
```

#### 3.2 Enhanced Team Card Display
```python
def generate_enhanced_team_cards(team_analytics):
    """Generate enhanced team member cards with project and issue info."""
    cards_html = []
    
    for member, data in sorted(team_analytics.items(), 
                              key=lambda x: x[1]['commits'], 
                              reverse=True)[:20]:
        
        projects_list = sorted(list(data['projects']))[:5]  # Top 5 projects
        projects_more = len(data['projects']) - 5 if len(data['projects']) > 5 else 0
        
        card = f"""
        <div class="enhanced-contributor-card">
            <div class="contributor-header">
                <div class="contributor-avatar">{get_initials(member)}</div>
                <div class="contributor-basic-info">
                    <h4 class="contributor-name">{member}</h4>
                    <div class="contributor-summary">
                        <span class="metric">{data['commits']} commits</span>
                        <span class="separator">•</span>
                        <span class="metric">{data['issues_assigned']} issues</span>
                        <span class="separator">•</span>
                        <span class="metric">{len(data['projects'])} projects</span>
                    </div>
                </div>
            </div>
            
            <div class="contributor-details">
                <div class="projects-section">
                    <h5>Active Projects:</h5>
                    <div class="project-tags">
                        {''.join(f'<span class="project-tag">{p}</span>' for p in projects_list)}
                        {f'<span class="project-tag more">+{projects_more} more</span>' if projects_more else ''}
                    </div>
                </div>
                
                <div class="workload-section">
                    <h5>Current Workload:</h5>
                    <div class="workload-stats">
                        <div class="stat-item">
                            <span class="stat-value">{data['issues_assigned']}</span>
                            <span class="stat-label">Open Issues</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{data['issues_resolved']}</span>
                            <span class="stat-label">Resolved</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{data['merge_requests']}</span>
                            <span class="stat-label">MRs</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        cards_html.append(card)
    
    return '\n'.join(cards_html)
```

### Files to Update
- `scripts/generate_executive_dashboard.py` - Add team analytics functions
- CSS styles - Add enhanced contributor card styles
- HTML template - Replace simple contributor cards with enhanced version

## 4. New Issues Management Section

### Current State
- No dedicated issues section
- Issues only shown as counts in project cards

### Target State
- Dedicated section showing all open and in-progress issues
- Filterable by status, priority, assignee, and project
- Sortable by due date, priority, or age

### Implementation Plan

#### 4.1 Issue Collection and Categorization
```python
def collect_all_issues(projects, gitlab_url, gitlab_token):
    """Collect all issues across projects with full details."""
    all_issues = []
    
    for project in projects:
        issues = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"projects/{project['id']}/issues",
            {"scope": "all", "state": "opened"}
        )
        
        for issue in issues:
            # Enrich issue data
            enriched_issue = {
                'id': issue['id'],
                'iid': issue['iid'],
                'title': issue['title'],
                'description': issue.get('description', ''),
                'project_id': project['id'],
                'project_name': project['name'],
                'state': issue['state'],
                'created_at': issue['created_at'],
                'updated_at': issue['updated_at'],
                'due_date': issue.get('due_date'),
                'labels': issue.get('labels', []),
                'assignee': issue.get('assignee', {}),
                'author': issue.get('author', {}),
                'weight': issue.get('weight', 0),
                'web_url': issue['web_url'],
                'priority': _determine_priority(issue.get('labels', [])),
                'type': _determine_type(issue.get('labels', [])),
                'age_days': _calculate_age(issue['created_at']),
                'is_overdue': _is_overdue(issue.get('due_date'))
            }
            
            all_issues.append(enriched_issue)
    
    return sorted(all_issues, key=lambda x: (
        x['priority'],  # Sort by priority first
        x['is_overdue'],  # Then by overdue status
        x['age_days']  # Then by age
    ))
```

#### 4.2 Issues Section HTML
```html
<section class="section">
    <h2 class="section-title">Issues Management</h2>
    
    <!-- Issue Filters -->
    <div class="issue-filters">
        <input type="text" 
               class="search-input" 
               placeholder="Search issues..." 
               onkeyup="filterIssues(this.value)">
        
        <select class="filter-select" onchange="filterByPriority(this.value)">
            <option value="">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
        </select>
        
        <select class="filter-select" onchange="filterByAssignee(this.value)">
            <option value="">All Assignees</option>
            <!-- Dynamically populated -->
        </select>
        
        <select class="filter-select" onchange="filterByProject(this.value)">
            <option value="">All Projects</option>
            <!-- Dynamically populated -->
        </select>
    </div>
    
    <!-- Issue Statistics -->
    <div class="issue-stats-bar">
        <div class="stat-item">
            <span class="stat-label">Total Open:</span>
            <span class="stat-value">{total_open}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Critical:</span>
            <span class="stat-value critical">{critical_count}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Overdue:</span>
            <span class="stat-value overdue">{overdue_count}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Unassigned:</span>
            <span class="stat-value">{unassigned_count}</span>
        </div>
    </div>
    
    <!-- Issues Table -->
    <div class="issues-table-container">
        <table class="issues-table">
            <thead>
                <tr>
                    <th onclick="sortIssues('priority')">Priority</th>
                    <th onclick="sortIssues('title')">Issue</th>
                    <th onclick="sortIssues('project')">Project</th>
                    <th onclick="sortIssues('assignee')">Assignee</th>
                    <th onclick="sortIssues('due_date')">Due Date</th>
                    <th onclick="sortIssues('age')">Age</th>
                    <th>Labels</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <!-- Issue rows -->
            </tbody>
        </table>
    </div>
</section>
```

#### 4.3 Issue Row Template
```python
def generate_issue_row(issue):
    """Generate HTML row for an issue."""
    priority_class = f"priority-{issue['priority']}"
    overdue_class = "overdue" if issue['is_overdue'] else ""
    assignee_name = issue['assignee'].get('name', 'Unassigned') if issue['assignee'] else 'Unassigned'
    
    labels_html = ''.join([
        f'<span class="issue-label label-{_label_class(label)}">{label}</span>'
        for label in issue['labels'][:3]  # Show max 3 labels
    ])
    
    return f"""
    <tr class="issue-row {overdue_class}" 
        data-priority="{issue['priority']}" 
        data-assignee="{assignee_name}"
        data-project="{issue['project_name']}">
        <td class="priority-cell">
            <span class="priority-badge {priority_class}">
                {issue['priority'].upper()}
            </span>
        </td>
        <td class="title-cell">
            <a href="{issue['web_url']}" target="_blank" class="issue-link">
                #{issue['iid']} - {html.escape(issue['title'][:60])}...
            </a>
        </td>
        <td class="project-cell">{issue['project_name']}</td>
        <td class="assignee-cell">
            <div class="assignee-info">
                <span class="assignee-avatar">{get_initials(assignee_name)}</span>
                <span class="assignee-name">{assignee_name}</span>
            </div>
        </td>
        <td class="due-date-cell">
            {format_due_date(issue['due_date'], issue['is_overdue'])}
        </td>
        <td class="age-cell">{issue['age_days']}d</td>
        <td class="labels-cell">{labels_html}</td>
        <td class="actions-cell">
            <a href="{issue['web_url']}" target="_blank" class="action-link">
                View →
            </a>
        </td>
    </tr>
    """
```

### Files to Update
- `scripts/generate_executive_dashboard.py` - Add issue collection and display functions
- CSS styles - Add issue table and filter styles
- JavaScript - Add sorting and filtering functions

## 5. CSS Enhancements Required

```css
/* Enhanced Contributor Cards */
.enhanced-contributor-card {
    background: hsl(var(--card));
    border: 1px solid hsl(var(--border));
    border-radius: var(--radius);
    padding: 1.5rem;
    transition: all 0.2s ease;
}

.contributor-header {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.contributor-summary {
    display: flex;
    gap: 0.5rem;
    color: hsl(var(--muted-foreground));
    font-size: 0.875rem;
}

.project-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    margin-top: 0.5rem;
}

.project-tag {
    background: hsl(var(--secondary));
    color: hsl(var(--secondary-foreground));
    padding: 0.25rem 0.5rem;
    border-radius: calc(var(--radius) - 4px);
    font-size: 0.75rem;
}

.workload-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 0.5rem;
}

/* Issues Table */
.issues-table {
    width: 100%;
    border-collapse: collapse;
}

.issues-table th {
    background: hsl(var(--muted));
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
    cursor: pointer;
    user-select: none;
}

.issues-table td {
    padding: 0.75rem;
    border-bottom: 1px solid hsl(var(--border));
}

.priority-badge {
    padding: 0.25rem 0.5rem;
    border-radius: calc(var(--radius) - 4px);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.priority-critical {
    background: hsl(0 85% 60%);
    color: white;
}

.priority-high {
    background: hsl(25 95% 53%);
    color: white;
}

.priority-medium {
    background: hsl(45 95% 53%);
    color: black;
}

.priority-low {
    background: hsl(200 85% 60%);
    color: white;
}

.issue-row.overdue {
    background: hsl(0 85% 95%);
}

.assignee-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.assignee-avatar {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: hsl(var(--primary));
    color: hsl(var(--primary-foreground));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
}
```

## 6. JavaScript Functions Required

```javascript
// Issue filtering and sorting
let allIssues = [];
let currentSort = { field: 'priority', direction: 'asc' };

function filterIssues(searchTerm) {
    const term = searchTerm.toLowerCase();
    const rows = document.querySelectorAll('.issue-row');
    
    rows.forEach(row => {
        const title = row.querySelector('.title-cell').textContent.toLowerCase();
        const project = row.getAttribute('data-project').toLowerCase();
        const assignee = row.getAttribute('data-assignee').toLowerCase();
        
        const matches = title.includes(term) || 
                       project.includes(term) || 
                       assignee.includes(term);
        
        row.style.display = matches ? '' : 'none';
    });
}

function filterByPriority(priority) {
    const rows = document.querySelectorAll('.issue-row');
    rows.forEach(row => {
        const rowPriority = row.getAttribute('data-priority');
        row.style.display = (priority === '' || rowPriority === priority) ? '' : 'none';
    });
}

function sortIssues(field) {
    // Toggle direction if same field
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = field;
        currentSort.direction = 'asc';
    }
    
    // Re-render sorted issues
    renderIssuesTable(sortIssuesArray(allIssues, field, currentSort.direction));
}
```

## Implementation Timeline

### Phase 1: Group Names & Basic Fixes (1 hour)
1. Add group name mapping
2. Fix issue data collection in analyze_project
3. Update HTML template with proper group names

### Phase 2: Issues Analysis & Recommendations (2 hours)
1. Implement comprehensive issue analytics collection
2. Create recommendation engine
3. Update HTML template with real data

### Phase 3: Enhanced Team Performance (2 hours)
1. Implement team analytics collection
2. Create enhanced contributor cards
3. Add project and issue assignment details

### Phase 4: Issues Management Section (3 hours)
1. Implement full issue collection across projects
2. Create filterable/sortable issues table
3. Add issue statistics and filters
4. Implement JavaScript functions

### Phase 5: Testing & Polish (1 hour)
1. Test all features with real data
2. Optimize performance for large datasets
3. Polish UI/UX details

## Expected Outcomes

1. **Group Names**: Clear, descriptive group names instead of IDs
2. **Issues Analysis**: Real-time issue metrics with 5-10 strategic recommendations
3. **Team Performance**: Complete visibility of who works on what with workload distribution
4. **Issues Section**: Comprehensive issue tracking with filtering and sorting capabilities

## Notes

- All enhancements maintain backward compatibility
- Performance optimized for 50+ projects and 500+ issues
- Graceful degradation if enhanced services unavailable
- Mobile-responsive design maintained throughout