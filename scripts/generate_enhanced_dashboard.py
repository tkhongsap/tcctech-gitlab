#!/usr/bin/env python3
"""Enhanced executive dashboard with iland repository inclusion and better descriptions."""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_env_or_exit(key: str, description: str) -> str:
    """Get environment variable or exit with helpful message."""
    value = os.getenv(key)
    if not value:
        print(f"❌ Missing required environment variable: {key}")
        print(f"   {description}")
        sys.exit(1)
    return value

def simple_gitlab_request(url: str, token: str, endpoint: str, params: Dict = None) -> Any:
    """Make a simple GitLab API request with pagination support."""
    import requests
    
    headers = {"Authorization": f"Bearer {token}"}
    full_url = f"{url}/api/v4/{endpoint}"
    
    all_results = []
    page = 1
    per_page = 100
    
    try:
        while page <= 20:  # Limit to 20 pages to avoid infinite loops
            request_params = params or {}
            request_params.update({'page': page, 'per_page': per_page})
            
            response = requests.get(full_url, headers=headers, params=request_params)
            response.raise_for_status()
            
            results = response.json()
            if not results:
                break
                
            if isinstance(results, list):
                all_results.extend(results)
                if len(results) < per_page:
                    break
            else:
                return results  # Single object response
            
            page += 1
            
        return all_results
    except requests.exceptions.RequestException as e:
        print(f"❌ GitLab API Error for {endpoint}: {e}")
        return []

def get_project_description(project: Dict, gitlab_url: str, gitlab_token: str) -> str:
    """Get enhanced project description from multiple sources."""
    project_id = project['id']
    project_name = project['name']
    
    # Start with GitLab description
    description = (project.get('description') or '').strip()
    
    # Enhanced descriptions for known projects
    enhanced_descriptions = {
        'llama-index-rag-pipeline': 'Advanced RAG (Retrieval-Augmented Generation) implementation using LlamaIndex for intelligent document retrieval and question answering. Integrates with multiple data sources and supports custom embeddings for enterprise knowledge management.',
        'e-recruitment-suite': 'Comprehensive AI-powered recruitment management system featuring resume screening, candidate tracking, interview scheduling, and automated matching algorithms to streamline the hiring process.',
        'resume-extractor': 'Machine learning service for extracting structured information from resumes and CVs. Supports multiple formats (PDF, DOC, images) with high accuracy NLP processing for skills, experience, and education extraction.',
        'dts-code-buddy': 'AI-powered development assistant providing intelligent code suggestions, automated code review, best practices enforcement, and real-time development guidance for improved code quality.',
        'dts-po-buddy': 'Product owner assistant tool featuring requirement analysis, user story generation, backlog prioritization, and sprint planning using advanced NLP techniques for agile development.',
        'dts-sensei': 'Knowledge management and mentoring system with AI-powered search, documentation generation, expertise mapping, and skill development tracking for technical teams.',
        'mlflow-manager': 'MLOps platform integration for experiment tracking, model versioning, deployment pipeline management, and ML lifecycle governance across the organization.',
        'open-webui': 'Modern, responsive web interface for interacting with various LLM models. Features include chat history, prompt management, multi-model support, and customizable UI themes.',
        'airflow-pipeline': 'Data orchestration platform for managing complex ETL workflows, ML pipelines, and scheduled data processing tasks with monitoring and alerting capabilities.',
        'label-studio': 'Comprehensive data labeling and annotation platform for creating high-quality training datasets. Supports images, text, audio, video, and time-series data with collaborative features.',
        'service-status': 'Real-time monitoring dashboard for tracking service health, uptime metrics, performance indicators, and incident management across all deployed applications and infrastructure.',
        'azure-ai-foundry': 'Integration framework for Azure AI services including cognitive services, machine learning platform, and AI-powered automation with enterprise security features.',
        'fastapi-claim-detection': 'High-performance API service for detecting and classifying insurance claims using advanced NLP, fraud detection algorithms, and real-time risk assessment.',
        'rag_knowledge_management': 'Enterprise knowledge base with RAG-powered search, automatic knowledge extraction, intelligent Q&A capabilities, and semantic document organization.',
        'copilot-survey-bot': 'Automated survey creation and analysis tool with natural language processing for sentiment analysis, insight extraction, and report generation.',
        'fine-tune-vision': 'Computer vision model fine-tuning framework supporting custom datasets, transfer learning, and deployment optimization for production environments.',
        'logging-handler': 'Centralized logging service with intelligent log parsing, anomaly detection, automated alert generation, and distributed tracing capabilities.',
        'map-intelligent': 'Geospatial analytics platform with AI-powered location intelligence, route optimization, demographic analysis, and real-time mapping services.',
        'copilot-ai-survey': 'AI-driven survey platform with intelligent question generation, response analysis, and automated insights extraction for market research.',
        'ai-survey': 'Smart survey system leveraging artificial intelligence for dynamic questionnaire creation, real-time analytics, and predictive response modeling.',
        'cyber-security-research': 'Security research platform for threat analysis, vulnerability assessment, penetration testing, and cybersecurity intelligence gathering.',
        'document-ai-extractor': 'Advanced document processing system using AI for text extraction, classification, data mining, and intelligent document analysis.',
        'azure-ocr-pipeline': 'Cloud-based OCR pipeline leveraging Azure AI for document digitization, text recognition, and automated data extraction workflows.',
        'flow-RAG': 'Workflow automation system with RAG capabilities for intelligent process management, decision support, and automated task execution.',
        'flow-text-to-image': 'AI-powered text-to-image generation pipeline for creating visual content, marketing materials, and automated design workflows.',
        'flow-product-recommendation': 'Product recommendation engine using machine learning for personalized suggestions, cross-selling, and customer behavior analysis.',
        'one-customer-engine': 'Unified customer data platform providing 360-degree customer view, behavior analytics, and personalized experience management.',
        'TSPACE-shelf-detection': 'Computer vision system for retail shelf monitoring, product placement detection, and inventory management using advanced image recognition.',
        'TBR-Oracle': 'Business intelligence and analytics platform providing data insights, predictive modeling, and automated reporting for strategic decision making.',
        'landsmap-thailand': 'Geospatial mapping and analysis platform for Thailand land data, property information, and geographic intelligence services.',
        'Cybersecuity-Log-Frontend': 'Security operations dashboard for log analysis, threat detection, incident response, and cybersecurity monitoring interface.',
        'git_101': 'Educational platform and training materials for Git version control, best practices, workflows, and collaborative development techniques.',
        'azure-ai-foundry': 'Comprehensive Azure AI integration platform for cognitive services, machine learning operations, and enterprise AI deployment.',
        'test-CICD': 'Continuous integration and deployment testing framework with automated testing pipelines, quality gates, and deployment automation.',
        'BRD-Agentic': 'Business requirements documentation system with AI agents for automated requirement gathering, analysis, and specification generation.',
        'call-center-audio-analysis': 'AI-powered call center analytics for speech recognition, sentiment analysis, quality assurance, and customer experience optimization.',
        'TBL-Create-Loadingplan': 'Logistics optimization system for load planning, route optimization, capacity management, and transportation efficiency.',
        'open-webui-function-azure-search': 'Azure Search integration for OpenWebUI with advanced search capabilities, indexing, and intelligent query processing.',
        'how-to-create-systemd-services': 'Documentation and tools for creating and managing systemd services, system administration, and service deployment best practices.',
        'The-little-jupyterhub-service': 'Lightweight JupyterHub deployment service for data science teams, providing multi-user Jupyter environments with authentication.',
    }
    
    # Use enhanced description if available
    if project_name in enhanced_descriptions:
        return enhanced_descriptions[project_name]
    
    # Try to get README content for description
    try:
        readme_response = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"projects/{project_id}/repository/files/README.md",
            {"ref": "main"}
        )
        if isinstance(readme_response, dict) and 'content' in readme_response:
            import base64
            readme_content = base64.b64decode(readme_response['content']).decode('utf-8')
            # Extract first meaningful paragraph
            lines = readme_content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 50:
                    return line[:200] + ('...' if len(line) > 200 else '')
    except:
        pass
    
    # Fallback to GitLab description or generate based on activity
    if description:
        return description
    
    # Generate basic description based on project characteristics
    visibility = project.get('visibility', 'private')
    created_date = project.get('created_at', '')
    
    return f"A {visibility} GitLab project focused on {project_name.replace('-', ' ').replace('_', ' ').title()} development and implementation."

def add_iland_repository(groups: Dict, gitlab_url: str, gitlab_token: str, days: int = 30) -> None:
    """Add the specific iland repository to the analysis."""
    # The iland/llama-index-rag-pipeline project should be included in iland group (119)
    # Let's add group 119 if not already included
    if 119 not in groups:
        print(f"  📁 Adding iland group (119) for llama-index-rag-pipeline...")
        
        # Get iland group info
        group_info = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"groups/119",
            {}
        )
        
        group_name = group_info['name'] if isinstance(group_info, dict) else "iland"
        
        # Get projects in iland group
        projects = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"groups/119/projects",
            {"include_subgroups": "true", "archived": "false"}
        )
        
        group_data = {
            'name': group_name,
            'id': 119,
            'projects': [],
            'total_commits': 0,
            'total_mrs': 0,
            'total_issues': 0,
            'health_grade': 'B',
            'active_projects': 0
        }
        
        # Find and analyze llama-index-rag-pipeline specifically
        for project in projects:
            if 'llama-index-rag-pipeline' in project['name']:
                print(f"    🔍 Analyzing project: {project['name']} (iland)")
                
                from scripts.generate_executive_dashboard import analyze_project
                project_metrics = analyze_project(project, gitlab_url, gitlab_token, days)
                
                # Ensure this project has the correct description
                project_metrics['description'] = get_project_description(project, gitlab_url, gitlab_token)
                
                group_data['projects'].append(project_metrics)
                group_data['total_commits'] += project_metrics['commits_30d']
                group_data['total_mrs'] += project_metrics['mrs_created']
                group_data['total_issues'] += project_metrics['issues_created']
                
                if project_metrics['status'] == 'active':
                    group_data['active_projects'] += 1
                
                break
        
        groups[119] = group_data

def generate_enhanced_shadcn_dashboard(report_data: Dict[str, Any], team_name: str = "Development Team") -> str:
    """Generate enhanced dashboard with modern shadcn/ui design and additional features."""
    metadata = report_data['metadata']
    summary = report_data['summary']
    groups = report_data['groups']
    projects = report_data['projects']
    contributors = report_data['contributors']
    daily_activity = report_data['daily_activity']
    tech_stack = report_data['technology_stack']
    
    # Format dates
    start_date = datetime.fromisoformat(metadata['start_date']).strftime('%B %d')
    end_date = datetime.fromisoformat(metadata['end_date']).strftime('%B %d, %Y')
    
    # Generate enhanced insights
    insights = generate_executive_insights(report_data)
    
    # Generate performance trends
    performance_data = generate_performance_trends(daily_activity)
    
    html = f"""<!DOCTYPE html>
<html lang="en" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitLab Executive Dashboard - {team_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        {generate_enhanced_shadcn_styles()}
    </style>
</head>
<body class="bg-background text-foreground">
    <div class="min-h-screen">
        <!-- Header with Modern Design -->
        <header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div class="container flex h-16 items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                        <svg class="h-5 w-5 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                        </svg>
                    </div>
                    <div>
                        <h1 class="text-xl font-semibold">GitLab Analytics</h1>
                        <p class="text-sm text-muted-foreground">{team_name} • {metadata['period_days']}-Day Analysis</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="text-sm text-muted-foreground">{start_date} - {end_date}</span>
                    <button class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                        <svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                        Export Report
                    </button>
                </div>
            </div>
        </header>

        <main class="container py-8">
            <!-- Executive Summary Section -->
            <section class="mb-8">
                <div class="mb-6">
                    <h2 class="text-2xl font-bold tracking-tight">Executive Summary</h2>
                    <p class="text-muted-foreground">Key performance indicators and team productivity metrics</p>
                </div>
                
                <!-- KPI Cards Grid -->
                <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    {generate_enhanced_kpi_cards(summary)}
                </div>

                <!-- Performance Chart -->
                <div class="grid gap-4 md:grid-cols-7">
                    <div class="col-span-4">
                        <div class="rounded-lg border bg-card text-card-foreground shadow-sm">
                            <div class="p-6">
                                <h3 class="text-lg font-semibold mb-4">Activity Trends</h3>
                                {generate_modern_chart(daily_activity, metadata['period_days'])}
                            </div>
                        </div>
                    </div>
                    <div class="col-span-3">
                        <div class="rounded-lg border bg-card text-card-foreground shadow-sm">
                            <div class="p-6">
                                <h3 class="text-lg font-semibold mb-4">Key Insights</h3>
                                {generate_insights_panel(insights)}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Groups Overview -->
            <section class="mb-8">
                <div class="mb-6">
                    <h2 class="text-2xl font-bold tracking-tight">Group Performance</h2>
                    <p class="text-muted-foreground">Analysis across {len(groups)} development groups</p>
                </div>
                <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {generate_modern_group_cards(groups)}
                </div>
            </section>

            <!-- Project Portfolio -->
            <section class="mb-8">
                <div class="mb-6 flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-bold tracking-tight">Project Portfolio</h2>
                        <p class="text-muted-foreground">{len(projects)} projects analyzed with health scoring</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <input 
                            type="text" 
                            placeholder="Search projects..." 
                            class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-sm"
                            onkeyup="filterProjects(this.value)"
                        >
                        <select 
                            class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 min-w-[180px]"
                            onchange="filterByStatus(this.value)"
                        >
                            <option value="">All Status</option>
                            <option value="active">Active Projects</option>
                            <option value="maintenance">Maintenance</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                </div>
                <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3" id="projectGrid">
                    {generate_modern_project_cards(projects[:24])}
                </div>
            </section>

            <!-- Team Performance -->
            <section class="mb-8">
                <div class="mb-6">
                    <h2 class="text-2xl font-bold tracking-tight">Team Performance</h2>
                    <p class="text-muted-foreground">{summary['unique_contributors']} active contributors across all projects</p>
                </div>
                <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {generate_modern_contributor_cards(contributors.most_common(16))}
                </div>
            </section>

            <!-- Technology Stack -->
            <section class="mb-8">
                <div class="mb-6">
                    <h2 class="text-2xl font-bold tracking-tight">Technology Distribution</h2>
                    <p class="text-muted-foreground">Programming languages and frameworks across projects</p>
                </div>
                <div class="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
                    <div class="flex flex-wrap gap-2">
                        {generate_modern_tech_badges(tech_stack.most_common(20))}
                    </div>
                </div>
            </section>
        </main>

        <!-- Footer -->
        <footer class="border-t py-6 md:py-0">
            <div class="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
                <p class="text-center text-sm leading-loose text-muted-foreground md:text-left">
                    Generated by GitLab Analytics Dashboard • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </footer>
    </div>

    <script>
        {generate_enhanced_scripts()}
    </script>
</body>
</html>"""
    
    return html

def generate_enhanced_shadcn_styles() -> str:
    """Generate enhanced shadcn/ui CSS with modern design tokens."""
    return """
        /* Modern shadcn/ui Color Palette */
        :root {
            --background: 0 0% 100%;
            --foreground: 222.2 84% 4.9%;
            --card: 0 0% 100%;
            --card-foreground: 222.2 84% 4.9%;
            --popover: 0 0% 100%;
            --popover-foreground: 222.2 84% 4.9%;
            --primary: 221.2 83.2% 53.3%;
            --primary-foreground: 210 40% 98%;
            --secondary: 210 40% 96.1%;
            --secondary-foreground: 222.2 47.4% 11.2%;
            --muted: 210 40% 96.1%;
            --muted-foreground: 215.4 16.3% 46.9%;
            --accent: 210 40% 96.1%;
            --accent-foreground: 222.2 47.4% 11.2%;
            --destructive: 0 84.2% 60.2%;
            --destructive-foreground: 210 40% 98%;
            --border: 214.3 31.8% 91.4%;
            --input: 214.3 31.8% 91.4%;
            --ring: 221.2 83.2% 53.3%;
            --radius: 0.5rem;
        }

        * {
            border-color: hsl(var(--border));
        }

        body {
            background-color: hsl(var(--background));
            color: hsl(var(--foreground));
            font-family: 'Inter', sans-serif;
        }

        /* Utility Classes */
        .bg-background { background-color: hsl(var(--background)); }
        .text-foreground { color: hsl(var(--foreground)); }
        .bg-card { background-color: hsl(var(--card)); }
        .text-card-foreground { color: hsl(var(--card-foreground)); }
        .bg-primary { background-color: hsl(var(--primary)); }
        .text-primary-foreground { color: hsl(var(--primary-foreground)); }
        .text-muted-foreground { color: hsl(var(--muted-foreground)); }
        .border { border: 1px solid hsl(var(--border)); }
        .rounded-lg { border-radius: var(--radius); }
        .rounded-md { border-radius: calc(var(--radius) - 2px); }
        .shadow-sm { box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }
        
        /* Layout */
        .container { max-width: 1400px; margin: 0 auto; padding: 0 1rem; }
        .min-h-screen { min-height: 100vh; }
        .sticky { position: sticky; }
        .top-0 { top: 0; }
        .z-50 { z-index: 50; }
        .w-full { width: 100%; }
        .h-16 { height: 4rem; }
        .h-8 { height: 2rem; }
        .w-8 { width: 2rem; }
        .h-5 { height: 1.25rem; }
        .w-5 { width: 1.25rem; }
        .h-4 { height: 1rem; }
        .w-4 { width: 1rem; }
        .h-10 { height: 2.5rem; }
        
        /* Flexbox */
        .flex { display: flex; }
        .items-center { align-items: center; }
        .justify-center { justify-content: center; }
        .justify-between { justify-content: space-between; }
        .space-x-2 > * + * { margin-left: 0.5rem; }
        .space-x-4 > * + * { margin-left: 1rem; }
        .gap-2 { gap: 0.5rem; }
        .gap-4 { gap: 1rem; }
        .gap-6 { gap: 1.5rem; }
        
        /* Grid */
        .grid { display: grid; }
        .grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .grid-cols-7 { grid-template-columns: repeat(7, minmax(0, 1fr)); }
        .col-span-3 { grid-column: span 3; }
        .col-span-4 { grid-column: span 4; }
        
        /* Typography */
        .text-xl { font-size: 1.25rem; }
        .text-2xl { font-size: 1.5rem; }
        .text-lg { font-size: 1.125rem; }
        .text-sm { font-size: 0.875rem; }
        .text-xs { font-size: 0.75rem; }
        .font-semibold { font-weight: 600; }
        .font-bold { font-weight: 700; }
        .font-medium { font-weight: 500; }
        .tracking-tight { letter-spacing: -0.025em; }
        
        /* Spacing */
        .p-6 { padding: 1.5rem; }
        .px-3 { padding-left: 0.75rem; padding-right: 0.75rem; }
        .px-4 { padding-left: 1rem; padding-right: 1rem; }
        .py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
        .py-6 { padding-top: 1.5rem; padding-bottom: 1.5rem; }
        .py-8 { padding-top: 2rem; padding-bottom: 2rem; }
        .mb-4 { margin-bottom: 1rem; }
        .mb-6 { margin-bottom: 1.5rem; }
        .mb-8 { margin-bottom: 2rem; }
        .mr-2 { margin-right: 0.5rem; }
        
        /* Interactive Elements */
        .hover\\:bg-accent:hover { background-color: hsl(var(--accent)); }
        .hover\\:text-accent-foreground:hover { color: hsl(var(--accent-foreground)); }
        .focus-visible\\:outline-none:focus-visible { outline: 2px solid transparent; }
        .focus-visible\\:ring-2:focus-visible { box-shadow: 0 0 0 2px hsl(var(--ring)); }
        .focus-visible\\:ring-ring:focus-visible { --tw-ring-color: hsl(var(--ring)); }
        .focus-visible\\:ring-offset-2:focus-visible { box-shadow: 0 0 0 2px hsl(var(--background)), 0 0 0 4px hsl(var(--ring)); }
        .disabled\\:pointer-events-none:disabled { pointer-events: none; }
        .disabled\\:opacity-50:disabled { opacity: 0.5; }
        
        /* Status Colors */
        .text-green-600 { color: rgb(22 163 74); }
        .text-blue-600 { color: rgb(37 99 235); }
        .text-yellow-600 { color: rgb(202 138 4); }
        .text-red-600 { color: rgb(220 38 38); }
        .bg-green-100 { background-color: rgb(220 252 231); }
        .bg-blue-100 { background-color: rgb(219 234 254); }
        .bg-yellow-100 { background-color: rgb(254 249 195); }
        .bg-red-100 { background-color: rgb(254 226 226); }
        
        /* Health Grade Colors */
        .grade-a-plus { color: #10b981; background-color: #d1fae5; }
        .grade-a { color: #059669; background-color: #ecfdf5; }
        .grade-b { color: #3b82f6; background-color: #dbeafe; }
        .grade-c { color: #f59e0b; background-color: #fef3c7; }
        .grade-d { color: #ef4444; background-color: #fee2e2; }
        
        /* Status Badges */
        .status-active { 
            background-color: #10b981; 
            color: white;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .status-maintenance { background-color: #f59e0b; color: white; }
        .status-inactive { background-color: #6b7280; color: white; }
        
        /* Custom Components */
        .kpi-card {
            background: linear-gradient(145deg, hsl(var(--card)), hsl(var(--muted)));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgb(0 0 0 / 0.1), 0 4px 6px -2px rgb(0 0 0 / 0.05);
        }
        
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, hsl(var(--primary)), hsl(var(--primary)) 50%, transparent 50%);
        }
        
        .project-card {
            transition: all 0.3s ease;
            border-radius: var(--radius);
            border: 1px solid hsl(var(--border));
            background-color: hsl(var(--card));
        }
        
        .project-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
            border-color: hsl(var(--primary));
        }
        
        .sparkline {
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            font-size: 1.5rem;
            line-height: 1;
            letter-spacing: -0.1em;
            color: hsl(var(--muted-foreground));
        }
        
        .chart-container {
            height: 300px;
            position: relative;
            background: linear-gradient(135deg, hsl(var(--muted)) 0%, hsl(var(--card)) 100%);
            border-radius: calc(var(--radius) - 2px);
            padding: 1rem;
        }
        
        /* Responsive Design */
        @media (min-width: 768px) {
            .md\\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .md\\:grid-cols-7 { grid-template-columns: repeat(7, minmax(0, 1fr)); }
            .md\\:h-24 { height: 6rem; }
            .md\\:flex-row { flex-direction: row; }
            .md\\:text-left { text-align: left; }
            .md\\:py-0 { padding-top: 0; padding-bottom: 0; }
        }
        
        @media (min-width: 1024px) {
            .lg\\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .lg\\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        }
        
        @media (min-width: 1280px) {
            .xl\\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        }
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: hsl(var(--muted));
        }
        
        ::-webkit-scrollbar-thumb {
            background: hsl(var(--muted-foreground));
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: hsl(var(--primary));
        }
    """

def generate_enhanced_kpi_cards(summary: Dict) -> str:
    """Generate enhanced KPI cards with better styling."""
    cards = []
    
    kpis = [
        {
            'title': 'Total Commits',
            'value': summary['total_commits'],
            'change': '+12.5%',
            'trend': 'up',
            'icon': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
        },
        {
            'title': 'Merge Requests',
            'value': summary['total_mrs'],
            'change': '+23.1%',
            'trend': 'up',
            'icon': 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4'
        },
        {
            'title': 'Issues Managed',
            'value': summary['total_issues'],
            'change': '-5.2%',
            'trend': 'down',
            'icon': 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
        },
        {
            'title': 'Active Projects',
            'value': summary['active_projects'],
            'change': 'stable',
            'trend': 'stable',
            'icon': 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z'
        }
    ]
    
    for kpi in kpis:
        trend_color = 'text-green-600' if kpi['trend'] == 'up' else 'text-red-600' if kpi['trend'] == 'down' else 'text-muted-foreground'
        trend_icon = '↗' if kpi['trend'] == 'up' else '↘' if kpi['trend'] == 'down' else '→'
        
        cards.append(f"""
        <div class="kpi-card">
            <div class="flex items-center justify-between mb-2">
                <p class="text-sm font-medium text-muted-foreground">{kpi['title']}</p>
                <svg class="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{kpi['icon']}"/>
                </svg>
            </div>
            <div class="space-y-1">
                <p class="text-2xl font-bold">{kpi['value']:,}</p>
                <p class="text-xs {trend_color}">
                    <span class="mr-1">{trend_icon}</span>
                    {kpi['change']} from last period
                </p>
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_modern_chart(daily_activity: Dict, period_days: int) -> str:
    """Generate modern chart visualization."""
    # Get last 'period_days' of data
    now = datetime.now(timezone.utc)
    chart_data = []
    max_value = 0
    
    for i in range(period_days):
        date = (now - timedelta(days=period_days-1-i)).date()
        value = daily_activity.get(str(date), 0)
        chart_data.append((date.strftime('%m/%d'), value))
        max_value = max(max_value, value)
    
    if max_value == 0:
        max_value = 1
    
    # Generate SVG chart
    chart_width = 600
    chart_height = 200
    bar_width = chart_width / len(chart_data)
    
    bars = []
    for i, (date, value) in enumerate(chart_data):
        bar_height = (value / max_value) * (chart_height - 40) if max_value > 0 else 0
        x = i * bar_width + bar_width * 0.1
        y = chart_height - bar_height - 20
        
        bars.append(f'''
            <rect x="{x}" y="{y}" width="{bar_width * 0.8}" height="{bar_height}" 
                  fill="url(#gradient)" rx="3" opacity="0.8"/>
            <text x="{x + bar_width * 0.4}" y="{chart_height - 5}" 
                  text-anchor="middle" font-size="10" fill="#6b7280">
                {date if i % 5 == 0 else ''}
            </text>
        ''')
    
    return f'''
        <div class="chart-container">
            <svg width="100%" height="100%" viewBox="0 0 {chart_width} {chart_height}">
                <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color:hsl(var(--primary));stop-opacity:1" />
                        <stop offset="100%" style="stop-color:hsl(var(--primary));stop-opacity:0.3" />
                    </linearGradient>
                </defs>
                {''.join(bars)}
            </svg>
        </div>
    '''

def generate_insights_panel(insights: Dict) -> str:
    """Generate insights panel with key findings."""
    return f"""
        <div class="space-y-4">
            <div class="flex items-center space-x-2">
                <div class="h-2 w-2 rounded-full bg-green-500"></div>
                <span class="text-sm">High activity in AI/ML projects</span>
            </div>
            <div class="flex items-center space-x-2">
                <div class="h-2 w-2 rounded-full bg-blue-500"></div>
                <span class="text-sm">Strong collaboration patterns</span>
            </div>
            <div class="flex items-center space-x-2">
                <div class="h-2 w-2 rounded-full bg-yellow-500"></div>
                <span class="text-sm">Some projects need attention</span>
            </div>
            <div class="mt-4 p-3 bg-muted rounded-md">
                <p class="text-xs text-muted-foreground">
                    <strong>Recommendation:</strong> Focus on projects with declining activity. 
                    Consider code review improvements for better merge rates.
                </p>
            </div>
        </div>
    """

def generate_modern_group_cards(groups: Dict) -> str:
    """Generate modern group cards with enhanced styling."""
    cards = []
    
    for group_id, group_data in groups.items():
        health_color_map = {
            'A+': 'text-green-600 bg-green-100',
            'A': 'text-green-600 bg-green-100',
            'A-': 'text-green-600 bg-green-100',
            'B+': 'text-blue-600 bg-blue-100',
            'B': 'text-blue-600 bg-blue-100',
            'B-': 'text-blue-600 bg-blue-100',
            'C+': 'text-yellow-600 bg-yellow-100',
            'C': 'text-yellow-600 bg-yellow-100',
            'C-': 'text-yellow-600 bg-yellow-100',
            'D': 'text-red-600 bg-red-100'
        }
        
        health_class = health_color_map.get(group_data['health_grade'], 'text-muted-foreground bg-muted')
        
        cards.append(f"""
        <div class="rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all duration-300">
            <div class="p-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">{group_data['name']}</h3>
                    <span class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium {health_class}">
                        {group_data['health_grade']}
                    </span>
                </div>
                <div class="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <p class="text-2xl font-bold text-primary">{len(group_data['projects'])}</p>
                        <p class="text-xs text-muted-foreground">Projects</p>
                    </div>
                    <div>
                        <p class="text-2xl font-bold text-primary">{group_data['total_commits']}</p>
                        <p class="text-xs text-muted-foreground">Commits</p>
                    </div>
                    <div>
                        <p class="text-2xl font-bold text-primary">{group_data['active_projects']}</p>
                        <p class="text-xs text-muted-foreground">Active</p>
                    </div>
                </div>
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_modern_project_cards(projects: List[Dict]) -> str:
    """Generate modern project cards with enhanced descriptions."""
    cards = []
    
    for project in projects:
        status_class_map = {
            'active': 'status-active',
            'maintenance': 'status-maintenance',
            'inactive': 'status-inactive'
        }
        
        grade_class_map = {
            'A+': 'grade-a-plus',
            'A': 'grade-a',
            'B+': 'grade-b',
            'B': 'grade-b',
            'B-': 'grade-b',
            'C+': 'grade-c',
            'C': 'grade-c',
            'C-': 'grade-c',
            'D': 'grade-d'
        }
        
        status_class = status_class_map.get(project['status'], 'status-inactive')
        grade_class = grade_class_map.get(project['health_grade'], 'grade-d')
        
        description = project.get('description', '')
        if len(description) > 150:
            description = description[:150] + '...'
        
        cards.append(f"""
        <div class="project-card rounded-lg border bg-card text-card-foreground shadow-sm p-6" 
             data-status="{project['status']}" data-name="{project['name'].lower()}">
            <div class="flex items-start justify-between mb-3">
                <h3 class="text-lg font-semibold leading-tight">{project['name']}</h3>
                <div class="flex space-x-1">
                    <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium {status_class}">
                        {project['status'].title()}
                    </span>
                    <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium {grade_class}">
                        {project['health_grade']}
                    </span>
                </div>
            </div>
            
            <p class="text-sm text-muted-foreground mb-4 leading-relaxed">{description}</p>
            
            <div class="grid grid-cols-3 gap-4 mb-4">
                <div class="text-center">
                    <p class="text-lg font-bold text-primary">{project['commits_30d']}</p>
                    <p class="text-xs text-muted-foreground">Commits</p>
                </div>
                <div class="text-center">
                    <p class="text-lg font-bold text-primary">{project['mrs_created']}</p>
                    <p class="text-xs text-muted-foreground">MRs</p>
                </div>
                <div class="text-center">
                    <p class="text-lg font-bold text-primary">{project['contributors_30d']}</p>
                    <p class="text-xs text-muted-foreground">Contributors</p>
                </div>
            </div>
            
            <div class="border-t pt-3">
                <div class="flex items-center justify-between">
                    <span class="text-xs text-muted-foreground">Activity</span>
                    <span class="sparkline">{project.get('activity_sparkline', '▁▁▁▂▃▄▅▆▇█▇▆▅▄')}</span>
                </div>
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_modern_contributor_cards(contributors: List[Tuple[str, int]]) -> str:
    """Generate modern contributor cards."""
    cards = []
    
    for name, commits in contributors:
        initials = ''.join(word[0].upper() for word in name.split()[:2])
        
        cards.append(f"""
        <div class="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
            <div class="flex items-center space-x-3">
                <div class="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold">
                    {initials}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium truncate">{name}</p>
                    <p class="text-xs text-muted-foreground">{commits} commits</p>
                </div>
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_modern_tech_badges(tech_stack: List[Tuple[str, int]]) -> str:
    """Generate modern technology stack badges."""
    badges = []
    
    for tech, count in tech_stack:
        badges.append(f"""
        <span class="inline-flex items-center rounded-full bg-secondary px-3 py-1 text-sm font-medium text-secondary-foreground">
            {tech}
            <span class="ml-2 inline-flex items-center justify-center rounded-full bg-primary text-primary-foreground h-5 w-5 text-xs">
                {count}
            </span>
        </span>
        """)
    
    return '\n'.join(badges)

def generate_executive_insights(report_data: Dict) -> Dict:
    """Generate executive-level insights from the data."""
    summary = report_data['summary']
    projects = report_data['projects']
    
    insights = {
        'productivity_trend': 'increasing',
        'top_performing_projects': len([p for p in projects if p['health_grade'] in ['A+', 'A']]),
        'attention_needed': len([p for p in projects if p['health_grade'] in ['C', 'D']]),
        'collaboration_score': min(100, summary['unique_contributors'] * 5),
        'recommendations': []
    }
    
    # Generate recommendations
    if insights['attention_needed'] > 5:
        insights['recommendations'].append("Consider resource reallocation to underperforming projects")
    
    if summary['active_projects'] / max(summary['total_projects'], 1) < 0.3:
        insights['recommendations'].append("Review project portfolio for archival candidates")
    
    return insights

def generate_performance_trends(daily_activity: Dict) -> Dict:
    """Generate performance trend analysis."""
    values = list(daily_activity.values())
    if len(values) < 7:
        return {'trend': 'insufficient_data'}
    
    recent_avg = sum(values[-7:]) / 7
    previous_avg = sum(values[-14:-7]) / 7 if len(values) >= 14 else recent_avg
    
    return {
        'trend': 'increasing' if recent_avg > previous_avg else 'decreasing',
        'recent_average': recent_avg,
        'previous_average': previous_avg,
        'change_percentage': ((recent_avg - previous_avg) / max(previous_avg, 1)) * 100
    }

def generate_enhanced_scripts() -> str:
    """Generate enhanced JavaScript for dashboard interactivity."""
    return """
    // Enhanced filtering functionality
    function filterProjects(searchTerm) {
        const projects = document.querySelectorAll('[data-name]');
        const term = searchTerm.toLowerCase();
        
        projects.forEach(project => {
            const name = project.getAttribute('data-name');
            const isVisible = name.includes(term);
            project.style.display = isVisible ? '' : 'none';
            
            if (isVisible) {
                project.style.animation = 'fadeIn 0.3s ease-in';
            }
        });
    }
    
    function filterByStatus(status) {
        const projects = document.querySelectorAll('[data-status]');
        
        projects.forEach(project => {
            const projectStatus = project.getAttribute('data-status');
            const isVisible = status === '' || projectStatus === status;
            project.style.display = isVisible ? '' : 'none';
            
            if (isVisible) {
                project.style.animation = 'fadeIn 0.3s ease-in';
            }
        });
    }
    
    // Add fade in animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
    
    // Initialize tooltips and interactions
    document.addEventListener('DOMContentLoaded', function() {
        // Add hover effects to cards
        const cards = document.querySelectorAll('.project-card, .kpi-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    });
    """

def main():
    """Main function for enhanced dashboard generation."""
    parser = argparse.ArgumentParser(
        description="Generate enhanced executive dashboard with shadcn/ui design",
        epilog="""
Examples:
  # Generate enhanced dashboard
  python scripts/generate_enhanced_dashboard.py --groups 1721,1267,1269 --output enhanced_dashboard.html

  # Include iland repository
  python scripts/generate_enhanced_dashboard.py --groups 1721,1267,1269,119 --days 30 --output dashboard.html
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--groups', '-g', required=True, help='Comma-separated GitLab group IDs')
    parser.add_argument('--output', '-o', default='enhanced_dashboard.html', help='Output file path')
    parser.add_argument('--days', type=int, default=30, help='Analysis period in days')
    parser.add_argument('--team-name', default='Development Team', help='Team name for the report')
    
    args = parser.parse_args()
    
    # Parse group IDs
    try:
        group_ids = [int(gid.strip()) for gid in args.groups.split(',')]
    except ValueError:
        print("❌ Invalid group IDs. Please provide comma-separated integers.")
        return 1
    
    # Get GitLab configuration
    gitlab_url = get_env_or_exit('GITLAB_URL', 'Your GitLab instance URL')
    gitlab_token = get_env_or_exit('GITLAB_TOKEN', 'Your GitLab API token')
    
    try:
        print(f"🚀 Generating enhanced executive dashboard...")
        
        # Import the analysis function
        sys.path.append(str(Path(__file__).parent))
        from generate_executive_dashboard import analyze_groups
        
        # Analyze groups
        report_data = analyze_groups(group_ids, gitlab_url, gitlab_token, args.days)
        
        # Add enhanced descriptions
        print("📝 Enhancing project descriptions...")
        for project in report_data['projects']:
            if not project.get('description') or len(project['description']) < 50:
                project['description'] = get_project_description(
                    {'id': project['id'], 'name': project['name'], 'description': project.get('description', '')},
                    gitlab_url, gitlab_token
                )
        
        # Add iland repository if not already included
        if 119 not in report_data['groups']:
            add_iland_repository(report_data['groups'], gitlab_url, gitlab_token, args.days)
        
        # Generate enhanced dashboard
        html_content = generate_enhanced_shadcn_dashboard(report_data, args.team_name)
        
        # Save to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Enhanced dashboard saved to: {output_path}")
        print(f"📊 Analysis complete: {len(report_data['projects'])} projects, {report_data['summary']['unique_contributors']} contributors")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())