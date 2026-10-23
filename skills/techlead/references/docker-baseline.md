# Docker Baseline

Use this reference when writing the environments and Docker sections of the SPEC and the Docker tasks in TASKS. Adapt the commands and services to the selected stack. The requirements are mandatory; the examples are illustrative.

## Local and test environment

### Required outcomes

- A new contributor can start the stack from a clean checkout using one documented command.
- The test suite runs inside a container with the same runtime version used by CI.
- Production credentials and production data are never required.
- The stack exposes healthchecks and fails fast when a dependency is unavailable.
- Data persists across restarts when the product needs local persistence.
- A documented reset command removes local state safely.

### Recommended files

```text
Dockerfile.dev
compose.local.yml
.env.example
scripts/dev-up.sh
scripts/dev-test.sh
scripts/dev-reset.sh
.dockerignore
```

### Development service

- Use a development target or a dedicated development image.
- Install development dependencies explicitly.
- Mount source code for hot reload or use a fast rebuild path.
- Run the application as a non-root user when the framework supports it.
- Bind to all interfaces inside the container, not only loopback.
- Expose only the ports needed for local development.
- Add a healthcheck that reflects real readiness, not only process existence.
- Keep dependency startup ordered with `depends_on` and health conditions.
- Pass configuration through environment variables with safe local defaults.

### Test service

- Run unit, integration, and end-to-end suites in a dedicated service or profile.
- Use a disposable database or schema for integration tests.
- Make tests deterministic: fixed clocks, seeded randomness, isolated data, and no shared mutable state.
- Produce a coverage report and fail below the configured gate.
- Export the coverage artifact from the container for CI and review.
- Provide one command for the full gate and one for a focused test file.

### Example local commands

```bash
docker compose -f compose.local.yml up --build
docker compose -f compose.local.yml run --rm tests
docker compose -f compose.local.yml run --rm tests pytest --cov --cov-fail-under=80
docker compose -f compose.local.yml down --volumes
```

### Local security boundaries

- Use separate local secrets and dummy credentials.
- Do not mount the Docker socket into application containers.
- Do not run privileged containers.
- Do not expose the database publicly unless the product requires it and the risk is documented.
- Pin image versions instead of relying on floating tags.

## Production environment on a VPS

### Required outcomes

- The production image is reproducible, minimal, and runs as a non-root user.
- Secrets are injected at runtime and are not present in the image, Git history, or logs.
- The public entry point uses TLS and a reverse proxy.
- The host is hardened and monitored.
- Deployments are repeatable, observable, and reversible.
- Backups exist and a restore has been tested.

### Image build

```dockerfile
FROM node:22.14.0-bookworm-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22.14.0-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home /app app
COPY --from=build --chown=app:app /app/dist ./dist
COPY --from=build --chown=app:app /app/node_modules ./node_modules
COPY --from=build --chown=app:app /app/package.json ./package.json
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
ENTRYPOINT ["node", "dist/server.js"]
```

Adapt the base image and commands to the real stack. Pin the base image by version or digest. Keep build tools out of the final stage. Copy only runtime artifacts. Add a `.dockerignore` that excludes `.git`, tests, local environments, credentials, caches, and build output not needed at runtime.

### Compose production service

- Use a dedicated Compose project name.
- Reference secrets through files or an external secret manager, not literal values.
- Run with `read_only: true` when the application does not need to write to its root filesystem.
- Mount explicit writable paths with `tmpfs` or named volumes.
- Set `cap_drop: [ALL]`.
- Set `security_opt: [no-new-privileges:true]`.
- Set CPU and memory limits.
- Set `restart: unless-stopped`.
- Add a healthcheck.
- Configure log rotation with `max-size` and `max-file`.
- Put the application behind a reverse proxy on a private network.
- Do not publish the application port directly to the host unless required.

### Reverse proxy and TLS

- Use Caddy, Traefik, or Nginx with automatic certificate management.
- Redirect HTTP to HTTPS.
- Set secure headers: HSTS, content type protection, frame policy, referrer policy, and a content security policy appropriate to the app.
- Limit request body size and timeouts.
- Preserve client IP only through trusted proxies.
- Restrict the admin surface by network or strong authentication when possible.

### VPS host hardening

- Use a supported Linux distribution with automatic security updates.
- Create a dedicated deployment user with least privilege.
- Disable password SSH and root login.
- Require key-based SSH.
- Restrict inbound ports to SSH, HTTP, and HTTPS; restrict SSH by network when possible.
- Enable a host firewall.
- Enable intrusion prevention such as fail2ban for SSH.
- Keep Docker and the host patched.
- Set timezone and clock synchronization.
- Configure disk usage alerts.
- Store backups outside the VPS.
- Document how to rebuild the host from scratch.

### Secrets

- Use Docker secrets, the VPS secret manager, or a dedicated secret store.
- Inject secrets at runtime.
- Never commit `.env` files with real values.
- Rotate secrets after exposure and on a defined schedule for high-risk credentials.
- Do not print secrets in logs, error messages, health endpoints, or CI output.
- Limit secret access to the services that need it.

### Observability

- Structured application logs with request IDs and no sensitive fields.
- Health and readiness endpoints.
- Metrics for traffic, errors, latency, saturation, queue depth, and dependency health.
- Alerts for availability, error rate, latency, disk, memory, certificate expiry, backup failure, and deployment failure.
- Log rotation and retention.
- A dashboard or at least a documented query set for the primary signals.

### Backup and restore

- Define what is backed up, how often, where it is stored, and how long it is retained.
- Encrypt backups at rest and in transit.
- Test restore on a schedule.
- Record the restore time and the acceptable data loss window.
- Back up configuration and secrets separately from application data.

### Deployment and rollback

- Build and tag images with an immutable version or commit SHA.
- Push to a registry with access control.
- Deploy with a single documented command or workflow.
- Run migrations as an explicit step with a rollback plan.
- Run a smoke test after deployment.
- Keep the previous image available.
- Test rollback to the previous image and confirm data compatibility.
- Record deployment evidence: version, operator, time, smoke result, and rollback result.

### Image and dependency scanning

- Scan the production image for operating system and application vulnerabilities.
- Fail the gate on unresolved critical findings.
- Define an exception process with owner, justification, and expiry for accepted high findings.
- Scan dependencies and lockfiles in CI.
- Rebuild regularly to pick up base image security updates.

## Stack profiles

### Web application

- Build the frontend in a build stage and serve static assets from the reverse proxy or a minimal runtime.
- Keep API and frontend versions aligned.
- Add cache headers and compression at the proxy.
- Test the production build, not only the development server.

### API or backend service

- Run migrations before or during startup with a controlled strategy.
- Expose health and readiness endpoints.
- Configure connection pool limits.
- Handle graceful shutdown.
- Add request timeouts and body limits.

### Worker or scheduler

- Run one process per container.
- Make jobs idempotent.
- Add retry, backoff, and dead-letter handling.
- Add a health signal that reflects queue progress.
- Avoid running multiple schedulers without a leader lock.

### Database

- Use a managed database when the budget allows.
- Otherwise run a pinned database image with a persistent volume, backup, and restore procedure.
- Do not expose the database port publicly.
- Apply least-privilege database users.
- Test migrations against a production-like dataset.

### Static site

- Build once and serve immutable artifacts.
- Use a minimal web server with security headers.
- Cache fingerprinted assets for a long time and HTML for a short time.
- Add a healthcheck and a deployment smoke test.

## Definition-of-done evidence

Record evidence for:

- local stack start and test run;
- coverage report at or above 80 percent;
- production image build;
- image scan result;
- VPS deployment and smoke test;
- rollback result;
- backup and restore result;
- alert test result;
- security review result;
- updated runbook and release notes.
