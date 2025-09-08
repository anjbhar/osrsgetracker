from typing import Union

from fastapi import FastAPI, HTTPException, Path, Query

from ge_tracker import OSRSGETracker

app = FastAPI(
    title="OSRS GE Tracker API",
    description="An API to track Old School RuneScape Grand Exchange prices.",
    version="1.0.0",
)
tracker = OSRSGETracker()


def resolve_item_identifier(item_identifier: Union[int, str]) -> int:
    item_id = None
    if isinstance(item_identifier, str):
        if item_identifier.isdigit():
            item_id = int(item_identifier)
        else:
            item_id = tracker.get_item_id_by_name(item_identifier)
    elif isinstance(item_identifier, int):
        item_id = item_identifier

    if item_id is None:
        raise HTTPException(
            status_code=404, detail=f"Item '{item_identifier}' not found."
        )

    if str(item_id) not in tracker.item_mapping:
        raise HTTPException(
            status_code=404, detail=f"Item with ID '{item_id}' not found in mapping."
        )

    return item_id


@app.get("/", summary="Root endpoint")
async def root():
    """
    Root endpoint that returns the API title.
    """
    return {"message": app.title}


@app.get("/latest", summary="Get latest prices for all items")
async def get_all_latest_prices():
    """
    Get the latest high and low prices for all items that we have data for.
    """
    latest_prices = tracker.get_latest_prices()
    response_data = []
    for item_id_str, price_data in latest_prices.items():
        item_info = tracker.item_mapping.get(item_id_str, {})
        response_data.append(
            {
                "id": int(item_id_str),
                "name": item_info.get("name", "Unknown"),
                **price_data,
            }
        )
    return response_data


@app.get("/latest/{item_identifier}", summary="Get latest price for a specific item")
async def get_latest_price(
    item_identifier: str = Path(..., description="The name or ID of the item.")
):
    """
    Get the latest high and low price for a single item.
    You can provide either the item's name (e.g., "Abyssal whip") or its ID (e.g., 4151).
    """
    item_id = resolve_item_identifier(item_identifier)
    price_data = tracker.get_latest_prices(item_id=item_id)

    if not price_data or str(item_id) not in price_data:
        raise HTTPException(
            status_code=404, detail=f"Price data not found for item ID {item_id}."
        )

    item_info = tracker.item_mapping.get(str(item_id), {})
    item_info.pop("icon", None)

    return {
        **item_info,
        "price_data": price_data[str(item_id)],
    }


@app.get(
    "/timeseries/{item_identifier}", summary="Get time-series data for an item"
)
async def get_timeseries_data(
    item_identifier: str = Path(..., description="The name or ID of the item."),
    timestep: str = Query(
        ...,
        description="Timestep for the time-series.",
        regex="^(5m|1h|6h|24h)$",
    ),
):
    """
    Get time-series data for an item at a specific interval.
    You can provide either the item's name (e.g., "Abyssal whip") or its ID (e.g., 4151).
    """
    item_id = resolve_item_identifier(item_identifier)
    try:
        timeseries_data = tracker.get_timeseries(item_id, timestep)
        item_info = tracker.item_mapping.get(str(item_id), {})
        item_info.pop("icon", None)
        return {
            **item_info,
            "timestep": timestep,
            "timeseries": timeseries_data,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
