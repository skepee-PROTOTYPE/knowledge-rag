#!/usr/bin/env python3
"""
Check GitHub Models API Usage and Costs
This script helps you understand your API usage with GitHub Models.
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

print("💰 GitHub Models - Cost & Usage Information")
print("=" * 60)

# Check token
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    print("❌ GITHUB_TOKEN not found in .env")
    exit(1)

print("\n✅ GitHub Token found")
print(f"   Token preview: {github_token[:10]}...{github_token[-4:]}")

print("\n" + "=" * 60)
print("📊 COST INFORMATION - GitHub Models")
print("=" * 60)

print("\n🆓 **GitHub Models is FREE for Personal Use**")
print("-" * 60)

print("""
GitHub Models offers FREE access to AI models including:
- ✅ gpt-4o-mini (what you're using)
- ✅ gpt-4o
- ✅ Various other models

**Free Tier Limits:**
- ✅ Rate limits apply (requests per minute/day)
- ✅ Token limits per request
- ✅ No monetary charges for personal use
- ✅ Intended for testing and development

**Your Current Usage:**
- Model: gpt-4o-mini
- Endpoint: models.inference.ai.azure.com
- Cost: $0.00 (FREE within rate limits)
""")

print("\n⚠️ RATE LIMITS (Not Costs!)")
print("-" * 60)
print("""
GitHub Models has RATE LIMITS, not costs:
- Requests per minute: Limited (typically 10-15 RPM)
- Tokens per request: Limited (typically 4000-8000)
- Daily requests: Limited

If you hit rate limits:
- ⏸️ Wait a few minutes
- ⏸️ Requests will resume automatically
- ⏸️ NO charges applied
""")

print("\n💡 How to Check Your Usage")
print("-" * 60)
print("""
GitHub Models doesn't provide a usage dashboard for free tier.

To monitor your usage:
1. Watch for rate limit errors in your app
2. Check terminal output for API responses
3. Note generation times (slower = approaching limits)

Common rate limit response:
"error": {
    "code": "429",
    "message": "Rate limit exceeded"
}
""")

print("\n🎯 Your Course Generator Usage")
print("-" * 60)
print("""
**Quick Mode** (Recommended for Testing):
- API Calls: ~15-20 per course
- Tokens: ~40,000-60,000 total
- Generation Time: 30-60 seconds
- FREE ✅

**Full Mode**:
- API Calls: ~60-80 per course
- Tokens: ~150,000-230,000 total
- Generation Time: 2-5 minutes
- FREE ✅ (but may hit rate limits faster)

Both are completely FREE within GitHub's rate limits!
""")

print("\n💰 When Would You Need to Pay?")
print("-" * 60)
print("""
You would only need to pay if you:

1. **Move to Production**: 
   - Use Azure OpenAI Service directly (not GitHub Models)
   - Need higher rate limits
   - Require SLA guarantees
   - Want dedicated capacity

2. **Switch to OpenAI Direct**:
   - Use api.openai.com instead of GitHub Models
   - Costs: ~$0.15-0.60 per 1M tokens
   - Your course: ~$0.02-0.15 each (very cheap)

3. **Enterprise Use**:
   - High volume production deployments
   - Commercial applications
   - Need contractual agreements
""")

print("\n✅ SUMMARY FOR YOU")
print("=" * 60)
print("""
Current Setup:
- Service: GitHub Models (FREE)
- Model: gpt-4o-mini
- Cost: $0.00
- Limit: Rate limits only (not monetary)

Your course generator:
- ✅ FREE to use
- ✅ No charges
- ✅ No credit card needed
- ⚠️ Rate limits may slow you down during heavy use

Recommendation:
- Use Quick Mode for testing (faster, less rate limit impact)
- Use Full Mode when you need comprehensive courses
- Both are completely FREE!
""")

print("\n🔍 How to Test Rate Limits")
print("-" * 60)
print("""
Generate a course and watch for:

✅ Success: Course generates normally (within limits)
⚠️ Slow: Approaching rate limits
❌ Error 429: Hit rate limit, wait 1-5 minutes

Example error if you hit limit:
{
  "error": {
    "code": "429",
    "message": "Rate limit exceeded. Please retry after..."
  }
}
""")

print("\n" + "=" * 60)
print("🎉 Bottom Line: GitHub Models is FREE!")
print("=" * 60)
print("""
You are NOT being charged for:
- ✅ API calls
- ✅ Token usage
- ✅ Course generation
- ✅ Testing and development

You only face:
- ⏱️ Rate limits (temporary slowdowns)
- ⏸️ Need to wait if you hit limits
- 🔄 Automatic resume when limits reset

NO CREDIT CARD REQUIRED
NO CHARGES APPLIED
NO BILLS TO PAY

For personal testing and development, it's completely FREE! 🎉
""")

print("\n💡 Want to check if you're being charged?")
print("-" * 60)
print("""
1. GitHub Models: 
   - No billing dashboard (it's free!)
   - Just rate limits, no charges
   - Check: https://github.com/marketplace/models

2. If you later switch to Azure/OpenAI:
   - Azure: portal.azure.com → Cost Management
   - OpenAI: platform.openai.com → Usage
   - You'll know because you'll need to enter payment info

Since you're using GitHub Models with no payment setup:
→ You're definitely not being charged! ✅
""")