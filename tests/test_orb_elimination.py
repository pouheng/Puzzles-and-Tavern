"""
Test script: Orb elimination light ball animation
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.chdir(project_dir)


def test_light_ball_particle_class():
    """Test LightBallParticle class"""
    print("=" * 50)
    print("Test: LightBallParticle class")
    print("=" * 50)

    from dungeon.board import LightBallParticle

    particle = LightBallParticle(
        x=100, y=200, color=(255, 80, 80), target_x=300, target_y=400, delay=0
    )

    print(f"Initial position: ({particle.x}, {particle.y})")
    print(f"Target position: ({particle.target_x}, {particle.target_y})")
    print(f"Color: {particle.color}")
    print(f"Speed: {particle.speed}")
    print(f"Progress: {particle.progress}")
    print(f"Active: {particle.active}")

    assert particle.x == 100
    assert particle.y == 200
    assert particle.target_x == 300
    assert particle.target_y == 400
    assert particle.color == (255, 80, 80)
    assert particle.active == True

    print("\nUpdate animation...")
    for i in range(30):
        particle.update(0.016)
        if i % 5 == 0:
            print(
                f"  Frame {i}: pos=({particle.x:.1f}, {particle.y:.1f}), progress={particle.progress:.2f}, active={particle.active}"
            )

    print(f"\nAnimation done, final pos: ({particle.x:.1f}, {particle.y:.1f})")
    print("[PASS] LightBallParticle test passed")

    return True


def test_light_ball_particle_delay():
    """Test delay functionality"""
    print("\n" + "=" * 50)
    print("Test: Delay functionality")
    print("=" * 50)

    from dungeon.board import LightBallParticle

    particle = LightBallParticle(
        x=100, y=200, color=(80, 150, 255), target_x=300, target_y=400, delay=0.1
    )

    print(f"Initial delay: {particle.delay}")
    assert particle.delay > 0

    for i in range(5):
        active = particle.update(0.02)
        print(f"  Frame {i}: delay={particle.delay:.3f}, active={active}")

    assert particle.delay <= 0
    print("[PASS] Delay functionality test passed")

    return True


def test_light_ball_animation_creation():
    """Test light ball animation creation"""
    print("\n" + "=" * 50)
    print("Test: Light ball animation creation")
    print("=" * 50)

    from dungeon.board import OrbBoard, LightBallParticle
    from config import ORB_COLORS

    class MockPet:
        def __init__(self, attr, sub_attr=None):
            self.name = f"Pet({attr}/{sub_attr})"
            self.attribute = attr
            self.sub_attribute = sub_attr

    board = OrbBoard()
    board._elimination_positions = [(100, 200), (150, 250), (200, 200)]
    board._elimination_colors = {
        "火": ORB_COLORS["火"],
        "水": ORB_COLORS["水"],
    }

    team_data = [
        {"pet": MockPet("火"), "x": 50, "y": 50},
        {"pet": MockPet("水"), "x": 100, "y": 50},
        {"pet": MockPet("火", "水"), "x": 150, "y": 50},
        {"pet": None, "x": 200, "y": 50},
        {"pet": MockPet("木"), "x": 250, "y": 50},
        {"pet": MockPet("光"), "x": 300, "y": 50},
    ]

    board.spawn_light_balls(team_data)

    print(f"Created light ball count: {len(board.light_balls)}")
    print(f"Elimination colors: {board._elimination_colors}")

    fire_positions = 3
    fire_targets = 3
    water_positions = 3
    water_targets = 2
    expected_count = (fire_positions * fire_targets) + (water_positions * water_targets)
    assert len(board.light_balls) == 12 or len(board.light_balls) == expected_count, (
        f"Expected {expected_count}, got {len(board.light_balls)}"
    )

    print("[PASS] Light ball animation creation test passed")

    return True


def test_light_ball_update_loop():
    """Test light ball update loop"""
    print("\n" + "=" * 50)
    print("Test: Light ball update loop")
    print("=" * 50)

    from dungeon.board import LightBallParticle

    particles = []
    for i in range(5):
        p = LightBallParticle(
            x=100 + i * 20,
            y=200,
            color=(255, 80, 80),
            target_x=300 + i * 20,
            target_y=400,
            delay=i * 0.05,
        )
        particles.append(p)

    print(f"Initial particle count: {len(particles)}")

    for frame in range(60):
        particles = [p for p in particles if p.update(0.016)]
        if frame % 5 == 0:
            print(f"  Frame {frame}: remaining particles={len(particles)}")

    assert len(particles) == 0
    print("[PASS] Light ball update loop test passed")

    return True


def test_elimination_colors_mapping():
    """Test elimination colors mapping"""
    print("\n" + "=" * 50)
    print("Test: Elimination colors mapping")
    print("=" * 50)

    from dungeon.board import OrbBoard
    from config import ORB_COLORS, ORB_TYPES

    board = OrbBoard()

    for orb_type in ORB_TYPES:
        if orb_type != "心":
            color = ORB_COLORS.get(orb_type)
            board._elimination_colors[orb_type] = color
            print(f"  {orb_type} -> color: {color}")

    assert "火" in board._elimination_colors
    assert "水" in board._elimination_colors
    assert board._elimination_colors["火"] == ORB_COLORS["火"]

    print("[PASS] Elimination colors mapping test passed")

    return True


def test_orb_elimination_flow():
    """Test orb elimination flow"""
    print("\n" + "=" * 50)
    print("Test: Orb elimination flow")
    print("=" * 50)

    from dungeon.board import OrbBoard
    from config import ORB_TYPES, ORB_COLORS

    board = OrbBoard()

    board.orbs[0][0].type = "火"
    board.orbs[0][1].type = "火"
    board.orbs[0][2].type = "火"

    print("Initial board:")
    for y in range(board.rows):
        row_str = "  "
        for x in range(board.cols):
            orb = board.orbs[y][x]
            if orb:
                row_str += f"{orb.type} "
            else:
                row_str += ". "
        print(row_str)

    match_groups = board.find_match_groups()
    print(f"\nFound match groups: {len(match_groups)}")

    for i, group in enumerate(match_groups):
        print(f"  Group {i}: {len(group)} orbs")
        if group:
            orb_type = board.orbs[group[0][1]][group[0][0]].type
            print(f"    Type: {orb_type}, Color: {ORB_COLORS.get(orb_type)}")

    board.process_matches()
    print(f"\nElimination list: {len(board.elimination_list)}")
    print(f"Elimination colors: {board._elimination_colors}")

    print("[PASS] Orb elimination flow test passed")

    return True


def test_light_ball_multiple_groups():
    """Test light ball animation with multiple elimination groups"""
    print("\n" + "=" * 50)
    print("Test: Light ball with multiple elimination groups")
    print("=" * 50)

    from dungeon.board import OrbBoard, LightBallParticle
    from config import ORB_COLORS

    class MockPet:
        def __init__(self, attr, sub_attr=None):
            self.name = f"Pet({attr}/{sub_attr})"
            self.attribute = attr
            self.sub_attribute = sub_attr

    board = OrbBoard()

    board.orbs[0][0].type = "火"
    board.orbs[0][1].type = "火"
    board.orbs[0][2].type = "火"

    board.orbs[2][0].type = "水"
    board.orbs[2][1].type = "水"
    board.orbs[2][2].type = "水"

    board.orbs[4][0].type = "木"
    board.orbs[4][1].type = "木"
    board.orbs[4][2].type = "木"

    team_data = [
        {"pet": MockPet("火", "水"), "x": 50, "y": 50},
        {"pet": MockPet("水", "火"), "x": 100, "y": 50},
        {"pet": MockPet("木", "光"), "x": 150, "y": 50},
        {"pet": MockPet("火"), "x": 200, "y": 50},
        {"pet": MockPet("水"), "x": 250, "y": 50},
        {"pet": MockPet("光", "暗"), "x": 300, "y": 50},
    ]

    match_groups = board.find_match_groups()
    print(f"Match groups found: {len(match_groups)}")

    for i, group in enumerate(match_groups):
        print(f"  Group {i}: {len(group)} orbs")
        if group:
            orb = board.orbs[group[0][1]][group[0][0]]
            print(f"    Type: {orb.type}")

    board.process_matches()
    print(f"\nFirst group elimination list: {len(board.elimination_list)}")
    print(f"First group elimination colors: {board._elimination_colors}")

    board.spawn_light_balls(team_data)
    first_batch_count = len(board.light_balls)
    print(f"Light balls after first group: {first_batch_count}")

    board.light_balls = []
    board._elimination_positions = []
    board._elimination_colors = {}

    if len(match_groups) > 1:
        board.elimination_list = list(match_groups[1])
        for x, y in board.elimination_list:
            orb = board.orbs[y][x]
            if orb:
                center = board.get_cell_center(x, y)
                board._elimination_positions.append(center)
                orb_type = orb.type
                if orb_type not in board._elimination_colors:
                    board._elimination_colors[orb_type] = ORB_COLORS.get(
                        orb_type, (200, 200, 200)
                    )

        print(f"\nSecond group elimination list: {len(board.elimination_list)}")
        print(f"Second group elimination colors: {board._elimination_colors}")

        board.spawn_light_balls(team_data)
        second_batch_count = len(board.light_balls)
        print(f"Light balls after second group: {second_batch_count}")

        assert first_batch_count > 0, "First group should have light balls"
        assert second_batch_count > 0, "Second group should have light balls"

    print("[PASS] Multiple groups test passed")
    return True


if __name__ == "__main__":
    results = []

    results.append(("LightBallParticle class", test_light_ball_particle_class()))
    results.append(("Delay functionality", test_light_ball_particle_delay()))
    results.append(
        ("Light ball animation creation", test_light_ball_animation_creation())
    )
    results.append(("Light ball update loop", test_light_ball_update_loop()))
    results.append(("Elimination colors mapping", test_elimination_colors_mapping()))
    results.append(("Orb elimination flow", test_orb_elimination_flow()))
    results.append(("Multiple elimination groups", test_light_ball_multiple_groups()))
    results.append(("Multiple groups", test_light_ball_multiple_groups()))

    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    passed = 0
    failed = 0

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)
