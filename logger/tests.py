import os
import tempfile
from logger import get_logger
from logger.formatters.color_formatter import RESET_SEQ


def test_console_logging(capsys):
    INFO_STRING = "info_test"
    DEBUG_STRING = "debug_test"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        file_name = f.name
    params = {"LOG_FILE_LOCATION": file_name}
    # Here comes the execution itself
    log = get_logger("", params)
    log.info(INFO_STRING)
    log.debug(DEBUG_STRING)

    # Capturing the standard output
    captured = capsys.readouterr()
    err = captured.err

    # Console part
    assert "INF" in err
    assert INFO_STRING in err, "logging doesn't work, mothing is written to stderr"
    assert RESET_SEQ in err, "color formatting not working"
    assert "DBG" not in err, "DEBUG is writen to console, despite default settings in logging.yaml"
    assert (
        DEBUG_STRING not in err
    ), "DEBUG message is written to console, despite default settings in logging.yaml"

    # File part
    with open(file_name) as f:
        s = f.read()
        assert INFO_STRING in s, "INFO not written to file"
        assert "DEBUG" in s, "DEBUG not written to file"
        assert DEBUG_STRING in s, "DEBUG message not written to file"
        assert len(s.split("\n")) == 3, "More lines in log file"
    os.remove(file_name)
