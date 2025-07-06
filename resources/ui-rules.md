# 📐 TRAIDER V1 - Core UI/UX Design Principles

This document outlines the fundamental design principles that guide the development of the TRAIDER dashboard and user interfaces. These rules ensure a consistent, reliable, and professional user experience, aligning with the project's core mission of building an institutional-grade trading platform.

---

## 1 · Core Philosophy: Risk-First Clarity

Our UI design philosophy is derived directly from the project's guiding principles: **"Risk Over Return"** and **"Observability Everywhere"**. The user interface must be, above all, a tool for clarity, risk management, and situational awareness. Every design decision should be weighed against its ability to provide clear, unambiguous information and prevent costly errors.

---

## 2 · Key Design Principles

### 2.1 · Data-Rich, Not Data-Overloaded

- **Principle**: Display dense, critical information without overwhelming the user. The goal is a high-performance cockpit, not a cluttered mess.
- **Implementation**:
  - Use a clear grid-based layout to organize information logically (e.g., P&L, NAV, Positions, Risk).
  - Group related metrics into cards or modules.
  - Employ progressive disclosure. Show high-level summaries by default and allow users to click for more detailed views (e.g., "View Model Details").

### 2.2 · Real-time Awareness is Paramount

- **Principle**: The user must always know the current state of the system at a glance.
- **Implementation**:
  - A persistent system status indicator (e.g., `🟢 TRADING`, `🔴 OFFLINE`) should be visible on all primary screens.
  - Key metrics like P&L, latency, and risk utilization should update in real-time.
  - Use visual cues (color, icons) to indicate the health of individual services and connections, as seen in the "System Health" screen.

### 2.3 · Safety & Confirmation for Critical Actions

- **Principle**: Prevent accidental, high-consequence actions. Users must be confident that they won't inadvertently trigger a major event.
- **Implementation**:
  - Actions that can lead to financial loss or system state changes (e.g., switching from Paper to Live mode, Emergency Stop) **must** require a confirmation step (e.g., a modal dialog with a secondary confirmation button).
  - Use distinct styling for destructive actions (e.g., red buttons).
  - Implement role-based access control (RBAC) to hide critical controls from unauthorized users (e.g., "Owner" vs. "Guest").

### 2.4 · Unambiguous Visual Hierarchy

- **Principle**: Guide the user's eye to the most important information first.
- **Implementation**:
  - Use font size, weight, and color to establish a clear hierarchy. Key performance indicators (KPIs) like Total NAV and Daily P&L should be the most prominent elements.
  - Negative space should be used strategically to separate and define sections of the UI.
  - Charts and visualizations are primary elements for conveying trends and should be given significant screen real estate.

### 2.5 · Consistency is Key

- **Principle**: A consistent design language reduces cognitive load and makes the interface more intuitive.
- **Implementation**:
  - Use the same component for the same purpose everywhere (e.g., all primary action buttons look the same).
  - Maintain consistent placement for core navigation and status elements.
  - Adhere strictly to the color palette and typography defined in `theme-rules.md`. Status colors (green for success, red for danger, yellow for warning) must be used consistently across all components.

### 2.6 · Performance is a Feature

- **Principle**: A slow, laggy interface undermines trust in a high-frequency trading system. The UI must be fast and responsive.
- **Implementation**:
  - Optimize data fetching and state management (as outlined in `tech-stack.md` with SWR and Zustand).
  - Use `next/dynamic` to lazy-load heavy components like charting libraries.
  - Throttle high-frequency data updates to the UI to prevent freezing, batching updates where possible.
  - Monitor bundle size and client-side performance with tools like Sentry.

### 2.7 · Responsive & Accessible Design

- **Principle**: The dashboard must be usable on various screen sizes, from a large monitor to a mobile device for on-the-go checks.
- **Implementation**:
  - Employ a mobile-first responsive design strategy.
  - Mobile views should prioritize the most critical information: status, P&L, and open positions, as shown in the `user-flow.md` mobile wireframe.
  - Ensure sufficient color contrast and use accessible ARIA attributes where appropriate.
