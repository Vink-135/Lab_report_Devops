# Lab Portal

Lab Portal is a Flask-based diagnostic laboratory application for managing patient registrations, test bookings, report uploads, and administrative operations. The project includes local development support, containerization, Kubernetes manifests, Terraform provisioning, and an ELK stack for log exploration.

## What The Application Does

The application supports two primary roles:

- Patients can register, log in, book tests, view booking history, and download uploaded reports.
- Admins can view operational dashboards, search and update booking status, and upload PDF reports against bookings.

The app is intentionally simple and local-first, but the repository also includes deployment artifacts so it can be run in containers or deployed to Kubernetes.

## Project Structure

```text
lab-portal/
├── app.py
├── models.py
├── requirements.txt
├── seed_data.py
├── Dockerfile
├── Jenkinsfile
├── README.md
├── elk/
├── instance/
├── k8s/
├── static/
├── templates/
├── terraform/
└── uploads/
```

### Root Files

- `app.py` is the Flask application entry point and contains the routes, authentication checks, booking flow, report download logic, and admin actions.
- `models.py` defines the SQLAlchemy models for users, bookings, and reports.
- `requirements.txt` lists the Python dependencies required to run the app.
- `seed_data.py` is used to seed or initialize data for local development.
- `Dockerfile` builds the Flask app into a container image.
- `Jenkinsfile` defines the CI pipeline used to build and verify the application image.
- `README.md` is this project guide.

## Application Architecture

The app follows a standard Flask monolith structure:

1. The browser sends requests to Flask routes in `app.py`.
2. Flask reads and writes data through SQLAlchemy models in `models.py`.
3. HTML templates render the UI.
4. CSS and static assets are served from the `static/` folder.
5. Uploaded reports are stored in `uploads/` and can be downloaded later.

### Core Behavior

- Registration creates a patient account.
- Login stores the session role and user information.
- Patients book tests through a form-driven workflow.
- Admins manage booking status and upload PDF reports.
- Reports are attached to bookings and can be downloaded after upload.

## Folder Guide

### `k8s/`

Contains raw Kubernetes manifests for running the app on a cluster.

- `deployment.yaml` defines the Flask application deployment.
- `service.yaml` exposes the deployment as a NodePort service.

These manifests mirror the current container assumptions: the app listens on port `5000`, uses the `lab-portal:latest` image, and exposes the service on node port `30050`.

### `terraform/`

Contains Terraform infrastructure for provisioning Kubernetes resources with the Kubernetes provider.

- `versions.tf` pins Terraform and provider requirements.
- `providers.tf` configures access to the cluster using kubeconfig.
- `variables.tf` defines reusable inputs like namespace, image, ports, and resource sizing.
- `main.tf` creates the namespace and deployment.
- `service.tf` creates the service.
- `outputs.tf` exports useful resource details.
- `terraform.tfvars.example` provides a sample variable file.
- `.gitignore` keeps generated state and local tfvars out of version control.

Use this folder when you want infrastructure managed declaratively instead of applying YAML directly.

### `elk/`

Contains the local ELK stack used to view logs and inspect service behavior.

- `docker-compose.yml` runs Elasticsearch and Kibana locally.
- `README.md` documents the ELK setup, access URLs, and logging flow.

This folder is intentionally separate so logging observability can be managed without affecting the main application runtime.

### `static/`

Holds all static frontend assets.

- `static/css/style.css` contains the app-specific styling.

### `templates/`

Contains the Jinja2 HTML templates rendered by Flask.

Important pages include:

- `base.html` for the shared layout.
- `login.html` and `register.html` for authentication.
- `patient_dashboard.html` for patient actions and history.
- `book_test.html` for booking lab tests.
- `reports.html` for viewing available reports.
- `admin_dashboard.html` and `admin_bookings.html` for admin operations.
- `upload_report.html` for PDF upload handling.

### `uploads/`

Stores uploaded report PDFs.

- This directory is used at runtime by the Flask app.
- Files here are treated as generated content, not source code.
- Uploaded reports are served back to users through the report download route.

### `instance/`

Flask uses this directory for instance-level data such as the local SQLite database.

- The database file is created here during runtime.
- This folder is environment-specific and may differ between machines.

## Data Model

The project uses three main tables defined in `models.py`:

- `User` stores the login identity, role, and profile information.
- `Booking` stores patient test bookings, status, and visit details.
- `Report` stores uploaded PDF metadata and related booking references.

Relationships are simple and direct:

- One user can have many bookings.
- One booking can have one report.

## Main Workflows

### Patient Workflow

1. Register an account.
2. Log in.
3. Book a lab test.
4. View booking status in the dashboard.
5. Download reports when they become available.

### Admin Workflow

1. Log in with the admin account.
2. Review booking statistics on the admin dashboard.
3. Search and update booking statuses.
4. Upload PDF reports for completed tests.

## Local Setup

### Prerequisites

- Python 3.12 or compatible
- `pip`
- Optional: Docker for container-based execution

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run The App

```bash
python app.py
```

The application will initialize its database on startup if needed and create the `uploads/` folder automatically if it does not already exist.

### Default Admin Account

- Email: `admin@lab.com`
- Password: `admin123`

## Docker Setup

The repository includes a `Dockerfile` for containerizing the Flask application.

### Build The Image

```bash
docker build -t lab-portal:latest .
```

### Run The Container

```bash
docker run -p 5000:5000 lab-portal:latest
```

The container exposes Flask on port `5000`.

## Kubernetes Deployment

If you want to deploy the app to Kubernetes, use the files in `k8s/` or the Terraform resources in `terraform/`.

### Apply The YAML Manifests

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Terraform-Based Provisioning

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## Logging And Observability

The `elk/` directory contains the local Elasticsearch and Kibana environment used for log inspection.

- Elasticsearch stores indexed log data.
- Kibana provides search and visualization.
- The setup is intended for local development and troubleshooting.

See [elk/README.md](elk/README.md) for the full ELK documentation.

## CI Pipeline

The `Jenkinsfile` builds the Docker image and runs a basic verification step to make sure the Python modules compile successfully inside the container.

## Notes On Runtime Files

- `uploads/` and `instance/` are runtime folders and may be populated after the app starts.
- SQLite database files are generated locally and are not part of the application source.
- Terraform state files are local infrastructure artifacts and should not be committed.

## Suggested Validation

Before merging changes, verify the main pieces work together:

```bash
python app.py
docker build -t lab-portal:latest .
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

If you are using the ELK stack, validate it separately from inside `elk/` with:

```bash
docker compose config
docker compose up -d
```
