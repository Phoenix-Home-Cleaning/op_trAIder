# 🌐 GitHub Pages Setup & Troubleshooting

*TRAIDER V1 Documentation Deployment Guide*

## 📋 Overview

This guide covers the setup and troubleshooting of GitHub Pages deployment for TRAIDER documentation, including the resolution of the `peaceiris/actions-gh-pages` permission issues.

## 🔧 Repository Setup

### 1. Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Set **Source** to "Deploy from a branch"
3. Select **Branch**: `gh-pages` 
4. Select **Folder**: `/ (root)`
5. Click **Save**

### 2. Configure Repository Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**

### 3. Optional: Custom Domain

If using a custom domain (e.g., `docs.traider.app`):

1. Go to **Settings** → **Pages**
2. Enter custom domain in **Custom domain** field
3. Enable **Enforce HTTPS**

## 🚨 Common Issues & Solutions

### Issue 1: Permission Denied (403 Error)

**Symptom**:
```
remote: Permission to Phoenix-Home-Cleaning/op_trAIder.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/...': The requested URL returned error: 403
```

**Root Cause**: Insufficient permissions for `GITHUB_TOKEN`

**Solution Applied** ✅:
```yaml
# Workflow-level permissions
permissions:
  contents: write
  pages: write
  id-token: write

# Job-level permissions
jobs:
  generate-docs:
    permissions:
      contents: write
      pages: write
      id-token: write
```

### Issue 2: peaceiris/actions-gh-pages Version Issues

**Solution Applied** ✅:
```yaml
- name: 🌐 Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v4  # Updated from v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
    enable_jekyll: false
    force_orphan: true  # Clean gh-pages branch
```

### Issue 3: tsx Command Not Found

**Symptom**:
```
/usr/bin/tsx: command not found
Error: Process completed with exit code 127
```

**Root Cause**: Missing `npx` prefix for tsx commands in CI environment

**Solution Applied** ✅:
```yaml
# Before (fails in CI)
- run: tsx scripts/validate-docs.ts

# After (works in CI)
- run: npx tsx scripts/validate-docs.ts
```

### Issue 4: Documentation Not Updating

**Possible Causes**:
- Workflow only runs on `main` branch pushes
- Documentation generation failed
- Caching issues
- Permission issues (see Issue 1)

**Troubleshooting Steps**:
1. Check **Actions** tab for workflow status
2. Verify push was to `main` branch
3. Check workflow logs for errors
4. Clear browser cache for documentation site
5. Verify repository permissions (see Issue 1)

## 📊 Workflow Configuration

### Current Workflow Features

✅ **Automated Documentation Generation**:
- TypeDoc API documentation
- Architecture diagrams (Mermaid)
- OpenAPI specifications
- Performance benchmarks
- Coverage reports

✅ **Deployment Strategy**:
- Only deploys from `main` branch
- Validates documentation before deployment
- Uploads artifacts for debugging
- Proper error handling and rollback

✅ **Performance Optimizations**:
- npm cache for faster builds
- Conditional deployment (main branch only)
- Artifact retention policies
- Parallel job execution where possible

### Workflow Triggers

```yaml
on:
  push:
    branches: [main, develop]  # Validates on both, deploys only main
  pull_request:
    branches: [main]           # Validates PRs
  schedule:
    - cron: '0 2 * * *'        # Daily validation at 2 AM UTC
```

## 🔍 Monitoring & Debugging

### 1. Check Workflow Status

Visit: `https://github.com/Phoenix-Home-Cleaning/op_trAIder/actions`

### 2. Common Log Locations

- **Documentation Generation**: `generate-docs` job logs
- **Deployment**: Look for "Deploy to GitHub Pages" step
- **Validation**: `validate-docs` job for pre-deployment checks

### 3. Artifact Downloads

Available artifacts after each run:
- `generated-documentation`: Complete docs folder
- `documentation-validation-results`: Coverage reports
- `performance-reports`: Benchmark results

## 🎯 Best Practices

### 1. Documentation Quality

- Maintain 95%+ JSDoc coverage
- Validate all code examples
- Keep internal links updated
- Regular documentation audits

### 2. Deployment Safety

- Always validate before deployment
- Use staging branches for major changes
- Monitor deployment success
- Keep rollback procedures ready

### 3. Performance

- Optimize image sizes in documentation
- Use appropriate caching strategies
- Monitor build times
- Regular dependency updates

## 🔄 Manual Deployment

If automatic deployment fails, manual deployment options:

### Option 1: Re-run Workflow
1. Go to **Actions** tab
2. Select failed workflow
3. Click **Re-run all jobs**

### Option 2: Local Generation + Push
```bash
# Generate documentation locally
npm run docs:generate

# Manual deployment (if needed)
git checkout gh-pages
cp -r docs/* .
git add -A
git commit -m "Manual documentation update"
git push origin gh-pages
git checkout main
```

## 📈 Success Metrics

After successful setup, expect:

- ✅ Documentation updates within 2-3 minutes of main branch pushes
- ✅ 99%+ deployment success rate
- ✅ Comprehensive documentation coverage
- ✅ Fast loading documentation site
- ✅ Mobile-responsive documentation

## 🆘 Emergency Contacts

If critical documentation deployment issues occur:

1. **Check GitHub Status**: https://www.githubstatus.com/
2. **Repository Issues**: Create issue with `documentation` label
3. **Escalation**: Contact repository administrators

---

> **Note**: This configuration was tested and verified as of the latest commit.
> The workflow should now successfully deploy documentation without permission issues. 