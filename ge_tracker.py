import json
from typing import Optional, Dict, Any, List

import requests

class OSRSGETracker:
    BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"
    
    def __init__(self, mapping_file: str = "mapping.json"):
        self.item_mapping = self._load_mapping(mapping_file)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "osrs-ge-tracker - a simple GE tracker"
        })

    def _load_mapping(self, mapping_file: str) -> Dict[str, Dict[str, Any]]:
        try:
            with open(mapping_file, 'r') as f:
                mapping_data = json.load(f)
            
            item_map = {}
            for item in mapping_data:
                item_map[str(item['id'])] = item
            return item_map
        except FileNotFoundError:
            print(f"Error: {mapping_file} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {mapping_file}.")
            return {}

    def get_item_id_by_name(self, name: str) -> Optional[int]:
        for item_id, item_data in self.item_mapping.items():
            if item_data['name'].lower() == name.lower():
                return int(item_id)
        return None

    def get_latest_prices(self, item_id: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest"
        params = {}
        if item_id:
            params['id'] = item_id
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get('data', {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching latest prices: {e}")
            return {}

    def get_5m_prices(self, timestamp: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/5m"
        params = {}
        if timestamp:
            params['timestamp'] = timestamp
            
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get('data', {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching 5m prices: {e}")
            return {}

    def get_1h_prices(self, timestamp: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/1h"
        params = {}
        if timestamp:
            params['timestamp'] = timestamp
            
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get('data', {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching 1h prices: {e}")
            return {}

    def get_timeseries(self, item_id: int, timestep: str) -> List[Dict[str, Any]]:
        if timestep not in ["5m", "1h", "6h", "24h"]:
            raise ValueError("Invalid timestep. Must be one of '5m', '1h', '6h', '24h'.")
            
        url = f"{self.BASE_URL}/timeseries"
        params = {'id': item_id, 'timestep': timestep}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching timeseries data: {e}")
            return []
