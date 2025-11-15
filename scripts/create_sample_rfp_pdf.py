#!/usr/bin/env python3
"""Create sample RFP PDF with good service matching potential."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def create_sample_rfp_pdf():
    """Create sample RFP PDF."""
    
    output_path = Path(__file__).parent.parent / "data" / "sample_rfp_with_matching.pdf"
    
    # Create document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#333333',
        spaceAfter=6,
        alignment=TA_CENTER
    )
    heading_style = styles['Heading2']
    subheading_style = styles['Heading3']
    body_style = styles['BodyText']
    
    # Content
    story = []
    
    # Title Page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("REQUEST FOR PROPOSAL (RFP)", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Cloud-Based E-Commerce Platform Development", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Project details
    details = [
        ("<b>Project Title:</b> Next-Generation E-Commerce Platform"),
        ("<b>Client:</b> TechRetail Inc."),
        ("<b>RFP Issued:</b> January 15, 2025"),
        ("<b>Proposal Deadline:</b> February 15, 2025"),
        ("<b>Project Start Date:</b> March 1, 2025"),
        ("<b>Budget:</b> $500,000 - $750,000"),
    ]
    for detail in details:
        story.append(Paragraph(detail, body_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Section 1: Project Overview
    story.append(Paragraph("1. PROJECT OVERVIEW", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "TechRetail Inc. is seeking a qualified software development partner to design, develop, "
        "and deploy a modern cloud-based e-commerce platform. The platform will serve 100,000+ daily "
        "users and must support high transaction volumes with 99.9% uptime.",
        body_style
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Section 2: Technical Requirements
    story.append(Paragraph("2. TECHNICAL REQUIREMENTS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # 2.1 Cloud Infrastructure
    story.append(Paragraph("2.1 Cloud Infrastructure", subheading_style))
    cloud_reqs = [
        "Deploy on AWS cloud infrastructure with multi-region support for high availability and disaster recovery",
        "Implement Kubernetes orchestration for container management with automated scaling policies",
        "Configure CI/CD pipelines using GitHub Actions or Jenkins for continuous integration and deployment",
        "Utilize Infrastructure as Code with Terraform for reproducible infrastructure provisioning",
        "Set up auto-scaling and load balancing for peak traffic handling up to 50,000 concurrent users",
        "Implement disaster recovery and backup strategies with RPO less than 1 hour and RTO less than 4 hours",
        "Monitoring and alerting using Prometheus and Grafana with 24/7 incident response",
    ]
    for req in cloud_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 2.2 Custom Software Development
    story.append(Paragraph("2.2 Custom Software Development", subheading_style))
    dev_reqs = [
        "Build full-stack web application using React.js for frontend with Redux state management",
        "Develop RESTful APIs using Node.js and Python FastAPI with comprehensive documentation",
        "Implement microservices architecture for scalability with service mesh (Istio)",
        "Create mobile-responsive design supporting iOS and Android devices using React Native",
        "Integrate with third-party payment gateways including Stripe, PayPal, and Authorize.net",
        "Database: PostgreSQL for transactional data, MongoDB for product catalog, Redis for caching",
        "Real-time inventory updates using WebSockets for instant stock level synchronization",
        "API integration with shipping providers (FedEx, UPS, USPS) and ERP systems",
    ]
    for req in dev_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 2.3 AI & Machine Learning
    story.append(Paragraph("2.3 AI & Machine Learning Features", subheading_style))
    ai_reqs = [
        "Product recommendation engine based on user behavior using collaborative filtering algorithms",
        "Natural Language Processing for intelligent search functionality and chatbot customer support",
        "Predictive analytics for inventory forecasting using time series analysis (LSTM, Prophet)",
        "Computer vision for visual product search enabling customers to upload images to find similar products",
        "Fraud detection using anomaly detection algorithms to identify suspicious transactions",
        "Machine learning model deployment using MLOps practices with automated retraining pipelines",
    ]
    for req in ai_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # 2.4 Data Analytics
    story.append(Paragraph("2.4 Data Analytics & Business Intelligence", subheading_style))
    data_reqs = [
        "Real-time analytics dashboard using Tableau or Power BI for business insights and KPI tracking",
        "ETL pipelines for data warehousing in Snowflake with incremental data processing",
        "Customer behavior tracking and reporting including funnel analysis and cohort analysis",
        "Sales forecasting and predictive analytics using machine learning models",
        "Data visualization for executive reporting with automated daily and weekly reports",
        "SQL optimization and query tuning for fast dashboard load times (under 3 seconds)",
    ]
    for req in data_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 2.5 UI/UX Design
    story.append(Paragraph("2.5 UI/UX Design Requirements", subheading_style))
    design_reqs = [
        "User-centered design with accessibility compliance (WCAG 2.1 AA standards)",
        "High-fidelity prototypes using Figma with interactive components and design tokens",
        "Responsive and mobile-first design approach ensuring seamless experience across all devices",
        "A/B testing framework for conversion optimization with statistical significance testing",
        "Design system creation for brand consistency including component library and style guide",
        "Usability testing with real users (minimum 20 participants per test cycle)",
    ]
    for req in design_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Section 3: QA Requirements
    story.append(Paragraph("3. QUALITY ASSURANCE REQUIREMENTS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("3.1 Testing Services", subheading_style))
    qa_reqs = [
        "Automated testing using Selenium and Cypress with continuous test execution in CI/CD pipeline",
        "Performance and load testing to handle 10,000 concurrent users using JMeter or k6",
        "Security testing and penetration testing following OWASP Top 10 guidelines",
        "API testing with Postman and REST Assured including contract testing",
        "Mobile app testing on iOS and Android devices using Appium",
        "Regression testing for all deployments with automated smoke tests",
        "Test coverage must exceed 80% for both backend and frontend code",
    ]
    for req in qa_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3.2 Security & Compliance", subheading_style))
    security_reqs = [
        "SOC 2 Type II compliance required with annual audit and reporting",
        "GDPR compliance for EU customers including data privacy controls and consent management",
        "PCI DSS compliance for payment processing with secure card data handling",
        "Security audits and vulnerability assessments using automated scanning tools",
        "Penetration testing conducted quarterly by certified ethical hackers",
        "Security code reviews for all critical components and authentication flows",
        "Incident response planning with defined escalation procedures and runbooks",
    ]
    for req in security_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(PageBreak())
    
    # Section 4: Staffing & Timeline
    story.append(Paragraph("4. STAFFING & TIMELINE REQUIREMENTS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("4.1 Staff Augmentation", subheading_style))
    staff_reqs = [
        "Require dedicated team of 8-10 engineers including architects, developers, and specialists",
        "Mix of senior full-stack developers (React, Node.js), DevOps engineers, and QA specialists",
        "Remote team preferred with timezone alignment (Americas, GMT-5 to GMT-8)",
        "Rapid onboarding within 2 weeks with knowledge transfer sessions",
        "Flexible engagement model with 6-12 months initial contract and extension options",
        "Pre-vetted senior engineers with 5+ years of relevant experience",
    ]
    for req in staff_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.2 Project Timeline", subheading_style))
    timeline = [
        "<b>Phase 1 (Weeks 1-8):</b> MVP Development with core features (shopping cart, checkout, payment)",
        "<b>Phase 2 (Weeks 9-16):</b> Full feature development (AI recommendations, analytics, mobile app)",
        "<b>Phase 3 (Weeks 17-20):</b> Testing and QA (automated tests, load testing, security testing)",
        "<b>Phase 4 (Weeks 21-24):</b> Deployment and launch (production rollout, monitoring setup)",
    ]
    for item in timeline:
        story.append(Paragraph(f"• {item}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.3 Post-Launch Support", subheading_style))
    support_reqs = [
        "24/7 application maintenance and support for 12 months post-launch",
        "SLA: 4-hour response time for critical issues, 24-hour for high priority, 48-hour for medium",
        "Monthly maintenance reports including performance metrics and incident summaries",
        "Performance monitoring and optimization with proactive issue detection",
        "Bug fixing and security patches with zero-downtime deployment procedures",
        "Feature enhancements and minor changes based on user feedback",
    ]
    for req in support_reqs:
        story.append(Paragraph(f"• {req}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Section 5: Deliverables
    story.append(Paragraph("5. DELIVERABLES", heading_style))
    story.append(Spacer(1, 0.1*inch))
    deliverables = [
        "Fully functional cloud-based e-commerce platform deployed on AWS",
        "Complete source code and comprehensive technical documentation",
        "CI/CD pipeline configuration with automated testing and deployment",
        "Test automation suite with 80%+ code coverage",
        "Security audit report and penetration testing results",
        "User training materials and administrator guides",
        "12 months of maintenance and support with 24/7 availability",
    ]
    for i, item in enumerate(deliverables, 1):
        story.append(Paragraph(f"{i}. {item}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Section 6: Evaluation Criteria
    story.append(Paragraph("6. EVALUATION CRITERIA", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Proposals will be evaluated based on:", body_style))
    criteria = [
        "<b>Technical Capability (30%)</b> - Expertise in required technologies and proven track record",
        "<b>Team Experience (25%)</b> - Similar project portfolio and relevant case studies",
        "<b>Cost (20%)</b> - Competitive pricing within budget with transparent cost breakdown",
        "<b>Timeline (15%)</b> - Ability to meet aggressive deadlines with milestone-based delivery",
        "<b>Quality & Testing (10%)</b> - Comprehensive QA approach and testing methodology",
    ]
    for item in criteria:
        story.append(Paragraph(f"• {item}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Section 7: Submission
    story.append(Paragraph("7. SUBMISSION REQUIREMENTS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Please submit the following documents:", body_style))
    submissions = [
        "Company profile and team qualifications with resumes of key personnel",
        "Detailed technical proposal addressing all requirements",
        "Project timeline and milestones with Gantt chart or roadmap",
        "Itemized cost breakdown including development, testing, and support costs",
        "References from similar projects (minimum 3 with contact information)",
        "Security and compliance certifications (SOC 2, ISO 27001, etc.)",
    ]
    for i, item in enumerate(submissions, 1):
        story.append(Paragraph(f"{i}. {item}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Contact
    story.append(Paragraph("<b>Contact:</b>", body_style))
    story.append(Paragraph("Sarah Johnson, Procurement Manager", body_style))
    story.append(Paragraph("TechRetail Inc.", body_style))
    story.append(Paragraph("Email: rfp@techretail.com", body_style))
    story.append(Paragraph("Phone: (555) 123-4567", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(
        "<i>This RFP is confidential and proprietary to TechRetail Inc. All rights reserved.</i>",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ PDF created: {output_path}")
    print(f"📄 File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"📊 This RFP contains requirements that should match:")
    print(f"   • Cloud Infrastructure & DevOps (90%+ match expected)")
    print(f"   • Custom Software Development (95%+ match expected)")
    print(f"   • AI & Machine Learning (85%+ match expected)")
    print(f"   • Data Analytics & BI (90%+ match expected)")
    print(f"   • UI/UX Design (85%+ match expected)")
    print(f"   • QA & Testing Services (90%+ match expected)")
    print(f"   • Security & Compliance (95%+ match expected)")
    print(f"   • Staff Augmentation (85%+ match expected)")
    print(f"   • Maintenance & Support (90%+ match expected)")
    print(f"   • MVP Development (70%+ match expected)")
    print(f"\n📝 Upload this RFP to test Service Matching feature!")


if __name__ == "__main__":
    create_sample_rfp_pdf()

