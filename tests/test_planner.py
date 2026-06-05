from cadence.planner import plan, render_plan


def test_splits_on_then():
    steps = plan("open settings, turn on airplane mode, then turn it back off")
    assert len(steps) == 2
    assert "airplane mode" in steps[0].goal
    assert steps[1].goal == "turn it back off"


def test_splits_numbered_list():
    steps = plan("1) clear notifications 2) open the calendar")
    assert [s.goal for s in steps] == ["clear notifications", "open the calendar"]


def test_single_goal_is_one_step():
    steps = plan("open the app and sign in")
    assert len(steps) == 1


def test_read_only_detection():
    steps = plan("open my orders and report the latest status")
    assert steps[0].read_only is True


def test_render_plan_numbers_steps():
    out = render_plan(plan("do a; do b"))
    assert "1." in out and "2." in out
    assert out.startswith("Plan:")
