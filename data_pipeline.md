### 1. High-level pipeline overview

Wrappers → MQ1 → Data Collector → MQ2 → Resource Service → MQ2 → Indicator Service
                        |                        |                     |
                        v                        v                     v
                        (Stats API)         Resource Mongo     Indicator Mongo + Redis

-----

### 2. Detailed step-by-step with data states

#### (A) Wrappers

  * **Function:** Pull data from external sources (CSV, XLSX, APIs, sensors).
  * **Granularity:** Economic indicators (low), sensors (high).
  * **Output format example:**

```json
{
  "wrapper_id": "uuid",
  "data": [
    { "x": "2025-08-09T12:00:00Z", "y": 42.5 },
    ...
  ],
  "metadata": { "source": "API name", "granularity": "hourly" }
}
```

Metadata can contain source details, granularity, collection timestamps, or other context (not yet strictly defined).

  * **Passes to:** Data Collector via **MQ1**.

-----

#### (B) Data Collector

  * **Function:**
    1.  Receive raw data from wrappers via MQ1.
    2.  Light validation (schema, duplicates, timestamps).
    3.  No merge or aggregation; keeps data raw.
    4.  Push validated raw data to **MQ2** for Resource Service.
  * **Storage:** No persistent storage here, only in-memory until pushed.
  * **API:** Stats API for operational metrics only.

-----

#### (C) MQ2 — Data flow (Data Collector → Resource Service)

  * **Purpose:** MQ2 carries messages from Data Collector to Resource Service, and later from Resource Service to Indicator Service. Messages in both directions are single `data` payloads (not lists), chunked as needed.
  * **Data in queue (Data Collector → Resource Service):** Raw `data` associated with a `wrapper_id`.
  * **Message example (Data Collector → Resource Service):**

```json
{
  "wrapper_id": "sensor_123",
  "data": [
    { "x": "2025-08-09T12:00:00Z", "y": 10.2 },
    { "x": "2025-08-09T12:00:10Z", "y": 10.4 }
  ],
  "metadata": { "source": "wrapper_abc", "granularity": "10s" }
}
```

Metadata can contain granularity, source, collection timestamps, or other attributes; the schema is not defined.

  * **Behavior:** Resource Service consumes these messages, maps `wrapper_id` → `resource_id`, stores the raw data in Resource Mongo, and proceeds with its minimal-merge + chunking logic before forwarding resource-level chunks back onto MQ2 for Indicator Service.

-----

#### (D) Resource Service

  * **Function:**
    1.  Map `wrapper_id` → `resource_id` (1:1).
    2.  Store raw data in Resource Mongo.
    3.  Perform minimal merge on data per resource (resolve conflicts, combine overlaps).
    4.  Store per-resource data in Resource Mongo.
    5.  Chunk merged data dynamically based on the interval that covers changed points (from the earliest to the last data point datetime); if a chunk exceeds `THRESHOLD` points, split into smaller chunks. Include an explicit `chunk_interval` on each chunk.
    6.  Push minimally merged, chunked resource-level data to **MQ2** for Indicator Service.
  * **Storage:** Raw + resource-level merged segments in Resource Mongo.

-----

#### (E) MQ2 → Indicator Service

  * **Source:** Messages from Resource Service over MQ2.
  * **Data type:** Minimally merged, chunked resource `data` with `resource_id` and `chunk_interval`.
  * **Message example (Resource Service → Indicator Service):**

```json
{
  "resource_id": "res_789",
  "data": [
    { "x": "2025-08-09T12:00:00Z", "y": 42.5 },
    { "x": "2025-08-09T12:01:00Z", "y": 43.1 }
  ],
  "chunk_interval": { "start": "2025-08-09T12:00:00Z", "end": "2025-08-09T12:10:00Z" },
  "metadata": { "granularity": "1min", "source": "sensor_device_1" }
}
```

Metadata can contain granularity, source, collection timestamps, or other attributes; the schema is not defined.

  * **Indicator Service handling:** For each chunk received, delete all existing data points in MongoDB for that resource within the `chunk_interval`, then insert the chunk's points. This guarantees no stale overlaps remain for that interval.

-----

#### (F) Indicator Service

  * **Function:**
    1.  Receives chunked resource-level data from MQ2.
    2.  Maintains a replica of resource-level data in `resource_level_data` collection using a "clean overwrite" strategy.
    3.  After each update to `resource_level_data`, triggers a merge process for the affected indicator.
    4.  The merge process combines data from all resources associated with the indicator and stores the result in a dedicated `indicator_data_store` collection.
    5.  The `data_propagator` service reads from the `indicator_data_store` to serve API requests, with options to customize the data window view.
    6.  Results from `data_propagator` are cached in Redis.
  * **Data state:**
      * Indicator Mongo:
          * `resource_level_data`: Per-resource merged data.
          * `indicator_data_store`: Per-indicator merged historical data.
      * Redis: Cached transformed views for fast API responses.

-----

### 3. Why this separation works

  * **Resource Mongo** holds raw + minimal merged resource data (authoritative per resource).
  * **Indicator Service** centralizes N:1 mapping, final merging, and transformation (**data_viewer**).
  * **Redis** caches common transformed views for performance.
  * **Chunking** with explicit intervals keeps MQ payloads manageable and enables clean overwrite semantics in Indicator Service.

-----

### 4. Data state transition summary

1.  Wrappers → raw **data** → MQ1.
2.  Data Collector → validated raw **data** → MQ2 (`wrapper_id`).
3.  Resource Service Mongo → raw (and minimally merged) segments, chunked dynamically.
4.  MQ2 → Indicator Service receives chunked minimal-merged resource **data** (`resource_id` + `chunk_interval`).
5.  Indicator Service Mongo → `resource_level_data` and `indicator_data_store` with merged final historical indicator data.
6.  Indicator Service Redis → cached transformed views (fast access).