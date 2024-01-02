#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

    if use_ptvsd():
        import ptvsd
        print('Waiting debugger to attach (port: 5000)...')
        ptvsd.enable_attach(address=('0.0.0.0', 5000))
        ptvsd.wait_for_attach()
        print('Attached debugger!')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def use_ptvsd():
    return os.environ.get('USE_PTVSD') == 'true'


if __name__ == '__main__':
    main()
