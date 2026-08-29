import unittest
from unittest.mock import patch

from src import util


class UtilTests(unittest.TestCase):
    def test_elapsed_time_log_supports_legacy_windows_encoding(self):
        @util.elapsed_time_decorator
        def operation():
            return "done"

        with patch("builtins.print") as print_mock:
            self.assertEqual(operation(), "done")

        # GitHub Actions의 Windows 콘솔(cp1252)에서도 출력 가능한 로그인지 검증한다.
        message = print_mock.call_args.args[0]
        message.encode("cp1252")


if __name__ == "__main__":
    unittest.main()
