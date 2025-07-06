# ADR-006: Environment Configuration Consolidation

**Status**: ✅ Accepted  
**Date**: 2025-06-29 
**Deciders**: TRAIDER Development Team  
**Technical Story**: Environment file management simplification  

---

## Context

During Phase 0 development, environment variables were managed separately:
- Backend environment variables in `/backend/.env` and `/backend/env.example`
- Frontend environment variables expected in root directory
- Duplicate configuration management across multiple locations
- Complex setup procedures requiring multiple environment files

This created operational complexity and potential for configuration drift between frontend and backend environments.

## Decision

**DECISION**: Consolidate all environment variables into a single root-level configuration:
- Move `/backend/.env` → `/.env`
- Move `/backend/env.example` → `/.env.example`
- Update all scripts, documentation, and infrastructure to reference root-level files
- Maintain single source of truth for all environment configuration

## Rationale

### ✅ **Benefits**
1. **Simplified Setup**: Single environment file for entire application
2. **Reduced Complexity**: Eliminate duplicate configuration management
3. **Better DX**: Developers manage one file instead of multiple
4. **Consistency**: Unified approach across frontend and backend
5. **Easier CI/CD**: Single environment file for deployment pipelines
6. **Reduced Errors**: Less chance of configuration drift

### ⚠️ **Trade-offs**
1. **File Size**: Larger single file vs. smaller specialized files
2. **Scope Mixing**: Frontend and backend variables in same file
3. **Migration Effort**: Update existing documentation and scripts

## Implementation

### Files Updated
- **Scripts**: `create-env.ps1`, `generate-secrets.ps1`, `setup-phase0.ps1`, `test-coinbase-api.py`
- **Documentation**: `environment-variables.md`, `coinbase-api-setup.md`, `gitleaks-setup.md`
- **Infrastructure**: Docker configurations, Kubernetes manifests
- **Testing**: Environment setup in test configurations

### Structure
```bash
# Root directory structure
/.env                    # All environment variables (gitignored)
/.env.example           # Template with all required variables
/backend/               # No environment files
/app/                   # No environment files
```

### Security Considerations
- Root `.env` file properly gitignored
- All sensitive variables documented in `.env.example`
- File permissions guidance updated in documentation
- Security scanning patterns updated

## Consequences

### ✅ **Positive**
- **Developer Experience**: Faster setup, single configuration point
- **Operational Simplicity**: Unified environment management
- **Documentation Clarity**: Single source of truth for environment setup
- **CI/CD Efficiency**: Simplified deployment configuration

### ⚠️ **Monitoring Required**
- **File Size Growth**: Monitor .env file size as application grows
- **Variable Organization**: May need sections/comments for clarity
- **Access Patterns**: Ensure both frontend and backend can access variables appropriately

### 🔄 **Future Considerations**
- **Phase 2+**: Consider environment-specific files (`.env.dev`, `.env.prod`)
- **Microservices**: May need service-specific environment files
- **Secret Management**: Integration with HashiCorp Vault or cloud secret managers

## Compliance & Audit

### Security Impact
- **Risk Level**: LOW - Configuration change only
- **Audit Trail**: All changes documented in git history
- **Access Control**: Same security model applies to root-level file

### Documentation Impact
- **Updated**: 15+ files across documentation, scripts, and infrastructure
- **Validated**: All references tested and verified
- **Comprehensive**: Complete migration with no broken references

---

**Implementation Status**: ✅ **COMPLETE**  
**Validation**: All scripts and documentation updated and tested  
**Next Review**: Phase 1 completion (evaluate if additional environment management needed)

---

*This ADR documents a foundational infrastructure decision that improves developer experience and operational simplicity while maintaining security and institutional standards.* 