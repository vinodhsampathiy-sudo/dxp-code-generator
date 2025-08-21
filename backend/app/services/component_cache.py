from typing import Dict, Optional, List
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ComponentCache:
    def __init__(self):
        # Core caches
        self.pattern_cache: Dict[str, Dict] = {}
        self.dialog_cache: Dict[str, Dict] = {}
        self.clientlib_cache: Dict[str, Dict] = {}
        
        # New specialized caches
        self.responsive_patterns: Dict[str, Dict] = {}  # Cache for responsive layouts
        self.interactive_features: Dict[str, Dict] = {}  # Cache for JS interactions
        self.style_patterns: Dict[str, Dict] = {}  # Cache for common CSS patterns
        self.sling_patterns: Dict[str, Dict] = {}  # Cache for Sling Model patterns
        self.accessibility_patterns: Dict[str, Dict] = {}  # Cache for a11y features
        
        # Cache configuration
        self.cache_expiry = timedelta(hours=24)
        self.pattern_hit_count: Dict[str, int] = {}  # Track pattern usage
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'pattern_reuse': {}
        }

    def _generate_cache_key(self, features: Dict) -> str:
        """Generate a unique cache key based on component features"""
        feature_str = json.dumps(features, sort_keys=True)
        return hashlib.md5(feature_str.encode()).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if the cached item is still valid"""
        cache_time = datetime.fromtimestamp(timestamp)
        return datetime.now() - cache_time < self.cache_expiry

    def cache_pattern(self, pattern_type: str, features: Dict, pattern: Dict):
        """Cache a component pattern"""
        cache_key = self._generate_cache_key(features)
        self.pattern_cache[cache_key] = {
            'pattern': pattern,
            'type': pattern_type,
            'timestamp': time.time()
        }
        logger.info(f"Cached {pattern_type} pattern with key {cache_key}")

    def get_cached_pattern(self, pattern_type: str, features: Dict) -> Optional[Dict]:
        """Retrieve a cached pattern if it exists and is valid"""
        cache_key = self._generate_cache_key(features)
        cached_item = self.pattern_cache.get(cache_key)
        
        if cached_item and cached_item['type'] == pattern_type:
            if self._is_cache_valid(cached_item['timestamp']):
                logger.info(f"Cache hit for {pattern_type} pattern with key {cache_key}")
                return cached_item['pattern']
            else:
                # Remove expired cache entry
                del self.pattern_cache[cache_key]
        
        return None

    def cache_dialog(self, fields: List[Dict], dialog_xml: str):
        """Cache dialog XML for common field combinations"""
        cache_key = self._generate_cache_key({'fields': fields})
        self.dialog_cache[cache_key] = {
            'xml': dialog_xml,
            'timestamp': time.time()
        }

    def get_cached_dialog(self, fields: List[Dict]) -> Optional[str]:
        """Retrieve cached dialog XML if it exists"""
        cache_key = self._generate_cache_key({'fields': fields})
        cached_item = self.dialog_cache.get(cache_key)
        
        if cached_item and self._is_cache_valid(cached_item['timestamp']):
            return cached_item['xml']
        
        return None

    def cache_clientlib(self, features: Dict, clientlib: Dict):
        """Cache client library code for common feature sets"""
        cache_key = self._generate_cache_key(features)
        self.clientlib_cache[cache_key] = {
            'code': clientlib,
            'timestamp': time.time()
        }

    def get_cached_clientlib(self, features: Dict) -> Optional[Dict]:
        """Retrieve cached client library code if it exists"""
        cache_key = self._generate_cache_key(features)
        cached_item = self.clientlib_cache.get(cache_key)
        
        if cached_item and self._is_cache_valid(cached_item['timestamp']):
            return cached_item['code']
        
        return None

    def cache_responsive_pattern(self, breakpoints: List[str], css_pattern: str):
        """Cache responsive design patterns"""
        key = self._generate_cache_key({'breakpoints': sorted(breakpoints)})
        self.responsive_patterns[key] = {
            'css': css_pattern,
            'timestamp': time.time(),
            'breakpoints': breakpoints
        }
        self._update_pattern_stats(key, 'responsive')

    def get_responsive_pattern(self, breakpoints: List[str]) -> Optional[str]:
        """Get cached responsive pattern matching the breakpoints"""
        key = self._generate_cache_key({'breakpoints': sorted(breakpoints)})
        if key in self.responsive_patterns and self._is_cache_valid(self.responsive_patterns[key]['timestamp']):
            self.cache_stats['hits'] += 1
            return self.responsive_patterns[key]['css']
        self.cache_stats['misses'] += 1
        return None

    def cache_interactive_feature(self, feature_type: str, js_code: str, dependencies: List[str] = None):
        """Cache common JavaScript interaction patterns"""
        key = self._generate_cache_key({
            'type': feature_type,
            'deps': sorted(dependencies or [])
        })
        self.interactive_features[key] = {
            'code': js_code,
            'dependencies': dependencies or [],
            'timestamp': time.time()
        }
        self._update_pattern_stats(key, 'interactive')

    def get_interactive_feature(self, feature_type: str, dependencies: List[str] = None) -> Optional[Dict]:
        """Get cached interactive feature pattern"""
        key = self._generate_cache_key({
            'type': feature_type,
            'deps': sorted(dependencies or [])
        })
        if key in self.interactive_features and self._is_cache_valid(self.interactive_features[key]['timestamp']):
            self.cache_stats['hits'] += 1
            return self.interactive_features[key]
        self.cache_stats['misses'] += 1
        return None

    def cache_style_pattern(self, style_type: str, css_code: str, variants: List[str] = None):
        """Cache reusable CSS style patterns"""
        key = self._generate_cache_key({
            'type': style_type,
            'variants': sorted(variants or [])
        })
        self.style_patterns[key] = {
            'css': css_code,
            'variants': variants or [],
            'timestamp': time.time()
        }
        self._update_pattern_stats(key, 'style')

    def get_style_pattern(self, style_type: str, variants: List[str] = None) -> Optional[str]:
        """Get cached style pattern"""
        key = self._generate_cache_key({
            'type': style_type,
            'variants': sorted(variants or [])
        })
        if key in self.style_patterns and self._is_cache_valid(self.style_patterns[key]['timestamp']):
            self.cache_stats['hits'] += 1
            return self.style_patterns[key]['css']
        self.cache_stats['misses'] += 1
        return None

    def cache_sling_pattern(self, pattern_type: str, code: str, fields: List[Dict] = None):
        """Cache common Sling Model patterns"""
        key = self._generate_cache_key({
            'type': pattern_type,
            'fields': sorted(fields or [], key=lambda x: str(x))
        })
        self.sling_patterns[key] = {
            'code': code,
            'fields': fields or [],
            'timestamp': time.time()
        }
        self._update_pattern_stats(key, 'sling')

    def get_sling_pattern(self, pattern_type: str, fields: List[Dict] = None) -> Optional[str]:
        """Get cached Sling Model pattern"""
        key = self._generate_cache_key({
            'type': pattern_type,
            'fields': sorted(fields or [], key=lambda x: str(x))
        })
        if key in self.sling_patterns and self._is_cache_valid(self.sling_patterns[key]['timestamp']):
            self.cache_stats['hits'] += 1
            return self.sling_patterns[key]['code']
        self.cache_stats['misses'] += 1
        return None

    def cache_accessibility_pattern(self, element_type: str, a11y_code: str):
        """Cache accessibility patterns (ARIA attributes, keyboard interactions)"""
        key = self._generate_cache_key({'type': element_type})
        self.accessibility_patterns[key] = {
            'code': a11y_code,
            'timestamp': time.time()
        }
        self._update_pattern_stats(key, 'accessibility')

    def get_accessibility_pattern(self, element_type: str) -> Optional[str]:
        """Get cached accessibility pattern"""
        key = self._generate_cache_key({'type': element_type})
        if key in self.accessibility_patterns and self._is_cache_valid(self.accessibility_patterns[key]['timestamp']):
            self.cache_stats['hits'] += 1
            return self.accessibility_patterns[key]['code']
        self.cache_stats['misses'] += 1
        return None

    def _update_pattern_stats(self, key: str, pattern_type: str):
        """Update pattern usage statistics"""
        if key not in self.pattern_hit_count:
            self.pattern_hit_count[key] = 0
        self.pattern_hit_count[key] += 1
        
        if pattern_type not in self.cache_stats['pattern_reuse']:
            self.cache_stats['pattern_reuse'][pattern_type] = 0
        self.cache_stats['pattern_reuse'][pattern_type] += 1

    def get_cache_stats(self) -> Dict:
        """Get cache usage statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'pattern_reuse': self.cache_stats['pattern_reuse'],
            'most_used_patterns': sorted(
                self.pattern_hit_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    def clear_expired_cache(self):
        """Remove all expired cache entries"""
        current_time = time.time()
        caches = [
            (self.pattern_cache, 'patterns'),
            (self.dialog_cache, 'dialogs'),
            (self.clientlib_cache, 'clientlibs'),
            (self.responsive_patterns, 'responsive patterns'),
            (self.interactive_features, 'interactive features'),
            (self.style_patterns, 'style patterns'),
            (self.sling_patterns, 'sling patterns'),
            (self.accessibility_patterns, 'accessibility patterns')
        ]
        
        total_cleared = 0
        stats = {}
        
        for cache, name in caches:
            expired = [
                key for key, item in cache.items()
                if not self._is_cache_valid(item['timestamp'])
            ]
            for key in expired:
                del cache[key]
            stats[name] = len(expired)
            total_cleared += len(expired)
        
        logger.info(f"Cache cleanup: Cleared {total_cleared} total items - {json.dumps(stats)}")
