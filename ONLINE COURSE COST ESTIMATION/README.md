# 📚 Online Course Cost Estimation (Internship Project)

A data-driven approach to pricing online courses: survey design → analysis
→ price-tier clustering → audience-specific dashboards. Built during my
Data Science & ML internship at Kites Software Pvt Ltd.

## Approach
1. **Survey design & collection** — structured survey of **200
   respondents** (students and working professionals) on the factors that
   influence what they'd pay for a course: duration, certification,
   content quality, platform, and learning preferences.
2. **Cleaning & EDA** — Python (Pandas/NumPy): missing-value handling,
   feature analysis, and relationship exploration between course
   attributes and price willingness.
3. **Price-tier segmentation** — **K-Means clustering (k=3)** with
   scikit-learn to group courses into low / mid / premium price tiers;
   clusters visualized and exported as labeled data for reporting.
4. **Dashboards** — three audience-specific **Power BI dashboards**:
   - **Student Dashboard** — learner preferences and expectations
   - **Professional Dashboard** — industry-oriented needs
   - **Common Dashboard** — overall trends and comparison (learning time,
     device usage, learning barriers, engagement preferences,
     effectiveness scores)

## Key findings
- Students and professionals differ measurably in engagement preferences
  and content-format choices — one price does not fit both segments
- Course duration and certification emerged as leading pricing factors
- Learning-barrier analysis (course length, difficulty concentrating,
  lack of guidance) informed content-strategy recommendations

## Tools
Python (Pandas, NumPy, Matplotlib) · scikit-learn (K-Means) ·
Power BI · Survey design & analysis
