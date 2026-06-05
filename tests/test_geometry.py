from cadence.geometry import from_pixels, parse_resolution, to_pixels


def test_corners_and_center():
    assert to_pixels(0, 0, 1080, 2400) == (0, 0)
    assert to_pixels(1000, 1000, 1080, 2400) == (1079, 2399)   # clamped to last pixel
    assert to_pixels(500, 500, 1080, 2400) == (540, 1200)


def test_clamp_out_of_range():
    assert to_pixels(2000, -50, 1080, 2400) == (1079, 0)


def test_round_trip_is_close():
    for nx, ny in [(250, 250), (500, 750), (900, 100)]:
        px, py = to_pixels(nx, ny, 1080, 2400)
        rx, ry = from_pixels(px, py, 1080, 2400)
        assert abs(rx - nx) <= 1 and abs(ry - ny) <= 1


def test_parse_resolution():
    assert parse_resolution("1080x2400") == (1080, 2400)
    assert parse_resolution("720X1280") == (720, 1280)
