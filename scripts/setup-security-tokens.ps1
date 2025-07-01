#!/usr/bin/env powershell

<#
.SYNOPSIS
    TRAIDER V1 - Security Tokens Setup Script

.DESCRIPTION
    Configures and validates security tokens for institutional-grade code quality analysis.
    Sets up SONAR_TOKEN, SEMGREP_APP_TOKEN, and SONARQUBE_DB_PASSWORD with proper security practices.

.PARAMETER Interactive
    Run in interactive mode to prompt for token values

.PARAMETER ValidateOnly
    Only validate existing tokens without prompting for new ones

.PARAMETER GeneratePasswords
    Generate secure passwords for database components

.EXAMPLE
    .\scripts\setup-security-tokens.ps1 -Interactive
    .\scripts\setup-security-tokens.ps1 -ValidateOnly
    .\scripts\setup-security-tokens.ps1 -GeneratePasswords

.NOTES
    Author: TRAIDER Team
    Version: 1.0.0-alpha
    Requires: PowerShell 5.1+, Internet connection for validation
    Security: All tokens are handled securely and never logged
#>

param(
    [switch]$Interactive,
    [switch]$ValidateOnly,
    [switch]$GeneratePasswords
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
    Secure  = "DarkGreen"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-InternetConnection {
    try {
        $response = Invoke-WebRequest -Uri "https://github.com" -Method Head -TimeoutSec 10 -UseBasicParsing
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function New-SecurePassword {
    param(
        [int]$Length = 32
    )
    
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    $password = ""
    
    for ($i = 0; $i -lt $Length; $i++) {
        $password += $chars[(Get-Random -Minimum 0 -Maximum $chars.Length)]
    }
    
    return $password
}

function Test-SonarQubeToken {
    param(
        [string]$Token,
        [string]$HostUrl
    )
    
    if ([string]::IsNullOrEmpty($Token) -or [string]::IsNullOrEmpty($HostUrl)) {
        return @{ Valid = $false; Message = "Token or Host URL is empty" }
    }
    
    try {
        $headers = @{
            "Authorization" = "Bearer $Token"
        }
        
        $response = Invoke-WebRequest -Uri "$HostUrl/api/authentication/validate" -Headers $headers -Method Get -TimeoutSec 10 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            return @{ Valid = $true; Message = "Token is valid" }
        } else {
            return @{ Valid = $false; Message = "Invalid response: $($response.StatusCode)" }
        }
    }
    catch {
        return @{ Valid = $false; Message = "Connection failed: $($_.Exception.Message)" }
    }
}

function Test-SemgrepToken {
    param(
        [string]$Token
    )
    
    if ([string]::IsNullOrEmpty($Token)) {
        return @{ Valid = $false; Message = "Token is empty" }
    }
    
    # Basic format validation for Semgrep tokens
    if ($Token -match "^[a-f0-9]{40,}$") {
        return @{ Valid = $true; Message = "Token format is valid (full validation requires Semgrep CLI)" }
    } else {
        return @{ Valid = $false; Message = "Token format appears invalid" }
    }
}

function Get-EnvironmentValue {
    param(
        [string]$VariableName
    )
    
    # Check current environment
    $value = [Environment]::GetEnvironmentVariable($VariableName)
    if (-not [string]::IsNullOrEmpty($value)) {
        return $value
    }
    
    # Check .env file
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        foreach ($line in $envContent) {
            if ($line -match "^$VariableName=(.+)$") {
                return $matches[1]
            }
        }
    }
    
    return $null
}

function Set-EnvironmentValue {
    param(
        [string]$VariableName,
        [string]$Value,
        [switch]$Secure
    )
    
    # Update .env file
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        $updated = $false
        
        for ($i = 0; $i -lt $envContent.Count; $i++) {
            if ($envContent[$i] -match "^$VariableName=") {
                $envContent[$i] = "$VariableName=$Value"
                $updated = $true
                break
            }
        }
        
        if (-not $updated) {
            $envContent += "$VariableName=$Value"
        }
        
        $envContent | Set-Content ".env"
    } else {
        "$VariableName=$Value" | Set-Content ".env"
    }
    
    # Set in current session
    [Environment]::SetEnvironmentVariable($VariableName, $Value, "Process")
    
    if ($Secure) {
        Write-ColorOutput "✅ $VariableName configured securely" "Secure"
    } else {
        Write-ColorOutput "✅ $VariableName set to: $Value" "Success"
    }
}

function Show-TokenSetupInstructions {
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🔐 SECURITY TOKENS SETUP INSTRUCTIONS" "Header"
    Write-ColorOutput "======================================" "Header"
    Write-ColorOutput "" "Info"
    
    Write-ColorOutput "📋 Required Tokens:" "Info"
    Write-ColorOutput "" "Info"
    
    Write-ColorOutput "1. SONAR_TOKEN (SonarQube Authentication)" "Info"
    Write-ColorOutput "   • Login to SonarQube: http://localhost:9000" "Info"
    Write-ColorOutput "   • Go to: My Account → Security → Generate Tokens" "Info"
    Write-ColorOutput "   • Name: 'TRAIDER-CI-Token'" "Info"
    Write-ColorOutput "   • Type: 'User Token'" "Info"
    Write-ColorOutput "   • Copy the generated token" "Info"
    Write-ColorOutput "" "Info"
    
    Write-ColorOutput "2. SEMGREP_APP_TOKEN (Semgrep Cloud Integration)" "Info"
    Write-ColorOutput "   • Sign up at: https://semgrep.dev/" "Info"
    Write-ColorOutput "   • Go to: Settings → Tokens" "Info"
    Write-ColorOutput "   • Create new token with 'CI' scope" "Info"
    Write-ColorOutput "   • Copy the generated token" "Info"
    Write-ColorOutput "" "Info"
    
    Write-ColorOutput "3. SONARQUBE_DB_PASSWORD (Database Security)" "Info"
    Write-ColorOutput "   • Use a strong password (32+ characters)" "Info"
    Write-ColorOutput "   • Include uppercase, lowercase, numbers, symbols" "Info"
    Write-ColorOutput "   • Never reuse passwords from other systems" "Info"
    Write-ColorOutput "" "Info"
    
    Write-ColorOutput "🏛️ GitHub Repository Secrets:" "Info"
    Write-ColorOutput "   • Go to: Repository -> Settings -> Secrets and variables -> Actions" "Info"
    Write-ColorOutput "   • Add the following secrets:" "Info"
    Write-ColorOutput "     - SONAR_HOST_URL (e.g., http://localhost:9000)" "Info"
    Write-ColorOutput "     - SONAR_TOKEN" "Info"
    Write-ColorOutput "     - SEMGREP_APP_TOKEN" "Info"
    Write-ColorOutput "" "Info"
}

function Invoke-TokenValidation {
    Write-ColorOutput "🔍 Validating Security Tokens..." "Info"
    Write-ColorOutput "================================" "Info"
    
    $allValid = $true
    
    # Validate SONAR_TOKEN
    $sonarToken = Get-EnvironmentValue "SONAR_TOKEN"
    $sonarHost = Get-EnvironmentValue "SONAR_HOST_URL"
    
    if ($sonarToken -and $sonarHost) {
        Write-ColorOutput "🔍 Validating SonarQube token..." "Info"
        $sonarResult = Test-SonarQubeToken -Token $sonarToken -HostUrl $sonarHost
        
        if ($sonarResult.Valid) {
            Write-ColorOutput "✅ SONAR_TOKEN: $($sonarResult.Message)" "Success"
        } else {
            Write-ColorOutput "❌ SONAR_TOKEN: $($sonarResult.Message)" "Error"
            $allValid = $false
        }
    } else {
        Write-ColorOutput "⚠️ SONAR_TOKEN or SONAR_HOST_URL not configured" "Warning"
        $allValid = $false
    }
    
    # Validate SEMGREP_APP_TOKEN
    $semgrepToken = Get-EnvironmentValue "SEMGREP_APP_TOKEN"
    
    if ($semgrepToken) {
        Write-ColorOutput "🔍 Validating Semgrep token..." "Info"
        $semgrepResult = Test-SemgrepToken -Token $semgrepToken
        
        if ($semgrepResult.Valid) {
            Write-ColorOutput "✅ SEMGREP_APP_TOKEN: $($semgrepResult.Message)" "Success"
        } else {
            Write-ColorOutput "❌ SEMGREP_APP_TOKEN: $($semgrepResult.Message)" "Error"
            $allValid = $false
        }
    } else {
        Write-ColorOutput "⚠️ SEMGREP_APP_TOKEN not configured" "Warning"
    }
    
    # Check SONARQUBE_DB_PASSWORD
    $dbPassword = Get-EnvironmentValue "SONARQUBE_DB_PASSWORD"
    
    if ($dbPassword) {
        if ($dbPassword.Length -ge 16) {
            Write-ColorOutput "✅ SONARQUBE_DB_PASSWORD: Configured with adequate length" "Success"
        } else {
            Write-ColorOutput "⚠️ SONARQUBE_DB_PASSWORD: Password is too short (minimum 16 characters)" "Warning"
        }
    } else {
        Write-ColorOutput "⚠️ SONARQUBE_DB_PASSWORD not configured" "Warning"
        $allValid = $false
    }
    
    return $allValid
}

function Invoke-InteractiveSetup {
    Write-ColorOutput "🔧 Interactive Security Tokens Setup" "Header"
    Write-ColorOutput "====================================" "Header"
    
    # SONAR_HOST_URL
    $currentSonarHost = Get-EnvironmentValue "SONAR_HOST_URL"
    if ($currentSonarHost) {
        Write-ColorOutput "Current SONAR_HOST_URL: $currentSonarHost" "Info"
        $newSonarHost = Read-Host "Enter new SONAR_HOST_URL (or press Enter to keep current)"
        if ([string]::IsNullOrEmpty($newSonarHost)) {
            $newSonarHost = $currentSonarHost
        }
    } else {
        $newSonarHost = Read-Host "Enter SONAR_HOST_URL (e.g., http://localhost:9000)"
    }
    
    if (-not [string]::IsNullOrEmpty($newSonarHost)) {
        Set-EnvironmentValue -VariableName "SONAR_HOST_URL" -Value $newSonarHost
    }
    
    # SONAR_TOKEN
    Write-ColorOutput "Enter SONAR_TOKEN (input will be hidden):" "Info"
    $sonarToken = Read-Host -AsSecureString
    $sonarTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sonarToken))
    
    if (-not [string]::IsNullOrEmpty($sonarTokenPlain)) {
        Set-EnvironmentValue -VariableName "SONAR_TOKEN" -Value $sonarTokenPlain -Secure
    }
    
    # SEMGREP_APP_TOKEN
    Write-ColorOutput "Enter SEMGREP_APP_TOKEN (input will be hidden):" "Info"
    $semgrepToken = Read-Host -AsSecureString
    $semgrepTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($semgrepToken))
    
    if (-not [string]::IsNullOrEmpty($semgrepTokenPlain)) {
        Set-EnvironmentValue -VariableName "SEMGREP_APP_TOKEN" -Value $semgrepTokenPlain -Secure
    }
    
    # SONARQUBE_DB_PASSWORD
    $currentDbPassword = Get-EnvironmentValue "SONARQUBE_DB_PASSWORD"
    if ($currentDbPassword) {
        Write-ColorOutput "SONARQUBE_DB_PASSWORD is already configured" "Info"
        $generateNew = Read-Host "Generate new secure password? (y/N)"
        if ($generateNew -eq "y" -or $generateNew -eq "Y") {
            $newDbPassword = New-SecurePassword -Length 32
            Set-EnvironmentValue -VariableName "SONARQUBE_DB_PASSWORD" -Value $newDbPassword -Secure
        }
    } else {
        $newDbPassword = New-SecurePassword -Length 32
        Set-EnvironmentValue -VariableName "SONARQUBE_DB_PASSWORD" -Value $newDbPassword -Secure
    }
}

function Show-CompletionInstructions {
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🎯 SETUP COMPLETE" "Header"
    Write-ColorOutput "=================" "Header"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📋 Next Steps:" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "1. 🔐 Add secrets to GitHub repository:" "Info"
    Write-ColorOutput "   • Go to: Repository -> Settings -> Secrets and variables -> Actions" "Info"
    Write-ColorOutput "   • Add these secrets:" "Info"
    Write-ColorOutput "     - SONAR_HOST_URL" "Info"
    Write-ColorOutput "     - SONAR_TOKEN" "Info"
    Write-ColorOutput "     - SEMGREP_APP_TOKEN" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "2. 🐳 Start SonarQube with new password:" "Info"
    Write-ColorOutput "   docker-compose -f docker-compose.sonarqube.yml up -d" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "3. 🧪 Test the pipeline:" "Info"
    Write-ColorOutput "   git push origin main" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "4. 📊 Monitor quality analysis:" "Info"
    Write-ColorOutput "   • GitHub Actions: Repository -> Actions" "Info"
    Write-ColorOutput "   • SonarQube: $((Get-EnvironmentValue 'SONAR_HOST_URL'))" "Info"
    Write-ColorOutput "   • Security: Repository -> Security -> Code scanning alerts" "Info"
    Write-ColorOutput "" "Info"
}

# Main execution
try {
    Write-ColorOutput "🚀 TRAIDER V1 - Security Tokens Setup" "Header"
    Write-ColorOutput "Institutional-Grade Code Quality and Security" "Header"
    Write-ColorOutput "===========================================" "Header"
    
    # Check prerequisites
    if (-not (Test-Path ".env.example")) {
        Write-ColorOutput "❌ env.example not found - please run from project root" "Error"
        exit 1
    }
    
    # Show instructions if no parameters
    if (-not $Interactive -and -not $ValidateOnly -and -not $GeneratePasswords) {
        Show-TokenSetupInstructions
        Write-ColorOutput "Run with -Interactive to configure tokens" "Info"
        exit 0
    }
    
    # Generate passwords mode
    if ($GeneratePasswords) {
        Write-ColorOutput "🔐 Generating secure passwords..." "Info"
        $dbPassword = New-SecurePassword -Length 32
        Set-EnvironmentValue -VariableName "SONARQUBE_DB_PASSWORD" -Value $dbPassword -Secure
        Write-ColorOutput "✅ SONARQUBE_DB_PASSWORD generated and configured" "Success"
        exit 0
    }
    
    # Interactive setup mode
    if ($Interactive) {
        Invoke-InteractiveSetup
    }
    
    # Validation
    Write-ColorOutput "" "Info"
    $allValid = Invoke-TokenValidation
    
    if ($allValid) {
        Write-ColorOutput "✅ All security tokens validated successfully!" "Success"
        Show-CompletionInstructions
    } else {
        Write-ColorOutput "⚠️ Some tokens need attention - see validation results above" "Warning"
        if (-not $ValidateOnly) {
            Write-ColorOutput "Run with -Interactive to configure missing tokens" "Info"
        }
        exit 1
    }
    
}
catch {
    Write-ColorOutput "❌ Setup failed: $_" "Error"
    Write-ColorOutput "Please check the error message and try again." "Error"
    exit 1
} 