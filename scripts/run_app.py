#!/usr/bin/env python
"""
Utility script to run the Flask application with various configurations.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import create_app

def parse_args():
    parser = argparse.ArgumentParser(description='Run the Order Management API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes (production only)')
    parser.add_argument('--production', action='store_true', help='Run in production mode with Gunicorn')
    
    return parser.parse_args()


def run_development(args):
    """Run the app in development mode with Flask's built-in server."""
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=args.reload)


def run_production(args):
    """Run the app in production mode with Gunicorn."""
    try:
        import gunicorn.app.base
    except ImportError:
        print("Error: Gunicorn is not installed. Run 'pip install gunicorn' to install it.")
        sys.exit(1)
    
    class GunicornApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                if key in self.cfg.settings and value is not None:
                    self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    # Create the Flask app
    app = create_app()
    
    # Gunicorn options
    options = {
        'bind': f"{args.host}:{args.port}",
        'workers': args.workers,
        'worker_class': 'sync',
        'timeout': 120,
        'reload': args.reload,
        'accesslog': '-',
        'errorlog': '-',
    }

    # Run with Gunicorn
    GunicornApplication(app, options).run()


if __name__ == '__main__':
    args = parse_args()
    
    if args.production:
        print(f"Starting server in production mode on {args.host}:{args.port} with {args.workers} workers")
        run_production(args)
    else:
        print(f"Starting development server on {args.host}:{args.port}")
        run_development(args)