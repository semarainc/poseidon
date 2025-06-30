import os
import sys

def app_path(path):
    """
    Return the path of the application.

    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), path)