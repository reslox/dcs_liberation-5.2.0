from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterator, List, Optional, TYPE_CHECKING, Tuple

from game import db
from game.data.groundunitclass import GroundUnitClass
from game.dcs.groundunittype import GroundUnitType
from game.factions.faction import Faction
from game.squadrons import Squadron
from game.theater import ControlPoint, MissionTarget
from game.utils import meters
from gen.flights.ai_flight_planner_db import aircraft_for_task
from gen.flights.closestairfields import ObjectiveDistanceCache
from gen.flights.flight import FlightType




@staticmethod
def fulfill_aircraft_request(
        squadrons: list[Squadron], quantity: int, budget: float
) -> Tuple[float, bool]:
    for squadron in squadrons:
        price = squadron.aircraft.price * quantity
        if price > budget:
            continue

        squadron.pending_deliveries += quantity
        budget -= price
        return budget, True
    return budget, False


def purchase_aircraft(self, budget: float) -> float:
    for request in self.game.coalition_for(self.is_player).procurement_requests:
        squadrons = list(self.best_squadrons_for(request))
        if not squadrons:
            # No airbases in range of this request. Skip it.
            continue
        budget, fulfilled = self.fulfill_aircraft_request(
            squadrons, request.number, budget
        )
        if not fulfilled:
            # The request was not fulfilled because we could not afford any suitable
            # aircraft. Rather than continuing, which could proceed to buy tons of
            # cheap escorts that will never allow us to plan a strike package, stop
            # buying so we can save the budget until a turn where we *can* afford to
            # fill the package.
            break
    return budget
