# OSRS GE Tracker API

This is an API to track item prices on the Old School RuneScape Grand Exchange using the RuneScape Wiki API.

## Features

- Get the latest high and low prices for any item.
- Get the latest prices for all available items.
- Get time-series data for an item (5m, 1h, 6h, 24h intervals).
- Uses a local `mapping.json` for item ID lookups.
- Endpoints accept either item name or item ID.

## Setup

1.  **Prerequisites**: Make sure you have Python 3.6+ installed.
2.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd osrs-ge-tracker
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Item Mapping**: Ensure you have the `mapping.json` file in the same directory as the scripts. This file should contain a mapping of OSRS items.

## Running the API

Run the API using `uvicorn`:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Once the API is running, you can access the interactive documentation at `http://127.0.0.1:8000/docs`.

## API Endpoints

-   `GET /`: Root endpoint that returns the API title.
-   `GET /latest`: Get the latest prices for all items.
-   `GET /latest/{item_identifier}`: Get the latest price for a specific item by name or ID.
-   `GET /timeseries/{item_identifier}`: Get time-series data for an item by name or ID.
    -   Query parameter: `timestep` (5m, 1h, 6h, 24h)
