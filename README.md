# Industrial Edge

## Project Description
A containerised Python based edge application for real-time industrial monitoring within factory/production line environments. Industrial Edge syncs sensor data (vitals) from a Raspberry Pi to HiveMQ Cloud via MQTT messaging.

## Inner Loop: Local Development
This project uses a sandbox approach to allow for development on a workstation (e.g. laptop) with mock data (mock mode) and for testing on the physical hardware with real sensor data (hardware mode).

### Prerequisites
- Podman installed on your workstation and Pi.
- A .env file in the root directory (see .env.example).

### Launch the Sandbox

#### Build the environment 

Run the following from the project root:
```
podman build -t industrial-edge-dev -f Containerfile.dev .
```

#### Start the service
Run the following from the project root:
```
./scripts/dev-up.sh
```

## Upcoming Features
- [ ] **Local Alerts** Local alerts via an LED when environmental data is outside of safe range, implemented via thresholds.
- [ ] **Cloud Dashboard:** Flask app web interface for viewing real-time telemetry.
- [ ] **K3s Deployment:** Transition from Podman to lightweight Kubernetes orchestration for production.
