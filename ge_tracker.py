import asyncio
from typing import Optional, Dict, Any, List

import httpx


class OSRSGETracker:
    BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"

    def __init__(self, mapping_refresh_interval: int = 3600):
        self.item_mapping: Dict[str, Dict[str, Any]] = {}
        self.mapping_refresh_interval = mapping_refresh_interval
        self.session: Optional[httpx.AsyncClient] = None
        self._mapping_task: Optional[asyncio.Task] = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            headers={"User-Agent": "osrs-ge-tracker - a simple GE tracker"}
        )
        await self.refresh_mapping()
        self._mapping_task = asyncio.create_task(self._mapping_refresh_loop())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._mapping_task:
            self._mapping_task.cancel()
            try:
                await self._mapping_task
            except asyncio.CancelledError:
                pass
        if self.session:
            await self.session.aclose()

    async def refresh_mapping(self) -> None:
        if not self.session:
            return

        url = f"{self.BASE_URL}/mapping"
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            mapping_data = response.json()
            item_map = {}
            for item in mapping_data:
                item_map[str(item["id"])] = item
            self.item_mapping = item_map
        except httpx.RequestError as e:
            print(f"Error fetching item mapping: {e}")
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error parsing item mapping response: {e}")

    async def _mapping_refresh_loop(self) -> None:
        while True:
            await asyncio.sleep(self.mapping_refresh_interval)
            await self.refresh_mapping()

    def get_item_id_by_name(self, name: str) -> Optional[int]:
        for item_id, item_data in self.item_mapping.items():
            if item_data["name"].lower() == name.lower():
                return int(item_id)
        return None

    async def get_latest_prices(self, item_id: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest"
        params = {}
        if item_id:
            params["id"] = item_id

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", {})
        except httpx.RequestError as e:
            print(f"Error fetching latest prices: {e}")
            return {}

    async def get_5m_prices(self, timestamp: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/5m"
        params = {}
        if timestamp:
            params["timestamp"] = timestamp

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", {})
        except httpx.RequestError as e:
            print(f"Error fetching 5m prices: {e}")
            return {}

    async def get_1h_prices(self, timestamp: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/1h"
        params = {}
        if timestamp:
            params["timestamp"] = timestamp

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", {})
        except httpx.RequestError as e:
            print(f"Error fetching 1h prices: {e}")
            return {}

    async def get_timeseries(
        self, item_id: int, timestep: str
    ) -> List[Dict[str, Any]]:
        if timestep not in ["5m", "1h", "6h", "24h"]:
            raise ValueError(
                "Invalid timestep. Must be one of '5m', '1h', '6h', '24h'."
            )

        url = f"{self.BASE_URL}/timeseries"
        params = {"id": item_id, "timestep": timestep}

        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except httpx.RequestError as e:
            print(f"Error fetching timeseries data: {e}")
            return []
