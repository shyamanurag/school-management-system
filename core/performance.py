"""
Production Performance Monitoring for School ERP System
"""
import time
import logging
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        initial_queries = len(connection.queries)
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            query_count = len(connection.queries) - initial_queries
            
            # Log performance metrics
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s with {query_count} queries")
            
            # Alert if performance is poor
            if execution_time > 5.0:
                logger.warning(f"SLOW FUNCTION: {func.__name__} took {execution_time:.2f}s")
            
            if query_count > 50:
                logger.warning(f"HIGH QUERY COUNT: {func.__name__} made {query_count} queries")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper

class PerformanceMetrics:
    """Collect and analyze performance metrics"""
    
    @staticmethod
    def get_database_stats():
        """Get database performance statistics"""
        with connection.cursor() as cursor:
            stats = {
                'total_queries': len(connection.queries),
                'connection_status': 'connected' if connection.connection else 'disconnected'
            }
            
            # SQLite specific stats
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                cursor.execute("PRAGMA database_list;")
                stats['databases'] = cursor.fetchall()
                
                cursor.execute("PRAGMA cache_size;")
                stats['cache_size'] = cursor.fetchone()[0]
            
            return stats
    
    @staticmethod
    def get_cache_stats():
        """Get cache performance statistics"""
        # Test cache performance
        start_time = time.time()
        cache.set('test_key', 'test_value', 60)
        cache_write_time = time.time() - start_time
        
        start_time = time.time()
        cache.get('test_key')
        cache_read_time = time.time() - start_time
        
        cache.delete('test_key')
        
        return {
            'cache_write_time': cache_write_time,
            'cache_read_time': cache_read_time,
            'cache_backend': settings.CACHES['default']['BACKEND']
        }
    
    @staticmethod
    def get_system_health():
        """Get overall system health metrics"""
        return {
            'database': PerformanceMetrics.get_database_stats(),
            'cache': PerformanceMetrics.get_cache_stats(),
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS
        }

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def analyze_slow_queries():
        """Analyze and log slow queries"""
        if settings.DEBUG:
            slow_queries = [q for q in connection.queries if float(q['time']) > 0.1]
            for query in slow_queries:
                logger.warning(f"SLOW QUERY ({query['time']}s): {query['sql'][:200]}...")
    
    @staticmethod
    def prefetch_related_data(queryset, *fields):
        """Optimize queryset with prefetch_related"""
        return queryset.prefetch_related(*fields)
    
    @staticmethod
    def select_related_data(queryset, *fields):
        """Optimize queryset with select_related"""
        return queryset.select_related(*fields)

class CacheManager:
    """Advanced cache management"""
    
    @staticmethod
    def cache_view_result(cache_key, timeout=300):
        """Decorator to cache view results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cached_result = cache.get(cache_key)
                if cached_result:
                    return cached_result
                
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_cache_pattern(pattern):
        """Invalidate cache keys matching pattern"""
        # This would need Redis for pattern-based deletion
        # For now, clear all cache
        cache.clear()
        logger.info(f"Cache invalidated for pattern: {pattern}")

class SecurityMonitor:
    """Security monitoring and alerting"""
    
    @staticmethod
    def log_security_event(event_type, user, details):
        """Log security events"""
        logger.warning(f"SECURITY EVENT: {event_type} - User: {user} - Details: {details}")
    
    @staticmethod
    def check_security_settings():
        """Check current security configuration"""
        security_issues = []
        
        if settings.DEBUG:
            security_issues.append("DEBUG mode is enabled")
        
        if 'django-insecure' in settings.SECRET_KEY:
            security_issues.append("Insecure SECRET_KEY detected")
        
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            security_issues.append("SSL redirect not enabled")
        
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            security_issues.append("Insecure session cookies")
        
        return security_issues

# Middleware for performance monitoring
class PerformanceMiddleware:
    """Middleware to monitor request performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        execution_time = time.time() - start_time
        query_count = len(connection.queries) - initial_queries
        
        # Log performance metrics
        logger.info(f"Request {request.path} took {execution_time:.2f}s with {query_count} queries")
        
        # Add performance headers for debugging
        if settings.DEBUG:
            response['X-Execution-Time'] = f"{execution_time:.2f}s"
            response['X-Query-Count'] = str(query_count)
        
        return response
