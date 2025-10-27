# Course Generator - Cost & Performance Analysis

## 💰 Current Cost Structure

### API Calls Per Course Generation

For a **comprehensive university-level course** (8 modules):

1. **Course Outline Generation**: 1 API call (~4000 tokens)
2. **Per Module** (8 modules):
   - Module overview: 1 call (~2000 tokens)
   - Per Lesson (4 lessons): 4 calls (~3000 tokens each)
   - Practical examples: 1 call (~2000 tokens)
   - Case studies: 1 call (~2000 tokens)
   - Assessment: 1 call (~2000 tokens)
   
**Total API Calls**: ~60-80 calls per comprehensive course

### Token Usage Estimate

- **Input tokens**: ~50,000-80,000 tokens
- **Output tokens**: ~100,000-150,000 tokens
- **Total**: ~150,000-230,000 tokens per course

### Cost with GitHub Models (gpt-4o-mini)

GitHub Models is **FREE** for rate-limited usage (tokens per minute/day caps).

**However**, if you exceed rate limits or use a paid API:
- gpt-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Estimated cost per course**: $0.01 - $0.15 (very affordable)

## ⏱️ Time Analysis

### Why It Takes So Long

1. **Sequential API Calls**: 60-80 calls done one after another
2. **Rate Limiting**: 1-second delays between calls to avoid hitting rate limits
3. **Token Processing**: Large prompts and responses take time

**Current Generation Time**: 
- Basic course (Wikipedia): ~30 seconds
- Enhanced course (multi-source): **2-5 minutes**

## 🚀 Optimization Options

### Option 1: Reduce Scope (Recommended for Testing)
**Quick implementation** - reduce the number of modules and lessons:

```python
# Instead of 8-12 modules → Use 3-5 modules
# Instead of 4 lessons per module → Use 2 lessons per module
```

**Impact**:
- ✅ Generation time: ~30-60 seconds
- ✅ Cost: ~70% reduction
- ⚠️ Less comprehensive content

### Option 2: Batch API Calls (Medium Effort)
Use async/parallel processing for independent calls:

```python
# Generate all module content in parallel
# Generate all lessons in a module simultaneously
```

**Impact**:
- ✅ Generation time: ~60-90 seconds (50% faster)
- ⚠️ Same cost, just faster
- ⚠️ May hit rate limits

### Option 3: Caching Strategy (Best Long-term)
Cache generated content and reuse:

```python
# Cache course outlines by topic
# Cache module content for common subjects
# Cache assessment templates
```

**Impact**:
- ✅ Subsequent generations: ~5-10 seconds
- ✅ Cost: ~90% reduction for repeated topics
- ✅ Consistent quality

### Option 4: Progressive Generation (User Experience)
Generate course outline first, then modules on-demand:

```python
# Step 1: Generate outline (5 seconds)
# Step 2: User selects which modules to expand
# Step 3: Generate only selected modules
```

**Impact**:
- ✅ Initial response: ~5 seconds
- ✅ User control over cost/detail
- ✅ Better UX with incremental loading

### Option 5: Template-Based Generation (Fastest)
Use pre-made templates with AI filling in specifics:

```python
# Use standard course structure templates
# AI only generates custom content for key sections
# Reduce API calls by 80%
```

**Impact**:
- ✅ Generation time: ~15-30 seconds
- ✅ Cost: ~80% reduction
- ⚠️ Less customization

## 📊 Recommended Strategy

### For Your Use Case

**Immediate (Now)**:
1. **Reduce scope**: 4 modules × 2 lessons = ~20 API calls
2. **Add loading indicators**: Show progress to users
3. **Add cost warnings**: Let users know comprehensive courses take time

**Short-term (This Week)**:
1. **Implement caching**: Store generated courses
2. **Add quick mode**: Lighter version for testing
3. **Progressive loading**: Generate outline first

**Long-term (Future)**:
1. **Async processing**: Background job queue
2. **Batch operations**: Parallel API calls
3. **Smart templates**: Reduce redundant generation

## 🎯 Quick Fix Implementation

Here's what I can implement RIGHT NOW to reduce cost and time:
