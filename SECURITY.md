# Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please report it to the repository owner directly rather than creating a public issue.

## Security Best Practices

### Environment Variables
- **Never commit `.env` files** - they are in `.gitignore`
- **Never hardcode API keys** in source code
- **Use environment variables** for all secrets (GITHUB_TOKEN, etc.)
- **Rotate tokens immediately** if accidentally exposed

### GitHub Repository Security Settings

Enable these features in GitHub repository settings:

1. **Secret scanning** (Settings → Security → Code security and analysis)
   - Enable "Secret scanning"
   - Enable "Push protection"

2. **Dependabot** (Settings → Security → Code security and analysis)
   - Enable "Dependabot alerts"
   - Enable "Dependabot security updates"

3. **Branch protection** (Settings → Branches)
   - Protect `main` branch
   - Require pull request reviews
   - Require status checks to pass

### Production Deployment Security

#### Required Steps Before Deployment:
- [ ] Set all secrets in deployment platform (Cloud Run, Azure, etc.)
- [ ] Use Secret Manager (GCP Secret Manager, Azure Key Vault, etc.)
- [ ] Never set secrets in Dockerfile or docker-compose
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Add rate limiting to API endpoints
- [ ] Implement request authentication (API keys or OAuth)
- [ ] Set up CORS policies
- [ ] Enable security headers (CSP, HSTS, X-Frame-Options)
- [ ] Disable debug mode in production
- [ ] Use production WSGI server (Gunicorn)
- [ ] Configure logging without exposing sensitive data
- [ ] Set up monitoring and alerting
- [ ] Regular security audits and dependency updates

#### Environment Variables for Production:
```bash
# Required
GITHUB_TOKEN=<your_github_token>

# Optional - Production configuration
CACHE_DIR=/app/cache
CHROMA_PERSIST_DIRECTORY=/app/cache/chroma_db
FLASK_ENV=production
LOG_LEVEL=INFO
MAX_WORKERS=4
REQUEST_TIMEOUT=30
```

#### Secrets Management Examples:

**Google Cloud Run with Secret Manager:**
```bash
# Store secret
echo -n "your_token" | gcloud secrets create github-token --data-file=-

# Deploy with secret
gcloud run deploy knowledge-rag \
  --set-secrets GITHUB_TOKEN=github-token:latest
```

**Azure Web App:**
```bash
# Set environment variable
az webapp config appsettings set \
  --name knowledge-rag \
  --resource-group myResourceGroup \
  --settings GITHUB_TOKEN=@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/github-token/)
```

**Docker (development only - use secrets in production):**
```bash
# Never do this in production!
docker run -e GITHUB_TOKEN=${GITHUB_TOKEN} knowledge-rag

# Production: use Docker secrets or external secret management
```

### API Security

#### Rate Limiting
The `/api/ask` endpoint should implement rate limiting:
- Limit: 10 requests per minute per IP
- Use Redis or in-memory store for tracking
- Return HTTP 429 when limit exceeded

#### Authentication (recommended for production)
Add API key authentication:
```python
# Example middleware
@app.before_request
def require_api_key():
    if request.path.startswith('/api/'):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
```

### Data Security

#### Vector Database
- **ChromaDB persistence**: Ensure persistent storage is on encrypted volumes
- **Backup strategy**: Regular exports to secure cloud storage
- **Access control**: Limit file system access to application user only

#### Logs
- Never log API keys, tokens, or user credentials
- Sanitize query strings before logging
- Use structured logging with appropriate log levels
- Secure log storage and implement log retention policies

### Dependency Security

Run regular security audits:
```bash
# Python dependencies
pip install safety
safety check

# Or use pip-audit
pip install pip-audit
pip-audit

# Check for outdated packages
pip list --outdated
```

### Docker Security

- Use official base images (`python:3.13-slim`)
- Don't run as root user
- Scan images for vulnerabilities:
  ```bash
  docker scan knowledge-rag:latest
  ```
- Keep base images updated
- Use multi-stage builds to reduce attack surface
- Don't include secrets in image layers

## Security Checklist

### Before Going Public:
- [x] `.env` in `.gitignore`
- [x] No hardcoded secrets in code
- [x] `.env.example` provided without real values
- [x] Security policy documented
- [ ] GitHub secret scanning enabled
- [ ] Dependabot alerts enabled
- [ ] Branch protection configured

### Before Production Deployment:
- [ ] All secrets in secure secret manager
- [ ] HTTPS/TLS enabled
- [ ] Rate limiting implemented
- [ ] API authentication added
- [ ] CORS configured
- [ ] Security headers set
- [ ] Debug mode disabled
- [ ] Production WSGI server configured
- [ ] Logging configured (no sensitive data)
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] Security audit completed
- [ ] Dependency vulnerabilities resolved

## Security Contact

For security-related questions or to report vulnerabilities, please contact the repository owner.

## Updates

This security policy will be updated as new security measures are implemented or as threats evolve.

Last updated: October 25, 2025
