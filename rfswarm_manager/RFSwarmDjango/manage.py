#!/usr/bin/env python
"""Django's command-line utility.

Please don't use this for anything other than managing your Django project.
"""

import os
import signal
import sys

def handle_shutdown(signum, frame):
    print("\n🛑 Shutdown signal received, cleaning up...")
    # Add your custom cleanup code here (closing connections, saving state)
    sys.exit(0)

def main():
    """Run all management commands."""
    # This ensures that Django knows where to find your settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RFSwarmDjango.django_project.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # This is likely because you're running this script without having installed
        # django. Please install it first.
        # If you're trying to run a Django project, please ensure you're in the
        # directory that contains manage.py
        raise ImportError(
            "Please install Django to run this script. "
            "If you're trying to run a Django project, please ensure you're in the "
            "directory that contains manage.py."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()


# Register the handler for SIGTERM (and optionally SIGINT)
signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
