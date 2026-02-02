# Changelog

All notable changes to the Tesla Charging Optimizer will be documented in this file.

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
