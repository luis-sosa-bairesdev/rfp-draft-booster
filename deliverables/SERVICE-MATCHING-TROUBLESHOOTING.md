# 🔧 Service Matching Troubleshooting Guide

## Problem: Low Match Count (1 match from 36 requirements)

### Root Cause

Your RFP extraction generated:
- ✅ **36 requirements** (excellent)
- ❌ **Only 1 match** (58%) to "QA & Testing Services"

**Why so few matches?**

1. **Requirements are mis-categorized by AI**
   - Example: "QA Testing requirements" → categorized as **Technical**
   - Service "QA & Testing" → category is **Compliance**
   - ❌ No category match = no bonus = lower score

2. **Minimum score threshold is 50%**
   - UI filters out matches < 50%
   - Most matches are 40-60% range (just below threshold)

3. **Only top 3 matches per requirement**
   - Default `top_n=3` limits results
   - With 36 requirements × 3 matches = max 108 potential matches
   - But filtering reduces it to 1

---

## 🎯 Solution 1: Lower the Minimum Match % Threshold

**In the Service Matching page UI**, adjust the slider:

```
Current: 50% minimum
Try: 30% or 40%
```

This will show more matches, including moderate-confidence ones.

---

## 🎯 Solution 2: Increase Matches Per Requirement

Edit `pages/3_🔗_Service_Matching.py`:

```python
# Find this line (around line 81-90):
matches = matcher.match_all_requirements(
    requirements=requirements,
    top_n=3,  # ← Change this to 5 or 10
    min_score=min_match_score
)
```

Change `top_n=3` to `top_n=5` to get more matches per requirement.

---

## 🎯 Solution 3: Fix AI Categorization (Best Long-Term Fix)

The AI is miscategorizing requirements. Examples:

| Requirement | Current Category | Should Be |
|-------------|-----------------|-----------|
| "Automated testing with Selenium..." | Technical | **Compliance** |
| "Security audits and pen testing..." | Technical | **Compliance** |
| "Staff augmentation 8-10 engineers..." | Functional | **Timeline** |

**Temporary workaround:**
1. Go to **📋 Requirements** page
2. Manually edit requirement categories
3. Change "Technical" → "Compliance" for QA/testing/security requirements
4. Re-run Service Matching

**Permanent fix:**
- Improve the AI extraction prompt to better categorize
- This is a known issue we'll fix in Epic 10

---

## 🎯 Solution 4: Understand Match Scores

Current algorithm scores are conservative:

| Score | Interpretation |
|-------|---------------|
| **70%+** | Excellent match - highly relevant |
| **50-70%** | Good match - relevant with some overlap |
| **30-50%** | Moderate match - some relevance |
| **<30%** | Weak match - likely not relevant |

**Recommendation:**
- **Auto-approve:** 70%+ (not 80%)
- **Review manually:** 50-70%
- **Ignore:** <50%

---

## 🔍 Debug: Check Your Current Matches

Run this diagnostic to see all potential matches:

```bash
cd /Users/luisfelipesosa/git/rfp-draft-booster
source venv/bin/activate
python3 scripts/diagnose_matching.py
```

This will show:
- All 10 services
- Sample requirements with different description styles
- Match scores and reasoning

---

## 📊 Expected Results with `sample_rfp_with_matching.pdf`

If you use the sample RFP provided (`data/sample_rfp_with_matching.pdf`):

**Expected:**
- 25-30 requirements extracted
- 60-100 service matches total
- 10-20 matches >70%
- 5-10 matches >80%

**If you see fewer:**
1. Check requirement descriptions are detailed
2. Lower min_score threshold to 30-40%
3. Verify services.json loaded correctly
4. Run diagnostic script

---

## 🚀 Quick Fix Summary

**Immediate actions:**

1. **In Service Matching page UI:**
   - Lower "Minimum Match %" slider to 30-40%
   - This should show 10-30 matches

2. **Review and approve matches manually:**
   - Any match >60% is worth reviewing
   - Check the "Reasoning" column for keywords

3. **Edit mis-categorized requirements:**
   - Go to Requirements page
   - Fix categories for QA/security/staffing requirements
   - Re-run matching

**Expected improvement:**
- From: 1 match (58%)
- To: 15-30 matches (40-80% range)

---

## 🐛 Still Having Issues?

1. **Export your requirements to JSON:**
   - Go to Requirements page
   - Click "Export Requirements" → JSON
   - Share the first 3 requirements (check description length and keywords)

2. **Check logs:**
   ```bash
   tail -f logs/app.log | grep "ServiceMatcher"
   ```

3. **Verify services loaded:**
   - Should see message: "ServiceMatcher initialized with 10 services"
   - If you see "0 services", there's a JSON loading issue

---

## 📈 Future Improvements (Post-MVP)

Planned enhancements:
1. **Semantic matching with Gemini embeddings** (Epic 11)
   - Will understand context, not just keywords
   - Expected improvement: 80-95% scores for good matches

2. **Better AI categorization** (Epic 10)
   - Improve requirement extraction prompt
   - Add category validation

3. **Custom service catalog** (Epic 12)
   - Add your own services
   - Edit existing service descriptions/tags

4. **Historical learning** (Epic 13)
   - Learn from manual approvals
   - Improve matching over time

---

**Last Updated:** January 15, 2025  
**Version:** 1.1

