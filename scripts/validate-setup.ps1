#!/usr/bin/env powershell

<#
.SYNOPSIS
    TRAIDER V1 - Setup Validation Script

.DESCRIPTION
    Validates the complete security tokens and code quality infrastructure setup.
    Checks local configuration, GitHub secrets, and CI/CD pipeline readiness.

.PARAMETER CheckLocal
    Validate local environment configuration only

.PARAMETER CheckSecrets
    Validate GitHub repository secrets (requires GitHub CLI)

.PARAMETER CheckWorkflow
    Validate GitHub Actions workflow configuration

.EXAMPLE
    .\scripts\validate-setup.ps1 -CheckLocal
    .\scripts\validate-setup.ps1 -CheckSecrets
    .\scripts\validate-setup.ps1 -CheckWorkflow

.NOTES
    Author: TRAIDER Team
    Version: 1.0.0-alpha
    Requires: PowerShell 5.1+, GitHub CLI (optional)
#>

param(
    [switch]$CheckLocal,
    [switch]$CheckSecrets,
    [switch]$CheckWorkflow,
    [switch]$All
)

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Info    = "Cyan"
    Header  = "Magenta"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-FileExists {
    param([string]$Path, [string]$Description)
    
    if (Test-Path $Path) {
        Write-ColorOutput "✅ $Description exists: $Path" "Success"
        return $true
    } else {
        Write-ColorOutput "❌ $Description missing: $Path" "Error"
        return $false
    }
}

function Test-EnvironmentVariable {
    param([string]$Name, [string]$Description, [switch]$Required)
    
    $value = [Environment]::GetEnvironmentVariable($Name)
    if (-not $value -and (Test-Path ".env")) {
        $envContent = Get-Content ".env"
        foreach ($line in $envContent) {
            if ($line -match "^$Name=(.+)$") {
                $value = $matches[1]
                break
            }
        }
    }
    
    if ($value) {
        if ($Name -like "*PASSWORD*" -or $Name -like "*TOKEN*" -or $Name -like "*SECRET*") {
            Write-ColorOutput "✅ $Description configured (value hidden)" "Success"
        } else {
            Write-ColorOutput "✅ ${Description}: $value" "Success"
        }
        return $true
    } else {
        if ($Required) {
            Write-ColorOutput "❌ $Description not configured" "Error"
        } else {
            Write-ColorOutput "⚠️ $Description not configured (optional)" "Warning"
        }
        return $false
    }
}

function Test-LocalConfiguration {
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🔍 VALIDATING LOCAL CONFIGURATION" "Header"
    Write-ColorOutput "=================================" "Header"
    
    $localValid = $true
    
    # Check critical files
    $criticalFiles = @(
        @{ Path = ".env.example"; Description = "Environment template" },
        @{ Path = ".qlty.toml"; Description = "Qlty configuration" },
        @{ Path = "sonar-project.properties"; Description = "SonarQube project config" },
        @{ Path = "docker-compose.sonarqube.yml"; Description = "SonarQube Docker compose" },
        @{ Path = ".github/workflows/code-quality.yml"; Description = "Code quality workflow" },
        @{ Path = "scripts/setup-security-tokens.ps1"; Description = "Token setup script" }
    )
    
    Write-ColorOutput "📁 Critical Files:" "Info"
    foreach ($file in $criticalFiles) {
        if (-not (Test-FileExists $file.Path $file.Description)) {
            $localValid = $false
        }
    }
    
    # Check environment variables
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🔧 Environment Variables:" "Info"
    
    $envVars = @(
        @{ Name = "SONAR_HOST_URL"; Description = "SonarQube host URL"; Required = $true },
        @{ Name = "SONAR_TOKEN"; Description = "SonarQube authentication token"; Required = $true },
        @{ Name = "SONARQUBE_DB_PASSWORD"; Description = "SonarQube database password"; Required = $true },
        @{ Name = "SEMGREP_APP_TOKEN"; Description = "Semgrep cloud token"; Required = $false },
        @{ Name = "QLTY_CONFIG_FILE"; Description = "Qlty configuration file"; Required = $false }
    )
    
    foreach ($var in $envVars) {
        $result = if ($var.Required) {
            Test-EnvironmentVariable $var.Name $var.Description -Required
        } else {
            Test-EnvironmentVariable $var.Name $var.Description
        }
        
        if (-not $result -and $var.Required) {
            $localValid = $false
        }
    }
    
    # Check Docker availability
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🐳 Docker Environment:" "Info"
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-ColorOutput "✅ Docker available: $dockerVersion" "Success"
        } else {
            Write-ColorOutput "❌ Docker not available" "Error"
            $localValid = $false
        }
    } catch {
        Write-ColorOutput "❌ Docker not available: $_" "Error"
        $localValid = $false
    }
    
    # Check Node.js and npm
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📦 Node.js Environment:" "Info"
    try {
        $nodeVersion = node --version 2>$null
        $npmVersion = npm --version 2>$null
        if ($nodeVersion -and $npmVersion) {
            Write-ColorOutput "✅ Node.js: $nodeVersion" "Success"
            Write-ColorOutput "✅ npm: $npmVersion" "Success"
        } else {
            Write-ColorOutput "❌ Node.js or npm not available" "Error"
            $localValid = $false
        }
    } catch {
        Write-ColorOutput "❌ Node.js environment error: $_" "Error"
        $localValid = $false
    }
    
    return $localValid
}

function Test-GitHubSecrets {
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🔐 VALIDATING GITHUB SECRETS" "Header"
    Write-ColorOutput "=============================" "Header"
    
    # Check if GitHub CLI is available
    try {
        $ghVersion = gh --version 2>$null
        if (-not $ghVersion) {
            Write-ColorOutput "⚠️ GitHub CLI not available - cannot validate secrets" "Warning"
            Write-ColorOutput "Install GitHub CLI: https://cli.github.com/" "Info"
            return $false
        }
        Write-ColorOutput "✅ GitHub CLI available" "Success"
    } catch {
        Write-ColorOutput "⚠️ GitHub CLI not available - cannot validate secrets" "Warning"
        return $false
    }
    
    $secretsValid = $true
    $requiredSecrets = @(
        "SONAR_HOST_URL",
        "SONAR_TOKEN",
        "SEMGREP_APP_TOKEN"
    )
    
    $optionalSecrets = @(
        "SONARQUBE_DB_PASSWORD"
    )
    
    Write-ColorOutput "🔍 Checking required secrets..." "Info"
    foreach ($secret in $requiredSecrets) {
        try {
            $result = gh secret list --json name | ConvertFrom-Json
            $secretExists = $result | Where-Object { $_.name -eq $secret }
            
            if ($secretExists) {
                Write-ColorOutput "✅ $secret configured" "Success"
            } else {
                Write-ColorOutput "❌ $secret not configured" "Error"
                $secretsValid = $false
            }
        } catch {
            Write-ColorOutput "❌ Failed to check secret $secret : $_" "Error"
            $secretsValid = $false
        }
    }
    
    Write-ColorOutput "🔍 Checking optional secrets..." "Info"
    foreach ($secret in $optionalSecrets) {
        try {
            $result = gh secret list --json name | ConvertFrom-Json
            $secretExists = $result | Where-Object { $_.name -eq $secret }
            
            if ($secretExists) {
                Write-ColorOutput "✅ $secret configured" "Success"
            } else {
                Write-ColorOutput "⚠️ $secret not configured (recommended)" "Warning"
            }
        } catch {
            Write-ColorOutput "⚠️ Failed to check secret $secret : $_" "Warning"
        }
    }
    
    return $secretsValid
}

function Test-WorkflowConfiguration {
    Write-ColorOutput "" "Info"
    Write-ColorOutput "⚙️ VALIDATING WORKFLOW CONFIGURATION" "Header"
    Write-ColorOutput "====================================" "Header"
    
    $workflowValid = $true
    $workflowPath = ".github/workflows/code-quality.yml"
    
    if (-not (Test-Path $workflowPath)) {
        Write-ColorOutput "❌ Code quality workflow not found" "Error"
        return $false
    }
    
    $workflowContent = Get-Content $workflowPath -Raw
    
    # Check for critical workflow components
    $requiredComponents = @(
        @{ Pattern = "coverage-analysis"; Description = "Coverage analysis job" },
        @{ Pattern = "sonarqube-analysis"; Description = "SonarQube analysis job" },
        @{ Pattern = "qlty-analysis"; Description = "Qlty analysis job" },
        @{ Pattern = "advanced-security-scan"; Description = "Security scanning job" },
        @{ Pattern = "quality-gate"; Description = "Quality gate job" },
        @{ Pattern = "SONAR_TOKEN"; Description = "SonarQube token usage" },
        @{ Pattern = "SEMGREP_APP_TOKEN"; Description = "Semgrep token usage" },
        @{ Pattern = "sonarqube-scanner-action"; Description = "SonarQube scanner action" },
        @{ Pattern = "qlty check"; Description = "Qlty check command" }
    )
    
    Write-ColorOutput "🔍 Checking workflow components..." "Info"
    foreach ($component in $requiredComponents) {
        if ($workflowContent -match $component.Pattern) {
            Write-ColorOutput "✅ $($component.Description) found" "Success"
        } else {
            Write-ColorOutput "❌ $($component.Description) missing" "Error"
            $workflowValid = $false
        }
    }
    
    # Check for proper step ordering
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🔍 Checking step ordering..." "Info"
    
    # Verify SonarQube scanner runs before quality gate
    $scannerPos = $workflowContent.IndexOf("sonarsource/sonarqube-scanner-action")
    $gatePos = $workflowContent.IndexOf("sonarqube-quality-gate-action")
    
    if ($scannerPos -gt 0 -and $gatePos -gt 0) {
        if ($scannerPos -lt $gatePos) {
            Write-ColorOutput "✅ SonarQube scanner runs before quality gate" "Success"
        } else {
            Write-ColorOutput "❌ SonarQube quality gate runs before scanner" "Error"
            $workflowValid = $false
        }
    }
    
    return $workflowValid
}

function Show-SetupInstructions {
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📋 SETUP COMPLETION INSTRUCTIONS" "Header"
    Write-ColorOutput "=================================" "Header"
    Write-ColorOutput "" "Info"
    
    Write-ColorOutput "🔧 To complete the setup:" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "1. Configure local environment:" "Info"
    Write-ColorOutput "   powershell ./scripts/setup-security-tokens.ps1 -Interactive" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "2. Add GitHub repository secrets:" "Info"
    Write-ColorOutput "   • Go to: Repository -> Settings -> Secrets and variables -> Actions" "Info"
    Write-ColorOutput "   • Add: SONAR_HOST_URL, SONAR_TOKEN, SEMGREP_APP_TOKEN" "Info"
    Write-ColorOutput "   • Optional: SONARQUBE_DB_PASSWORD" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "3. Test the setup:" "Info"
    Write-ColorOutput "   docker-compose -f docker-compose.sonarqube.yml up -d" "Info"
    Write-ColorOutput "   git add . ; git commit -m 'feat: complete quality infrastructure'" "Info"
    Write-ColorOutput "   git push origin main" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "4. Monitor the pipeline:" "Info"
    Write-ColorOutput "   • GitHub Actions: Repository -> Actions" "Info"
    Write-ColorOutput "   • SonarQube: http://localhost:9000" "Info"
    Write-ColorOutput "   • Security: Repository -> Security -> Code scanning alerts" "Info"
    Write-ColorOutput "" "Info"
}

# Main execution
try {
    Write-ColorOutput "🚀 TRAIDER V1 - Setup Validation" "Header"
    Write-ColorOutput "Institutional-Grade Code Quality and Security" "Header"
    Write-ColorOutput "=============================================" "Header"
    
    # Determine what to check
    if (-not $CheckLocal -and -not $CheckSecrets -and -not $CheckWorkflow -and -not $All) {
        $All = $true  # Default to checking everything
    }
    
    $allValid = $true
    
    # Check local configuration
    if ($CheckLocal -or $All) {
        $localValid = Test-LocalConfiguration
        $allValid = $allValid -and $localValid
    }
    
    # Check GitHub secrets
    if ($CheckSecrets -or $All) {
        $secretsValid = Test-GitHubSecrets
        $allValid = $allValid -and $secretsValid
    }
    
    # Check workflow configuration
    if ($CheckWorkflow -or $All) {
        $workflowValid = Test-WorkflowConfiguration
        $allValid = $allValid -and $workflowValid
    }
    
    # Final summary
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📊 VALIDATION SUMMARY" "Header"
    Write-ColorOutput "=====================" "Header"
    
    if ($allValid) {
        Write-ColorOutput "✅ All validations passed - setup is complete!" "Success"
        Write-ColorOutput "🚀 Ready for production deployment" "Success"
    } else {
        Write-ColorOutput "⚠️ Some validations failed - review issues above" "Warning"
        Show-SetupInstructions
        exit 1
    }
    
}
catch {
    Write-ColorOutput "❌ Validation failed: $_" "Error"
    Write-ColorOutput "Please check the error message and try again." "Error"
    exit 1
}