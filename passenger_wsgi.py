import os
import sys
import traceback

# 1. Add application directory to sys.path so 'myproject' and 'myapp' can be imported
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# 2. Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# 3. Load WSGI application with error diagnostics
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    error_traceback = traceback.format_exc()
    sys.stderr.write(error_traceback + "\n")

    def application(environ, start_response):
        status = '500 Internal Server Error'
        body = (
            "<!DOCTYPE html>"
            "<html><head><title>cPanel Startup Error</title></head>"
            "<body style='font-family: monospace; padding: 24px; background: #18181b; color: #f43f5e;'>"
            "<h2 style='color: #ef4444;'>Django Startup Error on cPanel</h2>"
            "<p style='color: #e4e4e7;'>The application failed to initialize before serving requests. Traceback:</p>"
            "<pre style='background: #27272a; color: #38bdf8; padding: 16px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; font-size: 14px;'>"
            f"{error_traceback}"
            "</pre></body></html>"
        ).encode('utf-8')
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(body)))
        ]
        start_response(status, response_headers)
        return [body]

