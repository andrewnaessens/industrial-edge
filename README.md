# Industrial Edge

## Project Description
A containerised Python based edge application for real-time industrial monitoring within factory/production line environments. Industrial Edge syncs sensor data (temperature, humidity, and illuminance) from a Raspberry Pi to HiveMQ Cloud via MQTT messaging.

Sensor data is processed locally with local alerts triggered via an LED when environmental sensor data (temperature, humidity, and illuminance) is outside of safe range, which is implemented via thresholds.

All sensor data and alert events can be monitored remotely via a dedicated web dashboard which is subscribed to HiveMQ Cloud and deployed via render at: [https://industrial-edge-dashboard.onrender.com](https://industrial-edge-dashboard.onrender.com)

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

## Outer Loop: Production Environment
Transitioned from Podman to K3s for scalable deployments to edge devices (Raspberry Pi) with Flask/Gunicorn dashboard on [Render](https://render.com) for global telemetry monitoring.

### Prerequisites
- Git clone repository (vitals-deployment.yaml) to Raspberry Pi.

### Install K3s: (Configured for local user access)
```
curl -sfL https://get.k3s.io | sudo sh -s - --write-kubeconfig-mode 644

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```
Note: using --write-kubeconfig-mode 644 for this single-node Edge deployment to allow the non-root Pi user to manage the cluster. However, in a multi-tenant production environment, 600 should be used. Access would instead be managed by copying the credentials to a user-owned directory (~/.kube/config) with restricted ownership.

### Configure HiveMQ Secrets: 
```
kubectl create secret generic hivemq-vitals \
  --from-literal=MQTT_BROKER='url' \
  --from-literal=MQTT_USER='user' \
  --from-literal=MQTT_PASS='pass'
```

### Deploy the Edge Service

Run the following from the project root to apply the Kubernetes manifest:
```
kubectl apply -f k8s/edge/vitals-deployment.yaml
```

## Contributing Guidelines
This project is maintained and contributed to by the developer, Andrew Naessens. Contributions from others are welcome. Please contact the developer for contributions relating to reporting issues, submitting feature requests, or code contributions. 

## Contact Information
Andrew Naessens
