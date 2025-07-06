# 🎨 TRAIDER V1 - Professional Dark Theme

This document defines the official color palette, typography, and styling conventions for the TRAIDER dashboard. Adhering to these rules ensures a consistent, professional, and visually clear dark-themed interface.

---

## 1 · Color Palette

The theme is designed for clarity and reduced eye strain during long periods of monitoring. It uses a base of dark slate/gray, with a professional blue as the primary accent and vibrant colors for status indicators.

### 1.1 · Base & Grays

| Name             | Hex       | Usage                                  |
| ---------------- | --------- | -------------------------------------- |
| `bg-primary`     | `#111827` | Main background color.                 |
| `bg-secondary`   | `#1F2937` | Card backgrounds, modal headers.       |
| `border`         | `#374151` | Borders, dividers, outlines.           |
| `text-primary`   | `#F9FAFB` | Main text, headers, important data.    |
| `text-secondary` | `#9CA3AF` | Secondary text, labels, muted info.    |
| `text-tertiary`  | `#6B7280` | Placeholder text, disabled state text. |

### 1.2 · Accent Colors

| Name            | Hex       | Usage                                              |
| --------------- | --------- | -------------------------------------------------- |
| `primary`       | `#3B82F6` | Primary buttons, links, active state, focus rings. |
| `primary-hover` | `#2563EB` | Hover state for primary elements.                  |

### 1.3 · Status & Semantic Colors

These colors are critical for conveying system state and financial outcomes at a glance.

| Name      | Hex       | Usage                                                           |
| --------- | --------- | --------------------------------------------------------------- |
| `success` | `#22C55E` | Profits, positive changes, success states, online status.       |
| `danger`  | `#EF4444` | Losses, negative changes, error states, alerts, offline status. |
| `warning` | `#F59E0B` | Warnings, degraded performance, neutral-to-negative states.     |

---

## 2 · Typography

### 2.1 · Fonts

- **UI Font**: `Inter` (or system-ui as a fallback). Chosen for its clarity and readability on screens.
- **Data/Mono Font**: `JetBrains Mono`. Used exclusively for numerical data, financial figures, and code snippets to ensure alignment and clarity.

### 2.2 · Type Scale

| Element        | Font Size         | Font Weight       | Font Family        | Usage                                  |
| -------------- | ----------------- | ----------------- | ------------------ | -------------------------------------- |
| Heading 1 (H1) | `2.25rem` (36px)  | `700` (Bold)      | UI Font            | Main page titles.                      |
| Heading 2 (H2) | `1.5rem` (24px)   | `600` (Semi-Bold) | UI Font            | Section titles, large KPI values.      |
| Heading 3 (H3) | `1.25rem` (20px)  | `600` (Semi-Bold) | UI Font            | Card titles, sub-sections.             |
| Body           | `1rem` (16px)     | `400` (Regular)   | UI Font            | Default paragraph and body text.       |
| Data           | `1rem` (16px)     | `400` (Regular)   | **Data/Mono Font** | All numerical data (P&L, prices, etc). |
| Small / Label  | `0.875rem` (14px) | `400` (Regular)   | UI Font            | Labels, captions, secondary info.      |

---

## 3 · Component & Element Styling

### 3.1 · Cards & Containers

- **Background**: `bg-secondary` (`#1F2937`).
- **Border**: `1px solid` using `border` color (`#374151`).
- **Shadow**: Avoid heavy shadows. Use borders for separation. A very subtle glow on hover for interactive cards is acceptable.
- **Padding**: `1.5rem` (24px) should be the standard internal padding.

### 3.2 · Buttons

- **Primary**: `bg-primary` (`#3B82F6`) background, `text-primary` (`#F9FAFB`) text.
- **Secondary**: `bg-secondary` background, `text-primary` text, `1px solid` `border` color.
- **Destructive**: `bg-danger` (`#EF4444`) background, `text-primary` text.
- **State**: All buttons should have clear `:hover` (e.g., `primary-hover`), `:focus` (visible outline ring with `primary` color), and `:disabled` (reduced opacity, `text-tertiary` color) states.
