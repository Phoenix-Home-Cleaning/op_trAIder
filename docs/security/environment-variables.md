# 🔐 Environment Variables Security Guide

## Overview

This document outlines the required environment variables for TRAIDER V1 and provides security best practices for managing sensitive configuration data.

## ⚠️ Critical Security Requirements

### Required Environment Variables

The following environment variables **MUST** be set for the application to start:

```bash
# JWT Authentication (REQUIRED)
SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Dashboard Authentication (REQUIRED)  
DASHBOARD_PASSWORD=your-secure-dashboard-password-change-in-production
```

**⚠️ WARNING**: The application will fail to start if these variables are not set. This is intentional for security.

## 🔑 Security Best Practices

### 1. Strong Secret Generation

Generate cryptographically secure secrets:

```bash
# Generate SECRET_KEY (256-bit)
openssl rand -hex 32

# Generate DASHBOARD_PASSWORD (strong password)
openssl rand -base64 32
```

### 2. Environment Variable Management

#### Development
```bash
# Copy example file
cp backend/env.example backend/.env

# Edit with secure values
nano backend/.env
```

#### Production
- Use container orchestration secrets (Kubernetes secrets, Docker secrets)
- Use cloud provider secret managers (AWS Secrets Manager, Azure Key Vault)
- Never commit secrets to version control

### 3. Access Control

- Limit access to environment files
- Use proper file permissions (600)
- Rotate secrets regularly

```bash
# Secure file permissions
chmod 600 backend/.env
```

## 📋 Complete Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | `a1b2c3d4e5f6...` |
| `DASHBOARD_PASSWORD` | Dashboard access password | `SecurePass123!` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GUEST_PASSWORD` | Guest access password | `""` (disabled) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `60` |

## 🚨 Security Incidents

### Compromised Secrets

If secrets are compromised:

1. **Immediately** rotate all affected secrets
2. Update environment variables in all environments
3. Restart all services
4. Review access logs for unauthorized activity
5. Notify security team

### Emergency Access

For emergency access without environment variables:

1. Use emergency access procedures documented in `docs/security/emergency-access.md`
2. Set temporary environment variables
3. Immediately rotate secrets after incident

## 🔍 Validation

The application performs startup validation:

```python
# Validates required environment variables
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set for security")
    
if not DASHBOARD_PASSWORD:
    raise ValueError("DASHBOARD_PASSWORD environment variable must be set for security")
```

## 📖 Related Documentation

- [Authentication Architecture](../architecture/authentication.md)
- [Security Scanning](./security-scanning.md)
- [Emergency Access Procedures](./emergency-access.md)

---

**⚠️ CRITICAL**: Never commit actual secrets to version control. Always use placeholder values in example files. 