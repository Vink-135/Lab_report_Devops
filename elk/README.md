# ELK Stack for Lab Portal

This directory contains the Docker Compose setup for running a local ELK stack for the Lab Portal project.

## Components

- Elasticsearch: stores and indexes logs and search data.
- Kibana: provides dashboards, log exploration, and visualization.
- Docker Compose: defines and runs both services in a single local environment.

## Elasticsearch Installation

The stack uses the official Elasticsearch image:

```yaml
docker.elastic.co/elasticsearch/elasticsearch:8.11.1
```

Elasticsearch is configured as a single-node instance for local development:

- `discovery.type=single-node`
- `xpack.security.enabled=false`
- JVM heap set to `512m` minimum and maximum

### Access

After startup, Elasticsearch is available at:

- http://localhost:9200

You can verify it with:

```bash
curl http://localhost:9200
```

## Kibana Installation

The stack uses the official Kibana image:

```yaml
docker.elastic.co/kibana/kibana:8.11.1
```

Kibana connects to the Elasticsearch service through the Docker Compose network.

### Access

After startup, Kibana is available at:

- http://localhost:5601

If Kibana starts before Elasticsearch is ready, it will retry until Elasticsearch becomes available.

## Docker Compose Setup

The compose file in this directory is:

- [docker-compose.yml](docker-compose.yml)

### Start the stack

From inside the `elk` directory, run:

```bash
docker compose up -d
```

### View logs

```bash
docker compose logs -f
```

### Stop the stack

```bash
docker compose down
```

### Recreate cleanly

```bash
docker compose down -v
docker compose up -d
```

## Logging Architecture

The ELK setup follows a simple local logging pipeline:

1. The application produces logs.
2. Logs are forwarded into Elasticsearch for storage and indexing.
3. Kibana reads indexed data from Elasticsearch.
4. Operators use Kibana to search logs, inspect trends, and build dashboards.

### Data Flow

```text
Application logs -> Elasticsearch -> Kibana dashboards and queries
```

### Design Notes

- Elasticsearch runs as a single node, which is appropriate for local development.
- Kibana is kept separate so visualization does not depend on application runtime behavior.
- Security is disabled in this local configuration to keep setup simple.
- The setup uses published ports only, so it can run without additional reverse proxies.

### Typical Use Cases

- Inspecting application logs during local development.
- Searching logs by time, service, or message content.
- Building simple dashboards for operational visibility.

## Validation

To verify the compose file is valid:

```bash
docker compose config
```

If the command completes without errors, the stack is ready to run.