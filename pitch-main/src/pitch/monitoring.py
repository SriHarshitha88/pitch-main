from prometheus_client import Counter, Histogram, start_http_server
import time
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ANALYSIS_COUNT = Counter(
    'analysis_requests_total',
    'Total analysis requests',
    ['status']
)

ANALYSIS_LATENCY = Histogram(
    'analysis_duration_seconds',
    'Analysis processing time'
)

# Logging configuration
def setup_logging():
    """Setup logging configuration"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # Create handlers
    file_handler = RotatingFileHandler(
        f"{log_dir}/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger

# Initialize logger
logger = setup_logging()

# Metrics decorator
def track_metrics(endpoint: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                response = await func(*args, **kwargs)
                status = response.status_code if hasattr(response, 'status_code') else 200
                REQUEST_COUNT.labels(
                    method=kwargs.get('method', 'GET'),
                    endpoint=endpoint,
                    status=status
                ).inc()
                return response
            except Exception as e:
                REQUEST_COUNT.labels(
                    method=kwargs.get('method', 'GET'),
                    endpoint=endpoint,
                    status=500
                ).inc()
                raise e
            finally:
                REQUEST_LATENCY.labels(
                    method=kwargs.get('method', 'GET'),
                    endpoint=endpoint
                ).observe(time.time() - start_time)
        return wrapper
    return decorator

# Analysis tracking
def track_analysis():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                ANALYSIS_COUNT.labels(status='success').inc()
                return result
            except Exception as e:
                ANALYSIS_COUNT.labels(status='error').inc()
                raise e
            finally:
                ANALYSIS_LATENCY.observe(time.time() - start_time)
        return wrapper
    return decorator

# System health check
async def check_system_health():
    """Check system health and return status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "healthy",
            "cache": "healthy",
            "message_broker": "healthy",
            "vector_store": "healthy"
        }
    }
    
    # Add actual health checks here
    
    return health_status

# Start Prometheus metrics server
def start_metrics_server(port: int = 8000):
    """Start Prometheus metrics server"""
    start_http_server(port)
    logger.info(f"Metrics server started on port {port}") 