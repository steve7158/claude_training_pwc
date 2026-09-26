---
type: community
cohesion: 0.29
members: 11
---

# Observability & Load-Test Stack

**Cohesion:** 0.29 - loosely connected
**Members:** 11 nodes

## Members
- [[Docker Compose - OTelPrometheusTempoGrafana Stack]] - code - docker-compose.yaml
- [[Docker Compose - k6 InfluxDBGrafana Stack]] - code - docker-compose.k6.yaml
- [[Grafana Datasources Provisioning (Prometheus + Tempo)]] - code - grafana/provisioning/datasources/datasources.yaml
- [[Grafana InfluxDB Datasource Provisioning]] - code - k6-observability/grafana/provisioning/datasources/influxdb.yaml
- [[Grafana k6 Dashboards Provider Config]] - code - k6-observability/grafana/provisioning/dashboards/dashboards.yaml
- [[OTel Collector Config]] - code - otel-collector-config.yaml
- [[Observability Python Requirements (OTel SDK)]] - code - requirements-observability.txt
- [[Prometheus Scrape Config]] - code - prometheus.yml
- [[Tempo Config]] - code - tempo.yaml
- [[k6-grafana Service (Grafana 11.4.0)]] - code - docker-compose.k6.yaml
- [[k6-influxdb Service (InfluxDB 1.8)]] - code - docker-compose.k6.yaml

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Observability__Load-Test_Stack
SORT file.name ASC
```
