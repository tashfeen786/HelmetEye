# TODO: Implement Refresh Mechanism for Report Section

## Backend Changes
- [x] Modify /api/report endpoint in main.py to add cache-control headers to prevent browser caching.

## Frontend Changes
- [x] Update ReportTable component in ../src/components/report-table.tsx to add a manual refresh button.
- [x] Reduce polling interval from 30 seconds to 10 seconds.
- [x] Add fetch options (cache: 'no-cache') to prevent caching in fetch requests.

## Testing
- [ ] Test that new detections appear immediately after insertion.
- [ ] Verify no memory leaks in polling.
- [ ] Ensure browser caching does not interfere.
