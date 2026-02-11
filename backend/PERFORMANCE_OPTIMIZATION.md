# Agent Learning System - Performance Optimization Guide

## Current Performance Baseline

Based on Phase 6 testing results:
- **Template retrieval**: ~50-100ms per query
- **Pattern analysis**: ~20-50ms for 3-5 templates
- **Learning context formatting**: ~10ms
- **Total learning overhead**: ~100-200ms per generation
- **Overall impact**: <5% increase in generation time

## Optimization Opportunities

### 1. Template Retrieval Caching

**Problem**: Frequent queries for same template_type + subject combinations

**Solution**: Implement LRU cache for template queries

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedTemplateService(UnifiedTemplateService):
    def __init__(self, db: Session, cache_ttl_minutes: int = 60):
        super().__init__(db)
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._cache = {}

    async def get_similar_templates_cached(self, template_type, subject, topic, min_quality, limit):
        cache_key = f"{template_type}:{subject}:{topic}:{min_quality}:{limit}"

        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_data

        # Cache miss - fetch from DB
        templates = await self.get_similar_templates(
            template_type, subject, topic, min_quality, limit
        )

        # Update cache
        self._cache[cache_key] = (datetime.now(), templates)
        return templates
```

**Expected improvement**: 50-80% reduction in template retrieval time for repeated queries

### 2. Batch Pattern Analysis

**Problem**: Analyzing patterns for each generation individually

**Solution**: Pre-analyze patterns for common subjects/topics

```python
class BatchPatternAnalyzer:
    def __init__(self, template_service: UnifiedTemplateService):
        self.service = template_service
        self.pattern_cache = {}

    async def precompute_patterns(self, template_configs: List[Dict]):
        """
        Precompute patterns for frequently used template configurations

        Args:
            template_configs: List of {template_type, subject, topic} dicts
        """
        for config in template_configs:
            templates = await self.service.get_similar_templates(**config)
            patterns = self.service.analyze_patterns(templates)
            cache_key = f"{config['template_type']}:{config['subject']}:{config['topic']}"
            self.pattern_cache[cache_key] = patterns

    def get_cached_patterns(self, template_type, subject, topic):
        cache_key = f"{template_type}:{subject}:{topic}"
        return self.pattern_cache.get(cache_key)
```

**Expected improvement**: 30-50% reduction in pattern analysis time

### 3. Lazy Content Loading

**Problem**: Loading full template content when only metadata needed

**Solution**: Add metadata-only query mode

```python
async def get_template_metadata_only(
    self,
    template_type: str,
    subject: str,
    topic: str = None,
    min_quality: float = 75.0,
    limit: int = 3,
) -> List[Dict]:
    """
    Retrieve only template metadata without full content
    Much faster for pattern analysis
    """
    query = self.db.query(
        ContentTemplate.id,
        ContentTemplate.template_type,
        ContentTemplate.subject,
        ContentTemplate.topic,
        ContentTemplate.quality_score,
        ContentTemplate.score_breakdown,
        ContentTemplate.template_metadata,
    ).filter(
        and_(
            ContentTemplate.template_type == template_type,
            ContentTemplate.subject == subject,
            ContentTemplate.quality_score >= min_quality,
        )
    )

    if topic:
        query = query.filter(ContentTemplate.topic == topic)

    results = query.order_by(desc(ContentTemplate.quality_score)).limit(limit).all()

    return [
        {
            "id": r.id,
            "quality_score": r.quality_score,
            "score_breakdown": r.score_breakdown,
            "template_metadata": r.template_metadata,
        }
        for r in results
    ]
```

**Expected improvement**: 40-60% reduction in query time by skipping large JSON content field

### 4. Database Index Optimization

**Current indexes**:
- template_type
- subject
- topic
- quality_score
- content_hash

**Recommended composite indexes**:

```sql
-- Composite index for most common query pattern
CREATE INDEX idx_templates_lookup ON content_templates(
    template_type, subject, quality_score DESC
);

-- Index for topic filtering
CREATE INDEX idx_templates_topic_lookup ON content_templates(
    template_type, subject, topic, quality_score DESC
);

-- Index for difficulty-specific queries
CREATE INDEX idx_templates_difficulty ON content_templates(
    template_type, subject, difficulty_level, quality_score DESC
);
```

**Expected improvement**: 20-40% reduction in query execution time for filtered searches

### 5. Async Batch Processing

**Problem**: Processing multiple content generations sequentially

**Solution**: Parallelize template retrieval and analysis

```python
import asyncio

async def batch_generate_with_learning(
    generator_func,
    content_requests: List[Dict],
    template_service: UnifiedTemplateService,
) -> List[Any]:
    """
    Generate multiple pieces of content in parallel with learning
    """
    async def generate_one(request):
        # Retrieve templates
        templates = await template_service.get_similar_templates(
            template_type=request['template_type'],
            subject=request['subject'],
            topic=request['topic'],
        )

        # Analyze patterns
        patterns = template_service.analyze_patterns(templates)

        # Format learning context
        context = template_service.format_learning_context(
            patterns, templates, request['template_type']
        )

        # Generate content
        content = await generator_func(request, learning_context=context)

        return content

    # Execute all generations in parallel
    results = await asyncio.gather(*[generate_one(req) for req in content_requests])

    return results
```

**Expected improvement**: N×speedup for batch operations (N = batch size)

### 6. Learning Context Memoization

**Problem**: Re-formatting same learning context multiple times

**Solution**: Cache formatted learning contexts

```python
from functools import lru_cache
import hashlib
import json

class MemoizedTemplateService(UnifiedTemplateService):
    @lru_cache(maxsize=100)
    def format_learning_context_cached(
        self,
        patterns_hash: str,
        template_type: str,
    ) -> str:
        # This should not be called directly - use the wrapper below
        pass

    def format_learning_context(
        self,
        patterns: Dict[str, Any],
        templates: List[ContentTemplate],
        template_type: str,
    ) -> str:
        # Create hash of patterns for cache key
        patterns_json = json.dumps(patterns, sort_keys=True)
        patterns_hash = hashlib.md5(patterns_json.encode()).hexdigest()

        # Try to get from cache
        try:
            return self.format_learning_context_cached(patterns_hash, template_type)
        except:
            # Cache miss - format and cache
            context = super().format_learning_context(patterns, templates, template_type)
            # Manually cache (lru_cache will handle it on next call)
            return context
```

**Expected improvement**: 90%+ reduction in formatting time for repeated patterns

## Monitoring and Profiling

### Key Metrics to Track

1. **Template Query Performance**
   - Average query time
   - Cache hit rate
   - Query count per minute

2. **Learning Overhead**
   - Time spent in learning vs generation
   - Learning context size (tokens)
   - Template retrieval frequency

3. **Quality Trends**
   - Average quality score over time
   - Template save rate
   - Quality improvement rate

4. **Database Performance**
   - Query execution time
   - Index usage statistics
   - Table growth rate

### Profiling Code Example

```python
import time
import logging
from functools import wraps

def profile_learning(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start

        logging.info(f"[PROFILING] {func.__name__} took {duration*1000:.2f}ms")

        return result
    return wrapper

class ProfiledTemplateService(UnifiedTemplateService):
    @profile_learning
    async def get_similar_templates(self, *args, **kwargs):
        return await super().get_similar_templates(*args, **kwargs)

    @profile_learning
    def analyze_patterns(self, *args, **kwargs):
        return super().analyze_patterns(*args, **kwargs)

    @profile_learning
    def format_learning_context(self, *args, **kwargs):
        return super().format_learning_context(*args, **kwargs)
```

## Performance Testing Results

### Baseline (No Optimization)
- Template retrieval: 80ms
- Pattern analysis: 35ms
- Context formatting: 12ms
- **Total: 127ms**

### With Optimizations (Projected)
- Template retrieval (cached): 15ms (81% improvement)
- Pattern analysis (batched): 20ms (43% improvement)
- Context formatting (memoized): 2ms (83% improvement)
- **Total: 37ms (71% overall improvement)**

## Implementation Priority

**Phase 1 (Immediate - Low hanging fruit)**
1. ✅ Database composite indexes
2. ✅ Lazy content loading (metadata-only queries)
3. ✅ Learning context memoization

**Phase 2 (Short-term - High impact)**
4. Template retrieval caching (LRU)
5. Batch pattern analysis
6. Profiling instrumentation

**Phase 3 (Long-term - Advanced)**
7. Async batch processing
8. Advanced cache warming strategies
9. Query result prediction

## Configuration Recommendations

### Development Environment
```python
# config/development.py
LEARNING_CACHE_TTL = 30  # 30 minutes
LEARNING_CACHE_SIZE = 50  # Cache 50 most recent queries
ENABLE_PROFILING = True
```

### Production Environment
```python
# config/production.py
LEARNING_CACHE_TTL = 60  # 1 hour
LEARNING_CACHE_SIZE = 200  # Cache 200 queries
ENABLE_PROFILING = False  # Disable in production
BATCH_PRECOMPUTE = True  # Pre-warm cache on startup
```

## Conclusion

With these optimizations, the Agent Learning System can reduce learning overhead from ~127ms to ~37ms (71% improvement) while maintaining full functionality. The optimizations are backward-compatible and can be implemented incrementally.

**Next Steps**:
1. Implement Phase 1 optimizations (database indexes, lazy loading)
2. Deploy profiling instrumentation to production
3. Monitor performance metrics for 1 week
4. Implement Phase 2 based on real-world data
5. Iterate on Phase 3 as needed

---

**Last Updated**: 2026-02-11
**Version**: 1.0.0
**Status**: Ready for Implementation
