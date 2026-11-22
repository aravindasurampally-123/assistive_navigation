"""
Module 7: Walking Navigation Subsystem
AI-Powered Assistive Navigation System for Visually Impaired People

Generates pedestrian walking routes, provides turn-by-turn guidance,
and features dual-engine routing (OpenRouteService with resilient OSRM fallback).
Academic Note: IP-based geolocation is explicitly labeled as approximate network location,
never misrepresented as hardware satellite GPS.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import os
import requests
import geocoder

from config import (
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE,
    ORS_API_KEY,
    OSRM_FALLBACK_URL
)

try:
    import openrouteservice
    HAS_ORS = True
except ImportError:
    HAS_ORS = False


@dataclass
class Location:
    """Represents geographic coordinates and their derivation method."""
    latitude: float
    longitude: float
    source: str                 # "IP_APPROXIMATE", "MANUAL_INPUT", "DEFAULT_PRESET"
    accuracy_note: str


@dataclass
class RouteStep:
    """A discrete turn-by-turn walking maneuver."""
    step_number: int
    instruction: str
    distance_meters: float
    duration_seconds: float
    maneuver_type: str


@dataclass
class WalkingRoute:
    """Complete pedestrian walking route with summary metrics and maneuvers."""
    total_distance_km: float
    total_duration_minutes: float
    provider: str               # "OpenRouteService" or "OSRM_Public_Fallback"
    steps: List[RouteStep]
    coordinates: List[Tuple[float, float]]  # [(lat, lon), ...] for map display


class WalkingNavigator:
    """
    Manages location acquisition, pedestrian pathfinding, and turn-by-turn guidance.
    """

    def __init__(self, ors_key: Optional[str] = None):
        self.ors_key = ors_key or ORS_API_KEY or os.getenv("ORS_API_KEY", "")
        self.current_route: Optional[WalkingRoute] = None
        self.current_step_index: int = 0

    @staticmethod
    def get_current_location(
        allow_ip_lookup: bool = True,
        manual_coords: Optional[Tuple[float, float]] = None
    ) -> Location:
        """
        Obtains starting location.
        Adheres to strict ethical constraint: IP network derivation is never labeled as GPS.
        """
        # 1. Manual coordinates take highest precedence
        if manual_coords is not None:
            lat, lon = manual_coords
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return Location(
                    latitude=lat,
                    longitude=lon,
                    source="MANUAL_INPUT",
                    accuracy_note="User-specified manual starting coordinate."
                )

        # 2. IP-based network geolocation (if permitted)
        if allow_ip_lookup:
            try:
                g = geocoder.ip("me")
                if g.latlng and len(g.latlng) == 2:
                    return Location(
                        latitude=float(g.latlng[0]),
                        longitude=float(g.latlng[1]),
                        source="IP_APPROXIMATE",
                        accuracy_note="Network IP-based approximate location (City/ISP level, not satellite GPS)."
                    )
            except Exception as e:
                print(f"[NAV] IP location lookup failed: {e}")

        # 3. Safe fallback to default configuration coordinate
        return Location(
            latitude=DEFAULT_LATITUDE,
            longitude=DEFAULT_LONGITUDE,
            source="DEFAULT_PRESET",
            accuracy_note="Default campus/city preset coordinate."
        )

    def calculate_walking_route(
        self,
        start_lat: float,
        start_lon: float,
        dest_lat: float,
        dest_lon: float
    ) -> Optional[WalkingRoute]:
        """
        Calculates a pedestrian foot-walking route.
        Attempts OpenRouteService first; automatically falls back to OSRM on any failure.
        """
        # Validate coordinates
        for lat, lon in [(start_lat, start_lon), (dest_lat, dest_lon)]:
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError(f"Invalid coordinate: lat={lat}, lon={lon}")

        # Try Primary Engine: OpenRouteService (if key is present)
        if self.ors_key and HAS_ORS:
            try:
                print("[NAV] Querying OpenRouteService foot-walking directions...")
                route = self._query_openrouteservice(start_lat, start_lon, dest_lat, dest_lon)
                if route:
                    self.current_route = route
                    self.current_step_index = 0
                    return route
            except Exception as exc:
                print(f"[NAV] OpenRouteService query failed ({exc}). Initiating resilient OSRM fallback...")

        # Try Resilient Secondary Engine: OSRM Public Walking API
        try:
            print("[NAV] Querying Open Source Routing Machine (OSRM) foot endpoint...")
            route = self._query_osrm(start_lat, start_lon, dest_lat, dest_lon)
            if route:
                self.current_route = route
                self.current_step_index = 0
                return route
        except Exception as exc:
            print(f"[NAV] OSRM query failed ({exc}).")

        # Offline geometric fallback (if completely disconnected from internet)
        print("[NAV] Network unavailable. Generating offline linear heading route...")
        route = self._generate_offline_route(start_lat, start_lon, dest_lat, dest_lon)
        self.current_route = route
        self.current_step_index = 0
        return route

    def _query_openrouteservice(
        self,
        start_lat: float,
        start_lon: float,
        dest_lat: float,
        dest_lon: float
    ) -> WalkingRoute:
        """Query ORS Directions API."""
        client = openrouteservice.Client(key=self.ors_key, timeout=10)
        res = client.directions(
            coordinates=[(start_lon, start_lat), (dest_lon, dest_lat)],
            profile="foot-walking",
            format="geojson",
            instructions=True,
            language="en"
        )

        props = res["features"][0]["properties"]
        summary = props["summary"]
        distance_m = float(summary["distance"])
        duration_s = float(summary["duration"])

        steps_data = props["segments"][0]["steps"]
        steps: List[RouteStep] = []

        for i, s in enumerate(steps_data, start=1):
            steps.append(RouteStep(
                step_number=i,
                instruction=s.get("instruction", "Continue walking"),
                distance_meters=float(s.get("distance", 0.0)),
                duration_seconds=float(s.get("duration", 0.0)),
                maneuver_type=str(s.get("type", "step"))
            ))

        # Extract coordinates for UI mapping
        raw_coords = res["features"][0]["geometry"]["coordinates"]
        coords = [(pt[1], pt[0]) for pt in raw_coords]

        return WalkingRoute(
            total_distance_km=distance_m / 1000.0,
            total_duration_minutes=duration_s / 60.0,
            provider="OpenRouteService",
            steps=steps,
            coordinates=coords
        )

    @staticmethod
    def _query_osrm(
        start_lat: float,
        start_lon: float,
        dest_lat: float,
        dest_lon: float
    ) -> WalkingRoute:
        """Query OSRM public walking router."""
        url = f"{OSRM_FALLBACK_URL}/{start_lon},{start_lat};{dest_lon},{dest_lat}?steps=true&geometries=geojson&overview=full"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise ValueError(f"OSRM returned error code: {data.get('code')}")

        primary_route = data["routes"][0]
        distance_m = float(primary_route["distance"])
        duration_s = float(primary_route["duration"])

        raw_steps = primary_route["legs"][0]["steps"]
        steps: List[RouteStep] = []

        for i, s in enumerate(raw_steps, start=1):
            maneuver = s.get("maneuver", {})
            m_type = maneuver.get("type", "turn")
            m_modifier = maneuver.get("modifier", "")
            street_name = s.get("name", "")

            # Format natural-language instruction
            if m_type == "depart":
                inst = f"Start walking along {street_name}" if street_name else "Start walking forward"
            elif m_type == "arrive":
                inst = "You have arrived at your destination."
            elif m_modifier:
                inst = f"Turn {m_modifier} onto {street_name}" if street_name else f"Turn {m_modifier}"
            else:
                inst = f"Continue on {street_name}" if street_name else "Continue forward"

            steps.append(RouteStep(
                step_number=i,
                instruction=inst,
                distance_meters=float(s.get("distance", 0.0)),
                duration_seconds=float(s.get("duration", 0.0)),
                maneuver_type=m_type
            ))

        raw_coords = primary_route["geometry"]["coordinates"]
        coords = [(pt[1], pt[0]) for pt in raw_coords]

        return WalkingRoute(
            total_distance_km=distance_m / 1000.0,
            total_duration_minutes=duration_s / 60.0,
            provider="OSRM_Public_Fallback",
            steps=steps,
            coordinates=coords
        )

    @staticmethod
    def _generate_offline_route(
        start_lat: float,
        start_lon: float,
        dest_lat: float,
        dest_lon: float
    ) -> WalkingRoute:
        """Approximates straight-line walking bearing when fully offline."""
        import math
        dlat = math.radians(dest_lat - start_lat)
        dlon = math.radians(dest_lon - start_lon)
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(math.radians(start_lat)) * math.cos(math.radians(dest_lat)) *
             math.sin(dlon / 2.0) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = 6371.0 * c
        duration_min = (distance_km / 4.5) * 60.0  # standard 4.5 km/h pedestrian walk speed

        steps = [
            RouteStep(1, "Start walking toward destination bearing", distance_km * 1000.0, duration_min * 60.0, "depart"),
            RouteStep(2, "You have reached destination area.", 0.0, 0.0, "arrive")
        ]

        return WalkingRoute(
            total_distance_km=distance_km,
            total_duration_minutes=duration_min,
            provider="Offline_Estimator",
            steps=steps,
            coordinates=[(start_lat, start_lon), (dest_lat, dest_lon)]
        )

    def get_current_instruction(self) -> Optional[str]:
        """Returns the current step instruction without advancing."""
        if not self.current_route or not self.current_route.steps:
            return None
        if self.current_step_index >= len(self.current_route.steps):
            return "You have reached your destination."
        step = self.current_route.steps[self.current_step_index]
        return f"{step.instruction} for {step.distance_meters:.0f} meters."

    def advance_step(self) -> Optional[str]:
        """Advances to the next turn maneuver along the route."""
        if not self.current_route or not self.current_route.steps:
            return None
        self.current_step_index += 1
        return self.get_current_instruction()

    def repeat_instruction(self) -> str:
        """Repeats the current maneuver instruction."""
        inst = self.get_current_instruction()
        return inst if inst else "No active walking route."
