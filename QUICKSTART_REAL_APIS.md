# 🚀 Quick Start Guide - Real API Integration

## Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test APIs
```bash
# Test all educational APIs
python educational_apis.py

# Expected output:
# ✅ mit_ocw: Working
# ✅ arxiv: Working
# ✅ khan_academy: Working
# ✅ coursera: Working
# ✅ stanford_encyclopedia: Working
```

### Step 3: Generate a Course!
```bash
# Start the web app
python app.py

# Visit: http://localhost:5000/enhanced-course
# Enter a topic: "Machine Learning"
# Click "Generate Course"
```

## ✅ What You Get

Your generated course will include content from **6 real educational sources**:

1. **MIT OpenCourseWare** (0.95 credibility)
   - Real MIT course links
   - Example: 6.867 Machine Learning

2. **arXiv** (0.85 credibility)
   - Real research papers
   - Latest academic work

3. **Coursera** (0.85 credibility)
   - Real course links
   - Example: Andrew Ng's ML course

4. **Stanford Encyclopedia** (0.9 credibility)
   - Real article links
   - Philosophical content

5. **Khan Academy** (0.8 credibility)
   - Real resource links
   - Interactive lessons

6. **Wikipedia** (0.7 credibility)
   - Real articles
   - Background information

## 🎯 Quick Mode vs Full Mode

### Quick Mode (Recommended for Speed)
```
✅ 3 modules
✅ 2 lessons per module
✅ ~15 API calls
⏱️ 30-60 seconds
💰 FREE
```

### Full Mode (Recommended for Depth)
```
✅ 8-12 modules
✅ 10 lessons per module
✅ ~60 API calls
⏱️ 2-5 minutes
💰 FREE
```

## 💡 Example: Generate "Data Science" Course

```bash
# Quick test
python test_comprehensive.py
```

Output:
```
✅ Found 5 sources from multiple providers:

ACADEMIC:
  • 15.071 The Analytics Edge (MIT)
    https://ocw.mit.edu/courses/15-071-...

EDUCATIONAL:
  • Data Science Specialization (Coursera)
    https://www.coursera.org/specializations/jhu-data-science
  • Khan Academy: data science
    https://www.khanacademy.org/search?...

RESEARCH:
  • A framework for understanding data science (arXiv)
  • Defining Data Science (arXiv)

Average Credibility: 0.86/1.0
Cost: $0.00 (FREE)
```

## 🔍 Verify Sources Are Real

All URLs are clickable and lead to real educational content:

### MIT OpenCourseWare
https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/

### Coursera
https://www.coursera.org/learn/machine-learning

### Khan Academy
https://www.khanacademy.org/math/calculus-1

### arXiv
http://arxiv.org/abs/1909.03550

All verified and working! ✅

## 📚 Documentation

- **REAL_API_GUIDE.md** - Complete API documentation
- **CONTENT_SOURCES_EXPLAINED.md** - Where content comes from
- **VISUAL_SUMMARY.md** - Visual diagrams and flowcharts
- **IMPLEMENTATION_SUMMARY.md** - Technical details

## 🎉 You're Ready!

The system is fully functional with real API integrations. Generate your first course now:

```bash
python app.py
```

Then visit: http://localhost:5000/enhanced-course

**Enjoy creating university-level courses with real educational sources!** 🚀

---

## 🆘 Troubleshooting

### Issue: "GITHUB_TOKEN not found"
**Solution**: Make sure `.env` file exists with your GitHub token:
```bash
GITHUB_TOKEN=your_github_token_here
```

### Issue: "API test fails"
**Solution**: Check internet connection, APIs require network access

### Issue: "Slow generation"
**Solution**: Use Quick Mode for faster results (check the Quick Mode box)

### Issue: "Need more sources"
**Solution**: Uncheck Quick Mode for more comprehensive results

---

## 💬 Need Help?

Run the test suite:
```bash
python educational_apis.py        # Test APIs
python test_real_apis.py          # Test integration
python test_comprehensive.py      # Full test
```

All tests should show ✅ Working!
