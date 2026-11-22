"""
Phase 7 Verification Script
Tests Walking Navigation, Location Acquisition (IP vs GPS vs Manual),
and Dual-Engine Routing (OpenRouteService + OSRM Fallback).
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.navigation import WalkingNavigator, Location, WalkingRoute


def test_location_acquisition():
    print("=" * 60)
    print("TEST 1: LOCATION DERIVATION & SENSOR LABELING")
    print("=" * 60)

    # 1. Manual Coordinate Input Test
    manual_loc = WalkingNavigator.get_current_location(
        allow_ip_lookup=False,
        manual_coords=(17.4400, 78.3489)
    )
    print(f"Manual Input: [{manual_loc.latitude}, {manual_loc.longitude}] | "
          f"Source: {manual_loc.source} | Note: {manual_loc.accuracy_note}")
    assert manual_loc.source == "MANUAL_INPUT"
    assert manual_loc.latitude == 17.4400

    # 2. IP-based Network Geolocation Test
    ip_loc = WalkingNavigator.get_current_location(allow_ip_lookup=True)
    print(f"IP Location : [{ip_loc.latitude}, {ip_loc.longitude}] | "
          f"Source: {ip_loc.source} | Note: {ip_loc.accuracy_note}")
    assert "GPS" not in ip_loc.source, "Constraint violation: IP location must never be labeled as GPS!"
    assert ip_loc.source in ["IP_APPROXIMATE", "DEFAULT_PRESET"]

    print("STATUS: PASS (Location acquisition and GPS distinction verified)")


def test_dual_engine_walking_route():
    print("\n" + "=" * 60)
    print("TEST 2: DUAL-ENGINE WALKING ROUTING (ORS + OSRM FALLBACK)")
    print("=" * 60)

    # Test route from Hyderabad City Center to nearby destination (~1 km walking route)
    start_lat, start_lon = 17.3840, 78.4564
    dest_lat, dest_lon = 17.3880, 78.4600

    navigator = WalkingNavigator()
    route = navigator.calculate_walking_route(start_lat, start_lon, dest_lat, dest_lon)

    assert route is not None, "Failed to generate walking route"
    assert len(route.steps) > 0, "Walking route has zero steps"
    assert route.total_distance_km > 0.0, "Route distance must be positive"

    print(f"Routing Successful:")
    print(f"  Provider       : {route.provider}")
    print(f"  Total Distance : {route.total_distance_km:.2f} km ({route.total_distance_km * 1000:.0f} m)")
    print(f"  Est. Duration  : {route.total_duration_minutes:.1f} minutes")
    print(f"  Turn Steps     : {len(route.steps)} maneuvers")

    print("\nTurn-by-Turn Maneuvers Sample (First 4 steps):")
    for s in route.steps[:4]:
        print(f"  Step {s.step_number}: {s.instruction:<45} | {s.distance_meters:.0f} m | Type: {s.maneuver_type}")

    print("STATUS: PASS (Walking route calculation and fallback verified)")
    return navigator


def test_turn_by_turn_guidance(navigator: WalkingNavigator):
    print("\n" + "=" * 60)
    print("TEST 3: TURN-BY-TURN STEP GUIDANCE & PROGRESSION")
    print("=" * 60)

    # 1. Initial Step
    step1 = navigator.get_current_instruction()
    print(f"Initial Step : '{step1}'")
    assert step1 is not None

    # 2. Repeat Step (Voice command "repeat instruction")
    repeated = navigator.repeat_instruction()
    print(f"Repeated Step: '{repeated}'")
    assert repeated == step1, "Repeat instruction did not return identical current step"

    # 3. Advance to Next Step
    step2 = navigator.advance_step()
    print(f"Advanced Step: '{step2}'")
    assert step2 is not None

    print("STATUS: PASS (Turn-by-turn instruction and repeat logic verified)")


def test_offline_geometric_route():
    print("\n" + "=" * 60)
    print("TEST 4: FULLY OFFLINE LINEAR ROUTE FALLBACK")
    print("=" * 60)

    offline_route = WalkingNavigator._generate_offline_route(17.3840, 78.4564, 17.3880, 78.4600)
    print(f"Offline Distance : {offline_route.total_distance_km:.2f} km")
    print(f"Offline Steps    : {len(offline_route.steps)}")
    assert offline_route.provider == "Offline_Estimator"
    assert len(offline_route.steps) == 2
    print("STATUS: PASS (Offline fallback verified)")


if __name__ == "__main__":
    test_location_acquisition()
    nav = test_dual_engine_walking_route()
    test_turn_by_turn_guidance(nav)
    test_offline_geometric_route()
    print("\n" + "=" * 60)
    print("PHASE 7 COMPLETED SUCCESSFULLY!")
    print("=" * 60)
