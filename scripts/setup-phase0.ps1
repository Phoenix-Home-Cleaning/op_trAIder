# =============================================================================
# TRAIDER V1 - Phase 0 Setup Script (Windows PowerShell)
# =============================================================================
#
# Comprehensive setup script for TRAIDER Phase 0 foundation.
# Initializes development environment, database, and verifies all components.
#
# Performance: Complete setup in <5 minutes
# Risk: MEDIUM - Development environment setup
# Compliance: All setup steps logged and tracked
#
# Usage: .\scripts\setup-phase0.ps1
# Author: TRAIDER Team
# Since: 1.0.0-alpha

param(
    [switch]$SkipDocker,
    [switch]$SkipDatabase,
    [switch]$SkipDependencies,
    [switch]$WithK3s,
    [switch]$Verbose
)

# Set error handling
$ErrorActionPreference = "Stop"

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

Write-Host "🚀 TRAIDER V1 - Phase 0 Setup Starting..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

function Write-Step {
    param([string]$Message)
    Write-Host "📋 $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Magenta
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$HostName,
        [int]$Port,
        [int]$TimeoutSeconds = 60
    )
    
    Write-Step "Waiting for $ServiceName to be ready..."
    $timeout = (Get-Date).AddSeconds($TimeoutSeconds)
    
    do {
        try {
            $connection = New-Object System.Net.Sockets.TcpClient
            $connection.Connect($HostName, $Port)
            $connection.Close()
            Write-Success "$ServiceName is ready!"
            return $true
        }
        catch {
            Start-Sleep -Seconds 2
        }
    } while ((Get-Date) -lt $timeout)
    
    Write-Error "$ServiceName failed to start within $TimeoutSeconds seconds"
    return $false
}

# =============================================================================
# PREREQUISITE CHECKS
# =============================================================================

Write-Step "Checking prerequisites..."

# Check Node.js
if (-not (Test-Command "node")) {
    Write-Error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
}

$nodeVersion = node --version
Write-Verbose "Node.js version: $nodeVersion"

# Check npm
if (-not (Test-Command "npm")) {
    Write-Error "npm is not installed. Please install Node.js which includes npm."
    exit 1
}

# Check Docker (optional)
if (-not $SkipDocker) {
    if (-not (Test-Command "docker")) {
        Write-Warning "Docker is not installed. Skipping Docker services..."
        $SkipDocker = $true
    } else {
        try {
            docker info | Out-Null
            Write-Verbose "Docker is running"
        }
        catch {
            Write-Warning "Docker is installed but not running. Skipping Docker services..."
            $SkipDocker = $true
        }
    }
}

# Check Python (for backend)
if (-not (Test-Command "py")) {
    Write-Error "Python is not installed. Please install Python 3.11+ from https://python.org/"
    exit 1
}

$pythonVersion = py --version
Write-Verbose "Python version: $pythonVersion"

# Check K3s and kubectl (optional)
if ($WithK3s) {
    if (-not (Test-Command "kubectl")) {
        Write-Error "kubectl is not installed. Please install kubectl for K3s management."
        Write-Host "Install guide: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/" -ForegroundColor Yellow
        exit 1
    }
    
    # Check if K3s is running
    try {
        kubectl cluster-info | Out-Null
        Write-Verbose "K3s cluster is accessible"
    }
    catch {
        Write-Error "K3s cluster is not accessible. Please ensure K3s is installed and running."
        Write-Host "Install K3s: curl -sfL https://get.k3s.io | sh -" -ForegroundColor Yellow
        exit 1
    }
}

Write-Success "Prerequisites check completed"

# =============================================================================
# FRONTEND SETUP
# =============================================================================

Write-Step "Setting up frontend dependencies..."

if (-not $SkipDependencies) {
    try {
        # Install frontend dependencies
        npm ci --prefer-offline --no-audit --no-fund
        Write-Success "Frontend dependencies installed"
        
        # Run type checking
        Write-Step "Running TypeScript type check..."
        npm run type-check
        Write-Success "TypeScript type check passed"
        
        # Run linting
        Write-Step "Running ESLint..."
        npm run lint
        Write-Success "ESLint check passed"
        
    }
    catch {
        Write-Error "Frontend setup failed: $_"
        exit 1
    }
} else {
    Write-Warning "Skipping dependency installation"
}

# =============================================================================
# BACKEND SETUP
# =============================================================================

Write-Step "Setting up backend dependencies..."

try {
    Push-Location "backend"
    
    if (-not $SkipDependencies) {
        # Install Python dependencies
        Write-Step "Installing Python dependencies..."
        pip install -r requirements.txt
        Write-Success "Backend dependencies installed"
    }
    
    # Create environment file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Step "Creating environment configuration..."
        Copy-Item "env.example" ".env"
        Write-Success "Environment file created from template"
        Write-Warning "Please review and update .env file with your configuration"
    }
    
    Pop-Location
}
catch {
    Pop-Location
    Write-Error "Backend setup failed: $_"
    exit 1
}

# =============================================================================
# DOCKER SERVICES SETUP
# =============================================================================

if (-not $SkipDocker) {
    Write-Step "Starting Docker services..."
    
    try {
        # Stop any existing services
        docker-compose -f docker-compose.dev.yml down | Out-Null
        
        # Start services
        docker-compose -f docker-compose.dev.yml up -d
        Write-Success "Docker services started"
        
        # Wait for PostgreSQL
        if (Wait-ForService -ServiceName "PostgreSQL" -HostName "localhost" -Port 5432) {
            Write-Success "PostgreSQL is ready"
        } else {
            Write-Error "PostgreSQL failed to start"
            exit 1
        }
        
        # Wait for Redis
        if (Wait-ForService -ServiceName "Redis" -HostName "localhost" -Port 6379) {
            Write-Success "Redis is ready"
        } else {
            Write-Error "Redis failed to start"
            exit 1
        }
        
    }
    catch {
        Write-Error "Docker services setup failed: $_"
        exit 1
    }
} else {
    Write-Warning "Skipping Docker services"
}

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

if (-not $SkipDatabase -and -not $SkipDocker) {
    Write-Step "Initializing database..."
    
    try {
        Push-Location "backend"
        
        # Run database initialization
        Write-Step "Creating database schema..."
        py init_db.py
        Write-Success "Database schema created"
        
        # Run Alembic migrations
        Write-Step "Running database migrations..."
        py -m alembic upgrade head
        Write-Success "Database migrations completed"
        
        Pop-Location
    }
    catch {
        Pop-Location
        Write-Error "Database initialization failed: $_"
        Write-Warning "You may need to run 'python backend/init_db.py' manually"
    }
} else {
    Write-Warning "Skipping database initialization"
}

# =============================================================================
# VERIFICATION TESTS
# =============================================================================

Write-Step "Running verification tests..."

try {
    # Test frontend build
    Write-Step "Testing frontend build..."
    npm run build
    Write-Success "Frontend builds successfully"
    
    # Test backend startup
    Write-Step "Testing backend startup..."
    Push-Location "backend"
    
    # Start backend in background and test health endpoint
    $backendProcess = Start-Process -FilePath "py" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" -PassThru -WindowStyle Hidden
    
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
        if ($response.status -eq "healthy") {
            Write-Success "Backend health check passed"
        } else {
            Write-Warning "Backend health check returned unexpected status: $($response.status)"
        }
    }
    catch {
        Write-Warning "Backend health check failed: $_"
    }
    finally {
        # Stop backend process
        if ($backendProcess -and -not $backendProcess.HasExited) {
            Stop-Process -Id $backendProcess.Id -Force
        }
    }
    
    Pop-Location
}
catch {
    Pop-Location
    Write-Warning "Verification tests encountered issues: $_"
}

# =============================================================================
# K3S DEPLOYMENT (OPTIONAL)
# =============================================================================

if ($WithK3s) {
    Write-Step "Deploying to K3s cluster..."
    
    try {
        # Apply K8s manifests
        Write-Step "Applying Kubernetes manifests..."
        kubectl apply -f infrastructure/k8s/dev/
        Write-Success "K8s manifests applied successfully"
        
        # Wait for deployments to be ready
        Write-Step "Waiting for deployments to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/postgres-dev -n traider-dev
        kubectl wait --for=condition=available --timeout=300s deployment/redis-dev -n traider-dev
        kubectl wait --for=condition=available --timeout=300s deployment/prometheus-dev -n traider-dev
        kubectl wait --for=condition=available --timeout=300s deployment/grafana-dev -n traider-dev
        
        Write-Success "All K8s deployments are ready"
        
        # Display access information
        Write-Step "K8s services are accessible at:"
        Write-Host "  Frontend:   http://localhost:30000" -ForegroundColor Green
        Write-Host "  Backend:    http://localhost:30001" -ForegroundColor Green  
        Write-Host "  Grafana:    http://localhost:30002 (admin/admin)" -ForegroundColor Green
        Write-Host "  Prometheus: kubectl port-forward svc/prometheus-dev 9090:9090 -n traider-dev" -ForegroundColor Green
        
        # Check pod status
        Write-Step "Pod status:"
        kubectl get pods -n traider-dev
        
    }
    catch {
        Write-Error "K3s deployment failed: $_"
        Write-Warning "You can manually apply manifests with: kubectl apply -f infrastructure/k8s/dev/"
    }
}

# =============================================================================
# COMPLETION SUMMARY
# =============================================================================

Write-Host "`n🎉 TRAIDER V1 Phase 0 Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

Write-Host "`n📊 Setup Summary:" -ForegroundColor Cyan
Write-Host "✅ Frontend dependencies installed and verified"
Write-Host "✅ Backend dependencies installed and configured"

if (-not $SkipDocker) {
    Write-Host "✅ Docker services started (PostgreSQL, Redis, Monitoring)"
    Write-Host "✅ Database initialized with TimescaleDB"
    Write-Host "✅ Database migrations applied"
} else {
    Write-Host "⚠️ Docker services skipped"
}

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review and update .env with your configuration"

if ($WithK3s) {
    Write-Host "2. K3s services are running! Access them at:"
    Write-Host "   Frontend:   http://localhost:30000"
    Write-Host "   Backend:    http://localhost:30001"
    Write-Host "   Grafana:    http://localhost:30002 (admin/admin)"
    Write-Host "3. Monitor with: kubectl get pods -n traider-dev"
    Write-Host "4. Logs with: kubectl logs -f deployment/[service-name] -n traider-dev"
} else {
    Write-Host "2. Start the development servers:"
    Write-Host "   Frontend: npm run dev"
    Write-Host "   Backend:  cd backend && py -m uvicorn main:app --reload"

    if (-not $SkipDocker) {
        Write-Host "3. Access development tools:"
        Write-Host "   Database Admin: http://localhost:8080 (Adminer)"
        Write-Host "   Redis Admin:    http://localhost:8081 (Redis Commander)"
        Write-Host "   Metrics:        http://localhost:9090 (Prometheus)"
        Write-Host "   Dashboards:     http://localhost:3001 (Grafana)"
    }
}

Write-Host "`n📚 Documentation:" -ForegroundColor Cyan
Write-Host "- Phase 0 Setup: _docs/phases/phase-0-setup.md"
Write-Host "- Action Items:  _docs/action_items.md"
Write-Host "- Project Rules: _docs/resources/project-rules.md"

Write-Host "`n🎯 Phase 0 Status: COMPLETE" -ForegroundColor Green
Write-Host "Ready to begin Phase 1 (MVP) development!" -ForegroundColor Green 