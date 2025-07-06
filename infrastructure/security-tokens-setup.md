# 🔐 TRAIDER V1 - Security Tokens Setup Guide

**Institutional-Grade Code Quality & Security Analysis Configuration**

## 📋 Overview

This guide covers the setup and management of security tokens required for TRAIDER V1's comprehensive code quality and security analysis pipeline. All tokens are handled with institutional-grade security practices.

### Required Tokens

| Token | Purpose | Criticality | Validation |
|-------|---------|-------------|------------|
| `SONAR_TOKEN` | SonarQube authentication | Critical | Real-time API validation |
| `SEMGREP_APP_TOKEN` | Semgrep cloud integration | High | Format validation |
| `SONARQUBE_DB_PASSWORD` | Database security | Critical | Strength validation |

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# Interactive setup with guided prompts
npm run setup:tokens:interactive

# Generate secure passwords only
npm run setup:tokens:generate

# Validate existing configuration
npm run setup:tokens:validate
```

### Manual Setup

```bash
# View setup instructions
npm run setup:tokens

# Edit environment file directly
cp env.example .env
# Edit .env with your values
```

## 🔑 Token Acquisition

### 1. SonarQube Token (SONAR_TOKEN)

**Prerequisites:**
- SonarQube instance running (local or remote)
- Admin or user account with token generation permissions

**Steps:**

1. **Start SonarQube** (if using local instance):
   ```bash
   docker-compose -f docker-compose.sonarqube.yml up -d
   ```

2. **Access SonarQube Web Interface:**
   - URL: `http://localhost:9000` (or your SonarQube host)
   - Default credentials: `admin/admin` (change immediately)

3. **Generate Token:**
   - Navigate to: **My Account** → **Security** → **Generate Tokens**
   - Token name: `TRAIDER-CI-Token`
   - Token type: `User Token`
   - Expiration: `No expiration` (for CI/CD)
   - Click **Generate**
   - **Copy the token immediately** (shown only once)

4. **Verify Token:**
   ```bash
   # Test token validity
   curl -u YOUR_TOKEN: http://localhost:9000/api/authentication/validate
   ```

### 2. Semgrep Token (SEMGREP_APP_TOKEN)

**Prerequisites:**
- Semgrep account (free tier available)
- Project registered in Semgrep dashboard

**Steps:**

1. **Create Semgrep Account:**
   - Visit: [https://semgrep.dev/](https://semgrep.dev/)
   - Sign up with GitHub/email

2. **Generate Token:**
   - Go to: **Settings** → **Tokens**
   - Click **Create new token**
   - Name: `TRAIDER-V1-CI`
   - Scope: `CI` (minimum required)
   - Click **Create token**
   - **Copy the token** (40+ character hex string)

3. **Verify Token Format:**
   ```bash
   # Should match pattern: ^[a-f0-9]{40,}$
   echo "YOUR_TOKEN" | grep -E '^[a-f0-9]{40,}$'
   ```

### 3. Database Password (SONARQUBE_DB_PASSWORD)

**Security Requirements:**
- Minimum 16 characters (32+ recommended)
- Mix of uppercase, lowercase, numbers, symbols
- No dictionary words or personal information
- Unique to this system

**Generation:**
```bash
# Auto-generate secure password
npm run setup:tokens:generate

# Or use system tools
openssl rand -base64 32
```

## 🏛️ GitHub Repository Configuration

### Adding Secrets to Repository

1. **Navigate to Repository Settings:**
   - Go to: `Repository` → `Settings` → `Secrets and variables` → `Actions`

2. **Add Required Secrets:**

   | Secret Name | Value | Example |
   |-------------|-------|---------|
   | `SONAR_HOST_URL` | SonarQube server URL | `http://localhost:9000` |
   | `SONAR_TOKEN` | SonarQube user token | `squ_abc123...` |
   | `SEMGREP_APP_TOKEN` | Semgrep API token | `1a2b3c4d5e...` |

3. **Verify Configuration:**
   - Secrets should show as "Updated X minutes ago"
   - Never display actual values in logs or UI

### Environment Variables vs Secrets

| Type | Usage | Security Level | Examples |
|------|-------|----------------|----------|
| **Repository Secrets** | CI/CD authentication | High | Tokens, passwords |
| **Environment Variables** | Configuration | Medium | URLs, thresholds |
| **Public Variables** | Non-sensitive config | Low | Feature flags |

## 🔧 Local Development Setup

### Environment File Configuration

1. **Create Local Environment:**
   ```bash
   cp env.example .env
   ```

2. **Configure Required Variables:**
   ```env
   # SonarQube Configuration
   SONAR_HOST_URL=http://localhost:9000
   SONAR_TOKEN=your-sonarqube-token-here
   SONARQUBE_DB_PASSWORD=your-secure-database-password-here
   
   # Security Scanning
   SEMGREP_APP_TOKEN=your-semgrep-token-here
   
   # Quality Gates
   QUALITY_GATE_ENABLED=true
   SECURITY_SCAN_ENABLED=true
   ```

3. **Validate Configuration:**
   ```bash
   npm run setup:tokens:validate
   ```

### Docker Environment

Update `docker-compose.sonarqube.yml` environment:

```yaml
services:
  sonarqube-db:
    environment:
      POSTGRES_PASSWORD: ${SONARQUBE_DB_PASSWORD}
  
  sonarqube:
    environment:
      SONAR_JDBC_PASSWORD: ${SONARQUBE_DB_PASSWORD}
```

## 🧪 Testing & Validation

### Token Validation

```bash
# Comprehensive validation
npm run setup:tokens:validate

# Manual SonarQube test
curl -u $SONAR_TOKEN: $SONAR_HOST_URL/api/authentication/validate

# Manual Semgrep test (requires CLI)
semgrep --config=auto --json app/ --dry-run
```

### Pipeline Testing

1. **Local Quality Analysis:**
   ```bash
   npm run quality:all
   ```

2. **Trigger CI/CD Pipeline:**
   ```bash
   git commit -m "test: validate security tokens configuration"
   git push origin main
   ```

3. **Monitor Results:**
   - GitHub Actions: Repository → Actions
   - SonarQube: `$SONAR_HOST_URL/dashboard`
   - Security: Repository → Security → Code scanning alerts

## 🛡️ Security Best Practices

### Token Management

1. **Rotation Policy:**
   - SonarQube tokens: Every 90 days
   - Semgrep tokens: Every 180 days
   - Database passwords: Every 30 days

2. **Access Control:**
   - Limit token permissions to minimum required
   - Use dedicated service accounts
   - Monitor token usage in audit logs

3. **Storage Security:**
   - Never commit tokens to version control
   - Use GitHub Secrets for CI/CD
   - Encrypt local environment files

### Monitoring & Auditing

```bash
# Check token usage
grep -r "SONAR_TOKEN\|SEMGREP_APP_TOKEN" .github/workflows/

# Audit environment variables
npm run setup:tokens:validate > security-audit.log
```

## 🚨 Troubleshooting

### Common Issues

#### SonarQube Token Issues

**Problem:** `401 Unauthorized`
```bash
# Check token format
echo $SONAR_TOKEN | grep -E '^squ_[a-f0-9]{40}$'

# Verify host connectivity
curl -I $SONAR_HOST_URL/api/system/status
```

**Solution:**
- Regenerate token in SonarQube UI
- Verify SONAR_HOST_URL is accessible
- Check firewall/network restrictions

#### Semgrep Token Issues

**Problem:** `Invalid token format`
```bash
# Validate token format
echo $SEMGREP_APP_TOKEN | grep -E '^[a-f0-9]{40,}$'
```

**Solution:**
- Regenerate token in Semgrep dashboard
- Ensure token has 'CI' scope
- Check for extra spaces or characters

#### Database Connection Issues

**Problem:** `Connection refused`
```bash
# Check database container
docker-compose -f docker-compose.sonarqube.yml ps

# Verify password
docker-compose -f docker-compose.sonarqube.yml logs sonarqube-db
```

**Solution:**
- Regenerate SONARQUBE_DB_PASSWORD
- Restart database containers
- Check Docker network connectivity

### Emergency Procedures

#### Token Compromise

1. **Immediate Actions:**
   ```bash
   # Revoke compromised tokens
   # SonarQube: My Account → Security → Revoke
   # Semgrep: Settings → Tokens → Delete
   
   # Generate new tokens
   npm run setup:tokens:interactive
   ```

2. **Update All Environments:**
   - Local `.env` file
   - GitHub repository secrets
   - Production deployments

3. **Audit & Monitor:**
   - Review access logs
   - Monitor for unauthorized usage
   - Update security documentation

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Daily validation
npm run setup:tokens:validate

# Weekly security audit
npm run security:scan:comprehensive

# Monthly token rotation check
grep -E "(SONAR_TOKEN|SEMGREP_APP_TOKEN)" .env | \
  xargs -I {} echo "Review token: {}"
```

### Performance Monitoring

| Metric | Threshold | Action |
|--------|-----------|--------|
| SonarQube response time | >5s | Check server resources |
| Semgrep scan duration | >10min | Review ruleset complexity |
| Token validation failures | >5% | Investigate network/auth issues |

## 📚 Additional Resources

### Documentation Links

- [SonarQube Token Documentation](https://docs.sonarqube.org/latest/user-guide/user-token/)
- [Semgrep CI/CD Integration](https://semgrep.dev/docs/semgrep-ci/)
- [GitHub Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

### Support Contacts

- **Security Issues:** Create issue with `security` label
- **Token Problems:** Check troubleshooting section first
- **Emergency:** Follow incident response procedures

---

## 🎯 Completion Checklist

- [ ] All tokens acquired and validated
- [ ] GitHub repository secrets configured
- [ ] Local environment file updated
- [ ] SonarQube instance accessible
- [ ] Semgrep integration tested
- [ ] CI/CD pipeline validated
- [ ] Security monitoring enabled
- [ ] Documentation reviewed
- [ ] Team access configured
- [ ] Backup procedures documented

**Next Steps:** Proceed to [Code Quality Pipeline](./code-quality-pipeline.md) for comprehensive analysis setup. 