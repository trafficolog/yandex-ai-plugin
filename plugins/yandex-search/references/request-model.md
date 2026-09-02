# Request model

REST uses CamelCase (`queryText`, `searchType`, `groupMode`, `groupsOnPage`, `docsInGroup`, `responseFormat`, `resultsWithin`). SEO structured workflows use `FORMAT_XML`, `GROUP_MODE_FLAT`, and `docsInGroup=1`. Do not silently change region, search type, device-oriented `userAgent`, freshness, grouping, sorting, family mode, or typo mode between snapshots.

The documented result-depth ceiling is 250 results. Validate the complete configured window using `requested_per_page = groupsOnPage * docsInGroup`, `window_start = page * requested_per_page`, `window_end = window_start + requested_per_page`. A window ending at 250 is valid; a window starting at 250 or ending above 250 is rejected. Do not rely on undocumented partial-page truncation.
