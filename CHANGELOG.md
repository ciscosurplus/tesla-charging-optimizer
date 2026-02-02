# Changelog

All notable changes to the Tesla Charging Optimizer will be documented in this file.

## [1.3.0] - 2026-02-02

### Added
- **Rate Chart Visualization**: Interactive bar chart showing electricity rates over 24-48 hours
- Built with Chart.js for smooth rendering and interactivity
- Color-coded rate bars (green for cheap, yellow for medium, red for expensive)
- Current time "NOW" marker to easily identify current position
- Day boundary markers showing today/tomorrow transition
- Optimal charging slots highlighted when calculation is performed
- Responsive design that works well on mobile devices

## [1.2.0] - 2026-02-02

### Added
- **Rate coverage badge**: Visual indicator showing whether rates include "Today only", "Tomorrow only", or "Today + Tomorrow"
- **Health check endpoint**: `GET /health` for container orchestration, with optional `?check_ha=true` for deep health checks
- **Last updated timestamp**: Footer now shows when data was last refreshed
- **APP_VERSION constant**: Centralized version tracking in app.py

### Changed
- Renamed "Today's Rates" heading to "Available Rates" for accuracy

## [1.1.0] - 2026-02-02

### Added
- **Next-day rates support**: App now fetches both current day and next day Octopus Agile rates
- After 4pm when Octopus publishes tomorrow's rates, the optimizer can find charging slots that span overnight into the next day
- New `rates_info` object in API responses with `includes_today` and `includes_tomorrow` flags
- Deduplication logic to handle overlapping rate slots at midnight

### Changed
- `get_octopus_rates()` now searches for both `current_day_rates` and `next_day_rates` entities
- API responses include rate coverage metadata for better visibility

## [1.0.0] - 2026-02-02

### Added
- Initial release of Tesla Charging Optimizer
- Flask web application with responsive dashboard
- Home Assistant integration for Tesla battery state
- Octopus Agile rate fetching from Home Assistant entities
- Optimal charging slot calculator based on cheapest 30-minute periods
- REST API endpoints:
  - `GET /api/status` - Current Tesla state and available rates
  - `GET /api/calculate?target=80` - Calculate optimal charging slots
- Docker support with Dockerfile for containerized deployment
- Support for Tesla Model Y Long Range (75 kWh battery, 7 kW charger)
- Automatic grouping of contiguous charging slots into blocks
- Cost calculation in both pence and pounds
