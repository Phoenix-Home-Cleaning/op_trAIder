#!/usr/bin/env pwsh

<#
.SYNOPSIS
    TRAIDER V1 - Qlty CLI Setup Script for Local Development

.DESCRIPTION
    Installs and configures Qlty CLI for local code quality analysis on Windows.
    Replaces CodeClimate with Qlty for institutional-grade quality analysis.

.PARAMETER Force
    Force reinstallation even if Qlty is already installed

.PARAMETER SkipConfig
    Skip configuration initialization

.EXAMPLE
    .\scripts\setup-qlty.ps1
    .\scripts\setup-qlty.ps1 -Force
    .\scripts\setup-qlty.ps1 -SkipConfig

.NOTES
    Author: TRAIDER Team
    Version: 1.0.0-alpha
    Requires: PowerShell 5.1+, Internet connection
#>

param(
    [switch]$Force,
    [switch]$SkipConfig
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

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
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

function Install-QltyCLI {
    Write-ColorOutput "🔧 Installing Qlty CLI..." "Info"
    
    # Create temp directory
    $tempDir = Join-Path $env:TEMP "qlty-install"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    try {
        # Download Qlty CLI for Windows
        $downloadUrl = "https://github.com/qltysh/qlty/releases/latest/download/qlty-windows-x86_64.zip"
        $zipPath = Join-Path $tempDir "qlty.zip"
        
        Write-ColorOutput "📥 Downloading Qlty CLI from GitHub..." "Info"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
        
        # Extract archive
        Write-ColorOutput "📦 Extracting Qlty CLI..." "Info"
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        
        # Find the executable
        $qltyExe = Get-ChildItem -Path $tempDir -Name "qlty.exe" -Recurse | Select-Object -First 1
        if (-not $qltyExe) {
            throw "Qlty executable not found in downloaded archive"
        }
        
        # Create installation directory
        $installDir = Join-Path $env:LOCALAPPDATA "qlty"
        if (-not (Test-Path $installDir)) {
            New-Item -ItemType Directory -Path $installDir | Out-Null
        }
        
        # Copy executable
        $qltyPath = Join-Path $installDir "qlty.exe"
        Copy-Item -Path (Join-Path $tempDir $qltyExe) -Destination $qltyPath -Force
        
        # Add to PATH if not already there
        $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($userPath -notlike "*$installDir*") {
            Write-ColorOutput "🔧 Adding Qlty to PATH..." "Info"
            $newPath = "$userPath;$installDir"
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            $env:PATH = "$env:PATH;$installDir"
        }
        
        # Verify installation
        & $qltyPath --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $version = & $qltyPath --version
            Write-ColorOutput "✅ Qlty CLI installed successfully: $version" "Success"
        } else {
            throw "Qlty installation verification failed"
        }
        
    }
    finally {
        # Cleanup
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Initialize-QltyConfig {
    Write-ColorOutput "🔧 Initializing Qlty configuration..." "Info"
    
    # Verify configuration file exists
    $configFile = ".qlty.toml"
    if (-not (Test-Path $configFile)) {
        Write-ColorOutput "❌ Qlty configuration file not found: $configFile" "Error"
        Write-ColorOutput "Please ensure .qlty.toml exists in the project root" "Warning"
        return $false
    }
    
    # Create output directory
    $outputDir = "quality-reports\qlty"
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
        Write-ColorOutput "📁 Created output directory: $outputDir" "Info"
    }
    
    # Initialize Qlty in the project
    try {
        Write-ColorOutput "🔧 Running Qlty initialization..." "Info"
        & qlty init --config $configFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Qlty configuration initialized successfully" "Success"
        } else {
            Write-ColorOutput "⚠️ Qlty initialization completed with warnings" "Warning"
        }
    }
    catch {
        Write-ColorOutput "❌ Failed to initialize Qlty configuration: $_" "Error"
        return $false
    }
    
    return $true
}

function Test-QltyInstallation {
    Write-ColorOutput "🧪 Testing Qlty installation..." "Info"
    
    try {
        # Test basic functionality
        $dryRunResult = & qlty check --dry-run 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Qlty dry-run test passed" "Success"
        } else {
            Write-ColorOutput "⚠️ Qlty dry-run test completed with warnings" "Warning"
            Write-ColorOutput "Output: $dryRunResult" "Warning"
        }
        
        # Test configuration
        if (Test-Path ".qlty.toml") {
            Write-ColorOutput "✅ Configuration file found" "Success"
        } else {
            Write-ColorOutput "❌ Configuration file missing" "Error"
            return $false
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "❌ Qlty installation test failed: $_" "Error"
        return $false
    }
}

function Show-UsageInstructions {
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🎯 QLTY CLI SETUP COMPLETE" "Header"
    Write-ColorOutput "========================================" "Header"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📋 Available Commands:" "Info"
    Write-ColorOutput "  npm run quality:qlty        - Run full quality analysis" "Info"
    Write-ColorOutput "  npm run quality:qlty:init   - Initialize Qlty configuration" "Info"
    Write-ColorOutput "  npm run quality:qlty:format - Auto-format code issues" "Info"
    Write-ColorOutput "  qlty check                   - Direct CLI usage" "Info"
    Write-ColorOutput "  qlty check --help            - Show all available options" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📊 Quality Standards:" "Info"
    Write-ColorOutput "  • Complexity Threshold: ≤12 (trading systems)" "Info"
    Write-ColorOutput "  • Duplication Limit: ≤3%" "Info"
    Write-ColorOutput "  • Maintainability: ≥80 score" "Info"
    Write-ColorOutput "  • Security: Integrated scanning" "Info"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📁 Output Location: quality-reports/qlty/" "Info"
    Write-ColorOutput "🔗 Documentation: docs/infrastructure/code-quality-pipeline.md" "Info"
    Write-ColorOutput "" "Info"
}

# Main execution
try {
    Write-ColorOutput "🚀 TRAIDER V1 - Qlty CLI Setup" "Header"
    Write-ColorOutput "Institutional-Grade Code Quality Analysis" "Header"
    Write-ColorOutput "========================================" "Header"
    
    # Verify prerequisites
    Write-ColorOutput "🔍 Checking prerequisites..." "Info"
    
    if (-not (Test-InternetConnection)) {
        Write-ColorOutput "❌ Internet connection required for installation" "Error"
        exit 1
    }
    
    # Check if Qlty is already installed
    $qltyInstalled = $false
    try {
        & qlty --version | Out-Null
        $qltyInstalled = ($LASTEXITCODE -eq 0)
    }
    catch {
        $qltyInstalled = $false
    }
    
    if ($qltyInstalled -and -not $Force) {
        $version = & qlty --version
        Write-ColorOutput "✅ Qlty CLI already installed: $version" "Success"
        Write-ColorOutput "Use -Force to reinstall" "Info"
    } else {
        Install-QltyCLI
    }
    
    # Initialize configuration
    if (-not $SkipConfig) {
        $configSuccess = Initialize-QltyConfig
        if (-not $configSuccess) {
            Write-ColorOutput "⚠️ Configuration initialization failed - continuing anyway" "Warning"
        }
    }
    
    # Test installation
    $testSuccess = Test-QltyInstallation
    if (-not $testSuccess) {
        Write-ColorOutput "❌ Installation test failed" "Error"
        exit 1
    }
    
    # Show usage instructions
    Show-UsageInstructions
    
    Write-ColorOutput "✅ Qlty CLI setup completed successfully!" "Success"
    Write-ColorOutput "You may need to restart your terminal for PATH changes to take effect." "Warning"
    
}
catch {
    Write-ColorOutput "❌ Setup failed: $_" "Error"
    Write-ColorOutput "Please check the error message and try again." "Error"
    exit 1
} 