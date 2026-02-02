# Roadmap

Future improvements for the Tesla Charging Optimizer.

## Quick Wins

Simple changes that can be done immediately.

- [x] Update "Today's Rates" heading to "Available Rates" (now includes tomorrow)
- [x] Add rate coverage badge showing "Today only" vs "Today + Tomorrow"
- [x] Add health check endpoint (`/health`) for Coolify monitoring
- [x] Show last updated timestamp in the UI

## High Value

Major features that significantly improve the user experience.

- [ ] **Departure Time Constraint**
  - Add "I need to leave by" time picker
  - Only select charging slots before that deadline
  - Ensures car is ready when you need it

- [ ] **Rate Chart Visualization**
  - Visual graph showing prices over 24-48 hours
  - Highlight optimal slots on the chart
  - Show current time marker

- [ ] **Start Charging Button**
  - Trigger Tesla charging via Home Assistant
  - One-click to start charging during optimal window
  - Option to schedule charging for next optimal slot

- [ ] **Next-Day Rates Indicator**
  - Visual badge when tomorrow's rates are available (after 4pm)
  - Clear indication of rate coverage period
  - Countdown to when next-day rates publish

- [ ] **Negative Rate Alerts**
  - Highlight plunge pricing events (Octopus pays you to charge)
  - Special styling for negative rates
  - Push notification for exceptional pricing

## Medium Value

Useful features that enhance the overall experience.

- [ ] **Auto-Refresh**
  - Real-time updates when rates change
  - WebSocket or Server-Sent Events for live data
  - More responsive than current 5-minute polling

- [ ] **PWA Support**
  - Add manifest.json for installability
  - Service worker for offline capability
  - Home screen icon for mobile devices

- [ ] **Push Notifications**
  - Alert when optimal charging window starts
  - Daily summary of best charging times
  - Notify when rates drop below threshold

- [ ] **Cost History & Analytics**
  - Track actual charging sessions
  - Calculate savings vs flat-rate tariff
  - Monthly/yearly cost summaries
  - Export data for analysis

- [ ] **Configurable Settings**
  - Charger power (7kW, 11kW, 22kW)
  - Battery capacity for different Tesla models
  - Default target percentage
  - Preferred charging hours

## Nice to Have

Features for the future when core functionality is solid.

- [ ] **Carbon Intensity Overlay**
  - Integrate National Grid carbon intensity API
  - Show when energy is cheap AND green
  - Eco-mode: prioritize low-carbon over cheapest

- [ ] **Multiple Vehicle Support**
  - Support households with multiple EVs
  - Different battery sizes and charger speeds
  - Combined optimal scheduling

- [ ] **Calendar Integration**
  - Sync with Google/Apple calendar
  - Auto-set departure times from appointments
  - Smart scheduling based on calendar events

- [ ] **Smart Preconditioning**
  - Schedule cabin heating during cheap rates
  - Align preconditioning with departure time
  - Battery preconditioning in cold weather

- [ ] **Octopus API Direct Integration**
  - Fetch rates directly from Octopus API
  - Fallback if Home Assistant unavailable
  - Support for other Agile regions

## Completed

- [x] Next-day rates support for overnight charging optimization (v1.1.0)
- [x] Initial release with Flask dashboard (v1.0.0)
- [x] Home Assistant integration for Tesla battery state
- [x] Octopus Agile rate fetching
- [x] Optimal charging slot calculator
- [x] Docker deployment support
