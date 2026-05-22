import logging
import sys

def setup_logging(log_filename: str):
    """
    Configures global logging: INFO to stdout, ERROR to a specified file.
    The log file is overwritten entirely on each execution.
    """
    if not log_filename.endswith(".log"):
        log_filename += ".log"
    root_logger = logging.getLogger()
    
    # Evita di duplicare gli handler se la funzione viene chiamata più volte
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.setLevel(logging.INFO)

    # Handler for errors (Aggiunto mode='w' per forzare la sovrascrittura)
    error_handler = logging.FileHandler(log_filename, mode='w')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))

    # Handler for standard output (terminal)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

    root_logger.addHandler(error_handler)
    root_logger.addHandler(stdout_handler)