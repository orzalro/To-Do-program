import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from src import util
from src.dialog import AddTodoDialog


class FakeValue:
    def __init__(self, value):
        self.value = value

    def text(self):
        return str(self.value)


class FakeCycleTime:
    def __init__(self, value):
        self.value = value

    def time(self):
        return self

    def toPyTime(self):
        return self.value


class FakeTodoList:
    def __init__(self, payload):
        self.payload = payload
        self.update_count = 0

    def count(self):
        return 1

    def item(self, index):
        return index

    def get_todo_payload(self, item):
        return dict(self.payload)

    def update_param(self, item, method, reset_time, param0, param1, checked):
        self.payload.update({
            "checked": checked,
            "reset_method": method,
            "reset_time": reset_time,
            "resetparam0": param0,
            "resetparam1": param1,
        })
        self.update_count += 1


class FakeApp:
    def __init__(self, payload):
        self.grid_row = 1
        self.grid_col = 1
        self.lastchecktime = "2026-08-15 08:00:00"
        self.todo_list = {"list0": FakeTodoList(payload)}


class ResetRuleTests(unittest.TestCase):
    def test_daily_reset_accepts_a_fixed_evaluation_time(self):
        checked, base = util.reset_check(
            1,
            "2026-08-15 08:00:00",
            0,
            540,
            -1,
            -1,
            now=datetime(2026, 8, 16, 10, 0, 0),
        )
        self.assertEqual(checked, 0)
        self.assertEqual(base, -1)

    def test_cycle_reset_reports_the_advanced_base(self):
        checked, base = util.reset_check(
            1,
            "2026-08-16 08:00:00",
            3,
            -1,
            60,
            "2026-08-16 08:00:00",
            now=datetime(2026, 8, 16, 10, 30, 0),
        )
        self.assertEqual(checked, 0)
        self.assertEqual(base, "2026-08-16 10:00:00")

    def test_cycle_reset_keeps_the_next_reset_strictly_in_the_future(self):
        now = datetime(2026, 8, 16, 9, 0, 0)

        _, base = util.cycle_reset(
            60,
            "2026-08-16 08:00:00",
            now=now,
        )

        next_reset = datetime.strptime(base, "%Y-%m-%d %H:%M:%S") + timedelta(
            minutes=60
        )
        self.assertGreater(next_reset, now)

    def test_new_cycle_todo_normalizes_a_past_base_before_display(self):
        now = datetime.now().replace(second=0, microsecond=0)
        past_base = now - timedelta(minutes=5)
        dialog = SimpleNamespace(
            stacked_widget=SimpleNamespace(currentIndex=lambda: 3),
            cycle_reset_time=FakeCycleTime(past_base.time()),
            cycle_resetparam1=FakeValue(
                f"기준 날짜: {past_base.strftime('%Y-%m-%d')}"
            ),
            cycle_resetparam0_day=FakeValue(0),
            cycle_resetparam0_hour=FakeValue(0),
            cycle_resetparam0_minute=FakeValue(2),
        )

        _, _, reset_period, normalized_base = AddTodoDialog.get_data(dialog)

        next_reset = datetime.strptime(
            normalized_base, "%Y-%m-%d %H:%M:%S"
        ) + timedelta(minutes=reset_period)
        self.assertGreater(next_reset, datetime.now())

    def test_apply_due_resets_updates_state_without_saving_data(self):
        app = FakeApp({
            "title": "일간 일정",
            "checked": 1,
            "reset_method": 0,
            "reset_time": 540,
            "resetparam0": -1,
            "resetparam1": -1,
        })

        def update_config(target, section, key, value):
            setattr(target, key, value)

        with (
            patch("src.config.update_config", side_effect=update_config),
            patch("src.util.safe_write_text") as write_text,
        ):
            changed = util.apply_due_resets(
                app,
                evaluated_at=datetime(2026, 8, 16, 10, 0, 0),
            )

        self.assertTrue(changed)
        self.assertEqual(app.todo_list["list0"].payload["checked"], 0)
        self.assertEqual(app.todo_list["list0"].update_count, 1)
        self.assertEqual(app.lastchecktime, "2026-08-16 10:00:00")
        write_text.assert_not_called()

    def test_save_data_does_not_evaluate_resets(self):
        app = FakeApp({
            "title": "저장 테스트",
            "checked": 1,
            "reset_method": 0,
            "reset_time": 540,
            "resetparam0": -1,
            "resetparam1": -1,
        })

        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = os.path.join(temp_dir, "userdata.json")
            with patch.object(util, "DATA_FILE_PATH", data_path):
                util.save_data(app)
            with open(data_path, "r", encoding="utf-8") as data_file:
                saved = json.loads(data_file.readline())

        self.assertEqual(app.todo_list["list0"].payload["checked"], 1)
        self.assertEqual(app.todo_list["list0"].update_count, 0)
        self.assertEqual(saved[3], 1)


if __name__ == "__main__":
    unittest.main()
