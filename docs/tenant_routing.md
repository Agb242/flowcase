# Nginx Tenant‑Aware Routing

*Placeholder for Nginx configuration to support multi‑tenant routing.*

The goal is to route requests based on subdomains (e.g., `tenant1.myapp.com`, `tenant2.myapp.com`) to the appropriate tenant context within the Flask application. This will involve:

1. Configuring Nginx server blocks with wildcard subdomains.
2. Passing the tenant identifier to the Flask app via a request header or URL parameter.
3. Modifying Flask middleware to resolve the tenant from the request and set the appropriate database schema or tenant context.
4. Ensuring security isolation between tenants.

Implementation details will be added as the feature is developed.