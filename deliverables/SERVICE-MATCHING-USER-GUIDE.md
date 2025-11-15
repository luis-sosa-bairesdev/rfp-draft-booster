# 🔗 Service Matching Feature - User Guide

## Overview

The Service Matching feature uses **TF-IDF (Term Frequency-Inverse Document Frequency)** and **cosine similarity** to automatically match RFP requirements to BairesDev's service catalog.

---

## 📊 How It Works

### Matching Algorithm

1. **Text Analysis**: Extracts keywords from requirement descriptions
2. **Vectorization**: Converts text to numerical vectors using TF-IDF
3. **Similarity Calculation**: Computes cosine similarity between requirements and services
4. **Score Assignment**: Assigns match score from 0% to 100%

### Score Interpretation

| Score | Color | Meaning | Action |
|-------|-------|---------|--------|
| **>80%** | 🟢 Green | **Strong Match** | Automatically approved for draft generation |
| **50-80%** | 🟡 Yellow | **Medium Match** | Review manually before approving |
| **<50%** | 🔴 Red | **Weak Match** | Likely not relevant, usually ignored |

---

## 🎯 Available Services (10 Total)

1. **Cloud Infrastructure & DevOps** (`technical`)
   - Keywords: AWS, Azure, GCP, Kubernetes, Docker, CI/CD, Terraform, DevOps, cloud, infrastructure

2. **Custom Software Development** (`functional`)
   - Keywords: React, Angular, Node.js, Python, Java, API, microservices, full-stack, web, mobile

3. **QA & Testing Services** (`compliance`)
   - Keywords: testing, QA, Selenium, Cypress, automation, performance, security testing, Playwright

4. **Data Analytics & Business Intelligence** (`functional`)
   - Keywords: data, analytics, BI, Tableau, Power BI, ETL, Snowflake, warehouse, SQL, reporting

5. **AI & Machine Learning Solutions** (`technical`)
   - Keywords: AI, ML, machine learning, NLP, computer vision, deep learning, TensorFlow, PyTorch

6. **Security Audit & Compliance** (`compliance`)
   - Keywords: security, compliance, GDPR, SOC 2, HIPAA, penetration testing, audit, vulnerability

7. **UI/UX Design & Prototyping** (`functional`)
   - Keywords: UI, UX, design, Figma, prototyping, accessibility, usability, user research

8. **Staff Augmentation & Dedicated Teams** (`timeline`)
   - Keywords: staffing, augmentation, hiring, dedicated teams, remote, onboarding, talent

9. **Application Maintenance & Support** (`timeline`)
   - Keywords: maintenance, support, 24/7, bug fixing, monitoring, SLA, hotfix, optimization

10. **MVP Development** (`budget`)
    - Keywords: MVP, rapid, startup, prototype, fast, fixed-price, scalable, launch

---

## 🚀 How to Use Service Matching

### Step 1: Upload RFP
1. Navigate to **📤 Upload RFP** page
2. Upload your RFP PDF
3. Provide RFP details (title, client, deadline)

### Step 2: Extract Requirements
1. Navigate to **📋 Requirements** page
2. Click **"Extract with AI"** (recommended) or **"Pattern Match"**
3. Wait for extraction to complete
4. Review and verify requirements

### Step 3: Run Service Matching
1. Navigate to **🔗 Service Matching** page
2. The page will automatically compute matches
3. Review the results table with match scores

### Step 4: Filter & Sort
- **Filter by Category**: Technical, Functional, Timeline, Budget, Compliance
- **Filter by Min Score**: Adjust slider to hide low-confidence matches (default: 50%)
- **Sort**: Highest/Lowest score first

### Step 5: Approve High-Confidence Matches
- **Manual Approval**: Click checkbox next to each match (>80% recommended)
- **Bulk Approval**: Click **"Approve All >80%"** button
- **Bulk Approval All**: Click **"Approve All Matches"** (use cautiously)

### Step 6: View Coverage & Export
- **Coverage Chart**: Shows match percentage by requirement category
- **Export Matches**: Download as JSON for reference

### Step 7: Generate Draft with Approved Matches
1. Navigate to **✍️ Draft Generation** page
2. Approved matches (>80%) are automatically included in the draft
3. The AI will reference these services in the proposal

---

## 📋 Best Practices

### For Better Matches:

✅ **DO:**
- Use **descriptive requirement descriptions** with technical keywords
- Include **technology names** (e.g., "AWS", "React", "Kubernetes")
- Mention **methodologies** (e.g., "agile", "CI/CD", "DevOps")
- Specify **deliverables** (e.g., "API", "dashboard", "mobile app")
- Include **compliance needs** (e.g., "GDPR", "SOC 2", "HIPAA")

❌ **DON'T:**
- Use vague descriptions like "Need software" or "Build system"
- Omit technical details
- Use acronyms without context (e.g., "CICD" instead of "CI/CD pipeline")
- Mix multiple requirements in one description

### Example: Good vs Bad Requirements

**❌ Bad Requirement:**
```
Category: Technical
Description: "Need cloud stuff"
Match Score: 20-30% (weak)
```

**✅ Good Requirement:**
```
Category: Technical
Description: "Deploy on AWS cloud infrastructure with Kubernetes orchestration, 
CI/CD pipelines using GitHub Actions, and Infrastructure as Code with Terraform"
Match Score: 95%+ (strong)
```

---

## 🧪 Testing Service Matching

### Use the Provided Sample RFP

We've created a sample RFP specifically designed to generate strong matches:

**File:** `data/sample_rfp_with_matching.pdf`

**What's Inside:**
- Cloud Infrastructure requirements (AWS, Kubernetes, CI/CD)
- Custom Software Development (React, Node.js, APIs)
- AI/ML requirements (NLP, recommendations, computer vision)
- Data Analytics (Tableau, ETL, Snowflake)
- UI/UX Design (Figma, accessibility, prototyping)
- QA/Testing (Selenium, Cypress, load testing)
- Security/Compliance (SOC 2, GDPR, pen testing)
- Staffing needs (dedicated teams, remote engineers)
- Maintenance & Support (24/7, SLA, monitoring)
- MVP Development (rapid prototyping, fixed-price)

**Expected Results:**
- **All 10 services** should have at least one match
- **80%+** of matches should be >50% confidence
- **50%+** of matches should be >80% confidence (auto-approved)

### Steps to Test:

1. **Upload** `data/sample_rfp_with_matching.pdf`
2. **Extract Requirements** using AI (should get 20-30 requirements)
3. **Navigate to Service Matching** page
4. **Verify** you see matches for all 10 service categories
5. **Approve** high-confidence matches (>80%)
6. **Generate Draft** and verify services are included

---

## 🐛 Troubleshooting

### "No matches found" or all scores < 50%

**Possible Causes:**
1. Requirements are too vague or generic
2. No technical keywords in descriptions
3. Requirements don't align with any BairesDev service

**Solutions:**
- ✅ Edit requirements to add more technical details
- ✅ Use specific technology names (AWS, React, etc.)
- ✅ Try the sample RFP (`sample_rfp_with_matching.pdf`)

### All matches have same score

**Cause:** Requirements are too similar or too generic

**Solution:**
- ✅ Ensure each requirement is distinct
- ✅ Add category-specific keywords

### Matches seem wrong

**Cause:** TF-IDF may match on common words, not domain-specific terms

**Solution:**
- ✅ Review the "Reasoning" column for each match
- ✅ Manually approve/reject matches
- ✅ Lower the minimum score threshold to see more options

---

## 📈 Understanding the Coverage Chart

The **Coverage by Category** bar chart shows:

- **X-axis**: Requirement categories (Technical, Functional, Timeline, Budget, Compliance)
- **Y-axis**: Average match percentage for that category
- **Subtitle**: Overall average match across all categories

**Interpretation:**
- **>70%**: Excellent coverage - most requirements have strong matches
- **50-70%**: Good coverage - some requirements match well
- **<50%**: Poor coverage - requirements may need more detail or services don't align

---

## 🔮 Future Enhancements (Post-MVP)

Planned improvements:
- **Semantic Matching**: Use Gemini embeddings for better understanding
- **Manual Service Addition**: Add custom services to the catalog
- **Weighted Matching**: Prioritize certain keywords over others
- **Historical Learning**: Improve matches based on past approvals
- **Hybrid Matching**: Combine TF-IDF with LLM-based reasoning

---

## 📞 Need Help?

- Use the **💬 AI Assistant** button (top-right of any page)
- Ask questions like:
  - "Why are my match scores low?"
  - "How do I improve service matching?"
  - "Which services match my requirements?"

---

**Last Updated:** January 15, 2025  
**Version:** 1.0

