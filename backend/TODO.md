# TODO: Implement Polling in ReportTable Component

## Steps to Complete:
- [x] Modify useEffect in ReportTable.tsx to add polling every 30 seconds
- [x] Ensure interval is cleared on component unmount to prevent memory leaks
- [x] Test by triggering a new detection and verifying frontend updates automatically

## Notes:
- Polling will re-fetch data from /api/report every 30 seconds.
- No manual refresh button needed as per user preference.
- Testing completed: Backend data is being fetched correctly, and polling is implemented. Frontend will now update automatically every 30 seconds with new detections.
