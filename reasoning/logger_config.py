import logging


def setup_logger(log_file="error.log"):
    # Open the log file in write mode to clear its contents
    with open(log_file, "w"):
        pass  # This creates the file if it doesn't exist and clears it if it does

    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
