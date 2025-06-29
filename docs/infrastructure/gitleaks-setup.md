# GitLeaks License Setup Guide

## Overview
GitLeaks provides secret scanning capabilities for TRAIDER V1. While GitLeaks has an open-source version, GitHub organizations require a license key for advanced features and organization-level scanning.

## Setup Instructions

### 1. Obtain GitLeaks License
1. Visit [gitleaks.io](https://gitleaks.io)
2. Sign up for an organization license
3. Obtain your license key

### 2. Configure GitHub Secrets
1. Go to your GitHub repository settings
2. Navigate to **Settings > Secrets and variables > Actions**
3. Click **New repository secret**
4. Name: `GITLEAKS_LICENSE`
5. Value: Your GitLeaks license key
6. Click **Add secret**

### 3. Local Development Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your license key:
   ```bash
   GITLEAKS_LICENSE=your-actual-license-key-here
   ```

3. The `.env` file is automatically ignored by git for security

## Verification

### GitHub Actions
Once the `GITLEAKS_LICENSE` secret is configured, the security workflow will:
- ✅ Run GitLeaks secret scanning without license errors
- ✅ Upload results to GitHub Security tab
- ✅ Block deployments if secrets are detected

### Local Testing
You can test GitLeaks locally:
```bash
# Install GitLeaks
brew install gitleaks  # macOS
# or
curl -sSfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh  # Linux

# Run scan with license
GITLEAKS_LICENSE=your-license-key gitleaks detect --source . --verbose
```

## Troubleshooting

### License Error in CI/CD
If you see errors like:
```
Error: missing gitleaks license
```

**Solution:**
1. Verify the `GITLEAKS_LICENSE` secret is set in GitHub repository settings
2. Ensure the license key is valid and not expired
3. Check that the license supports organization-level scanning

### Local Development Issues
If GitLeaks fails locally:
1. Ensure `.env` file exists with correct `GITLEAKS_LICENSE` value
2. Verify the license key format (no extra spaces or characters)
3. Test with a simple command: `echo $GITLEAKS_LICENSE`

## Security Best Practices

### License Key Protection
- ✅ Store license in GitHub Secrets (encrypted)
- ✅ Use `.env` for local development (gitignored)
- ❌ Never commit license keys to repository
- ❌ Never share license keys in plain text

### Scanning Coverage
GitLeaks scans for:
- API keys and tokens
- Database credentials
- Cryptographic keys
- Authentication secrets
- Trading platform credentials

## Support
- [GitLeaks Documentation](https://github.com/gitleaks/gitleaks)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- Internal: Contact DevOps team for license management 