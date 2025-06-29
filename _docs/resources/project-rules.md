# 🏗️ TRAIDER V1 — Project Rules & Development Standards

### AI-First Codebase Guidelines for Institutional-Grade Trading Platform *(June 28 2025)*

---

## 1 · 🎯 Core Philosophy: AI-First Development

TRAIDER is designed as an **AI-first codebase**, meaning every architectural decision prioritizes:

- **Modularity**: Each component can be understood and modified independently
- **Scalability**: Code structure supports rapid feature addition and system growth
- **Readability**: AI tools and human developers can quickly understand purpose and context
- **Maintainability**: Clear separation of concerns and consistent patterns throughout

---

## 2 · 📁 Directory Structure & Organization

### 2.1 · Root Directory Structure
```
traider/
├── app/                    # Next.js App Router (frontend)
├── backend/               # Python trading system
├── docs/                  # Project documentation
├── infrastructure/        # Terraform, Docker, deployment configs
├── tests/                 # Cross-system integration tests
├── scripts/              # Utility scripts and tools
├── .github/              # CI/CD workflows
└── shared/               # Shared types and utilities
```

### 2.2 · Frontend Structure (`app/`)
```
app/
├── (auth)/               # Auth route group
│   ├── login/
│   │   └── page.tsx
│   └── layout.tsx
├── dashboard/            # Main trading dashboard
│   ├── page.tsx
│   ├── layout.tsx
│   └── components/       # Dashboard-specific components
├── performance/          # Performance analytics
│   ├── page.tsx
│   └── components/
├── risk/                 # Risk management
│   ├── page.tsx
│   └── components/
├── signals/              # Signal generation & ML models
│   ├── page.tsx
│   └── components/
├── system/               # System health monitoring
│   ├── page.tsx
│   └── components/
├── settings/             # Configuration (owner only)
│   ├── trading/
│   ├── notifications/
│   └── layout.tsx
├── api/                  # API routes
│   ├── auth/
│   ├── positions/
│   ├── pnl/
│   └── health/
├── components/           # Shared UI components
│   ├── ui/              # Base UI components (buttons, cards, etc.)
│   ├── charts/          # Chart components
│   ├── trading/         # Trading-specific components
│   └── layout/          # Layout components
├── hooks/               # Custom React hooks
├── lib/                 # Utilities and configurations
├── types/               # TypeScript type definitions
└── globals.css          # Global styles
```

### 2.3 · Backend Structure (`backend/`)
```
backend/
├── services/            # Microservices
│   ├── market_data/     # Market data ingestion
│   ├── signal_gen/      # Signal generation
│   ├── risk_engine/     # Risk management
│   ├── executor/        # Order execution
│   └── portfolio/       # Portfolio management
├── shared/              # Shared Python modules
│   ├── models/          # Data models and schemas
│   ├── utils/           # Utility functions
│   ├── config/          # Configuration management
│   └── types/           # Type definitions
├── ml/                  # Machine learning components
│   ├── features/        # Feature engineering
│   ├── models/          # ML model definitions
│   ├── training/        # Training pipelines
│   └── inference/       # Inference services
├── data/                # Data management
│   ├── ingestion/       # Data ingestion pipelines
│   ├── storage/         # Database schemas and migrations
│   └── validation/      # Data validation rules
└── tests/               # Backend-specific tests
```

---

## 3 · 📝 File Naming Conventions

### 3.1 · General Rules
- **Use kebab-case** for directories: `market-data/`, `signal-generation/`
- **Use PascalCase** for React components: `PnLChart.tsx`, `RiskDashboard.tsx`
- **Use camelCase** for utility files: `tradingUtils.ts`, `chartHelpers.ts`
- **Use snake_case** for Python files: `market_data.py`, `risk_engine.py`
- **Be descriptive**: File names should clearly indicate their purpose

### 3.2 · Frontend Naming Patterns
```
components/
├── ui/
│   ├── Button.tsx           # Base UI components (PascalCase)
│   ├── Card.tsx
│   └── Modal.tsx
├── trading/
│   ├── PositionCard.tsx     # Domain-specific components
│   ├── PnLChart.tsx
│   └── RiskMeter.tsx
└── charts/
    ├── LineChart.tsx        # Chart components
    └── CandlestickChart.tsx

hooks/
├── usePositions.ts          # Data fetching hooks
├── usePnL.ts
└── useTradingStore.ts       # Store hooks

lib/
├── auth.ts                  # Authentication utilities
├── trading.ts               # Trading calculations
└── chartConfig.ts           # Chart configurations

types/
├── trading.ts               # Trading-related types
├── api.ts                   # API response types
└── ui.ts                    # UI component types
```

### 3.3 · Backend Naming Patterns
```
services/
├── market_data/
│   ├── __init__.py
│   ├── websocket_client.py  # Specific functionality
│   ├── data_processor.py
│   └── storage_handler.py
└── risk_engine/
    ├── __init__.py
    ├── var_calculator.py
    ├── position_sizer.py
    └── circuit_breaker.py

shared/
├── models/
│   ├── position.py          # Data models
│   ├── trade.py
│   └── signal.py
└── utils/
    ├── logging.py           # Utility functions
    ├── metrics.py
    └── validation.py
```

---

## 4 · 📄 File Structure & Documentation Standards

### 4.1 · File Header Requirements
Every file must begin with a clear header explaining its purpose:

```typescript
/**
 * @fileoverview Real-time P&L chart component for trading dashboard
 * 
 * This component displays live profit/loss data using Chart.js with
 * real-time updates via Socket.IO. Handles both daily and historical
 * P&L visualization with proper error boundaries.
 * 
 * @author TRAIDER Team
 * @since 2025-06-28
 */
```

```python
"""
Market Data WebSocket Client

Manages real-time connection to Coinbase Advanced Trade API for Level-2
order book data and trade feeds. Implements automatic reconnection with
exponential backoff and data validation.

Author: TRAIDER Team
Since: 2025-06-28
"""
```

### 4.2 · Function Documentation Standards
All functions must have comprehensive documentation:

```typescript
/**
 * Calculates position size based on volatility targeting
 * 
 * @param signal - Trading signal strength (-1 to 1)
 * @param volatility - Historical volatility (annualized)
 * @param riskBudget - Available risk budget in USD
 * @param maxPosition - Maximum position size limit
 * @returns Position size in USD, clamped to risk limits
 * 
 * @example
 * const size = calculatePositionSize(0.5, 0.25, 1000, 2000);
 * // Returns: 800 (for 0.5 signal strength)
 */
function calculatePositionSize(
  signal: number,
  volatility: number,
  riskBudget: number,
  maxPosition: number
): number {
  // Implementation...
}
```

```python
def calculate_var(
    positions: List[Position],
    confidence_level: float = 0.95,
    time_horizon: int = 1
) -> float:
    """
    Calculate Value at Risk for current portfolio positions.
    
    Uses historical simulation method with 252-day lookback period.
    Incorporates correlation matrix for multi-asset portfolios.
    
    Args:
        positions: List of current trading positions
        confidence_level: VaR confidence level (default: 0.95)
        time_horizon: Time horizon in days (default: 1)
        
    Returns:
        VaR estimate in USD (positive value represents potential loss)
        
    Raises:
        ValueError: If positions list is empty or confidence_level invalid
        
    Example:
        >>> positions = [Position("BTC", 1000), Position("ETH", 500)]
        >>> var = calculate_var(positions, 0.99, 1)
        >>> print(f"1-day VaR (99%): ${var:.2f}")
    """
```

### 4.3 · File Size Limits
- **Maximum 500 lines per file** to ensure AI tool compatibility
- **Break large files into logical modules** when approaching limit
- **Use barrel exports** (`index.ts`) to maintain clean import paths

---

## 5 · 🏗️ Code Organization Principles

### 5.1 · Separation of Concerns
```typescript
// ❌ Bad: Mixed concerns in single file
export function TradingDashboard() {
  // API calls, state management, UI rendering all mixed together
}

// ✅ Good: Separated concerns
export function TradingDashboard() {
  const { positions, isLoading } = usePositions();  // Data layer
  const { pnl } = usePnL();                         // Data layer
  
  return (
    <DashboardLayout>                               {/* Layout layer */}
      <PositionCards positions={positions} />       {/* UI layer */}
      <PnLChart data={pnl} />                      {/* UI layer */}
    </DashboardLayout>
  );
}
```

### 5.2 · Single Responsibility Principle
Each file/function should have one clear purpose:

```typescript
// ❌ Bad: Multiple responsibilities
function processTradeData(data: any) {
  // Validates data
  // Calculates P&L
  // Updates database
  // Sends notifications
}

// ✅ Good: Single responsibility
function validateTradeData(data: TradeData): ValidationResult { }
function calculatePnL(trade: Trade): number { }
function updateTradeDatabase(trade: Trade): Promise<void> { }
function sendTradeNotification(trade: Trade): void { }
```

### 5.3 · Dependency Direction
- **UI components depend on hooks**
- **Hooks depend on services**
- **Services depend on utilities**
- **Utilities have no dependencies**

```typescript
// Dependency flow: Component → Hook → Service → Utility
Component (PositionCard) 
  → Hook (usePositions) 
    → Service (tradingApi) 
      → Utility (httpClient)
```

---

## 6 · 🎨 UI/UX Implementation Rules

### 6.1 · Component Architecture
```typescript
// Component structure template
interface ComponentProps {
  // Props interface with clear documentation
}

/**
 * Component description
 */
export function ComponentName({ prop1, prop2 }: ComponentProps) {
  // 1. Hooks and state
  // 2. Event handlers
  // 3. Effects
  // 4. Render logic
  
  return (
    // JSX with proper semantic structure
  );
}
```

### 6.2 · Styling Conventions
- **Use Tailwind CSS classes** following the design system
- **Create reusable component variants** for consistent styling
- **Follow the color palette** defined in `theme-rules.md`
- **Implement responsive design** with mobile-first approach

```typescript
// ✅ Good: Consistent styling with variants
const cardVariants = {
  default: 'bg-secondary border-border',
  success: 'bg-green-50 border-green-200',
  danger: 'bg-red-50 border-red-200',
};

export function TradingCard({ variant = 'default', children }: Props) {
  return (
    <div className={`rounded-lg border p-4 shadow-sm ${cardVariants[variant]}`}>
      {children}
    </div>
  );
}
```

---

## 7 · 🔒 Security & Safety Rules

### 7.1 · Sensitive Data Handling
- **Never log sensitive data** (API keys, trading positions, P&L)
- **Use environment variables** for all configuration
- **Implement proper input validation** on all API endpoints
- **Sanitize all user inputs** to prevent XSS attacks

### 7.2 · Trading Safety
- **Implement confirmation dialogs** for critical actions
- **Use role-based access control** (Owner vs Guest)
- **Log all trading decisions** with full audit trail
- **Include emergency stop mechanisms** in all trading components

---

## 8 · 🧪 Testing Standards

### 8.1 · Test File Organization
```
__tests__/
├── components/           # Component tests
│   ├── PnLChart.test.tsx
│   └── PositionCard.test.tsx
├── hooks/               # Hook tests
│   ├── usePositions.test.ts
│   └── usePnL.test.ts
├── utils/               # Utility tests
│   ├── trading.test.ts
│   └── validation.test.ts
└── integration/         # Integration tests
    └── trading-flow.test.ts
```

### 8.2 · Test Requirements
- **Unit tests** for all utilities and business logic
- **Component tests** for UI components with user interactions
- **Integration tests** for critical trading flows
- **E2E tests** for complete user journeys
- **Minimum 90% code coverage** for critical paths

---

## 9 · 📊 Performance & Monitoring Rules

### 9.1 · Performance Standards
- **Bundle size monitoring** with `@next/bundle-analyzer`
- **Lazy loading** for heavy components (charts, complex UI)
- **Optimized data fetching** with SWR caching strategies
- **Real-time update throttling** to prevent UI freezing

### 9.2 · Monitoring Implementation
- **Instrument all critical functions** with OpenTelemetry traces
- **Add performance metrics** for trading operations
- **Implement error boundaries** for graceful failure handling
- **Use Sentry for error tracking** with proper error categorization

---

## 10 · 🔄 Development Workflow

### 10.1 · Git Workflow
- **Feature branches** for all development work
- **Descriptive commit messages** following conventional commits
- **Pull request reviews** required for all changes
- **Automated testing** in CI/CD pipeline

### 10.2 · Code Quality Gates
- **TypeScript strict mode** with zero errors
- **ESLint and Prettier** for consistent formatting
- **Unit test coverage** above 90% for critical paths
- **Security scanning** with automated tools

---

## 11 · 📚 Documentation Requirements

### 11.1 · Code Documentation
- **File headers** explaining purpose and context
- **Function documentation** with parameters and examples
- **Type definitions** with clear descriptions
- **README files** for each major module

### 11.2 · Architecture Documentation
- **Decision records** for major architectural choices
- **API documentation** with OpenAPI specifications
- **Deployment guides** with step-by-step instructions
- **Troubleshooting guides** for common issues

---

> **Remember**: These rules exist to support our core mission of building a reliable, institutional-grade trading platform. Every decision should prioritize **clarity, safety, and maintainability** over clever code or premature optimization. When in doubt, choose the approach that makes the code easier for both AI tools and human developers to understand and modify. 