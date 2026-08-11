---
name: Merkaz
description: Community file library for Merkaz Tze'irim / Kfar Kama. Operate-mode app UI.
colors:
  brand: "#e6b422"
  brand-strong: "#d4a41a"
  brand-soft: "#fff6d6"
  ink: "#1c2430"
  ink-hover: "#2a3444"
  mist-bg: "#e8eef2"
  warm-mist: "#f3f0e6"
  text: "#14181f"
  text-muted: "#5a6470"
  surface: "#ffffff"
  surface-subtle: "#f4f6f8"
  border: "#dce3e8"
  danger-bg: "#fceceb"
  danger-text: "#b42318"
  success: "#1f7a3f"
typography:
  title:
    fontFamily: "Assistant, Segoe UI, sans-serif"
    fontSize: "1.7rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Assistant, Segoe UI, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Assistant, Segoe UI, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Assistant, Segoe UI, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 600
    letterSpacing: "0.04em"
rounded:
  sm: "8px"
  md: "12px"
  lg: "18px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "28px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "12px 16px"
  button-primary-hover:
    backgroundColor: "{colors.ink-hover}"
    textColor: "#ffffff"
  button-secondary:
    backgroundColor: "#eef1f4"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "8px 14px"
  button-brand-soft:
    backgroundColor: "{colors.brand-soft}"
    textColor: "#6a5208"
    rounded: "{rounded.sm}"
    padding: "6px 11px"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "22px 28px"
  input:
    backgroundColor: "{colors.surface-subtle}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "12px 14px"
---

# Design System: Merkaz

## Overview

**Creative North Star: "The Mustard Brush Desk"**

Merkaz is an Operate-mode file library: browse, upload, approve, administer. The visual world comes from the community brand mark (Hebrew bold type on a mustard brushstroke for מרכז צעירים / K Φ A P - K A M A). The UI should feel like a calm community desk, not a SaaS dashboard template and not Material leftovers.

Personality is warm, clear, and competent. Density is medium: tables and admin tools need scan speed; auth and upload get breathing room. Brand yellow is rare and intentional. Ink handles primary commitment. Soft mist backgrounds and white panels carry the work surface.

**Key Characteristics:**
- Mustard brand accent on focus, active tabs, and soft action fills
- Ink primary buttons in light mode; brand yellow primary in dark mode
- Centered panels (`max-width` ~1080px) floating on mist with soft panel shadows
- Assistant typeface throughout
- Overflow admin actions collapse into a vertical 3-dot menu

## Colors

Palette is cool mist neutrals with one warm brand voice from the logo.

### Primary
- **Mustard Brand** (`#e6b422`): Focus rings, active admin tabs, progress fill, soft action fills (`#fff6d6`). Used sparingly.
- **Desk Ink** (`#1c2430`): Primary CTAs and high-commitment controls in light mode.

### Neutral
- **Cool Mist** (`#e8eef2`): Page background, with soft radial brand wash.
- **Paper Surface** (`#ffffff`): Main panels and cards.
- **Subtle Well** (`#f4f6f8`): Inputs, nested wells, strip backgrounds.
- **Ink Text** (`#14181f`) / **Muted Text** (`#5a6470`): Body and secondary copy.
- **Hairline Border** (`#dce3e8`): Dividers and panel edges.

### Semantic
- **Danger** (`#fceceb` / `#b42318`): Delete and deny.
- **Success** (`#1f7a3f`): Approve / approved status.

**The One Brush Rule.** Brand yellow appears as accent or soft fill, never as large decorative gradients or purple-tinted AI skins.

## Typography

**Display / Body Font:** Assistant (Segoe UI fallback)

**Character:** Friendly Hebrew-capable sans with clear weights. No Inter. No display serif cosplay.

### Hierarchy
- **Title** (700, ~1.7rem, -0.02em): Auth page titles.
- **Headline** (700, ~1.35rem, -0.02em): Panel headers ("Admin Dashboard", "Upload files").
- **Body** (400–600, ~0.9–0.95rem): Table cells, forms, descriptions.
- **Label** (600, ~0.78–0.82rem, optional uppercase tracking): Field labels and table headers.

**The Sentence Case Rule.** UI headings use sentence case ("Sign in", "Upload files"), not Title Case Everywhere.

## Layout

Operate layout: full-viewport shell (`#root` flex column), page roots center a single floating panel. Panel max width ~1000–1080px. Auth cards max ~420px. Horizontal padding ~16–28px. Breakpoint mobile at 768px: panels go edge-to-edge, drop shadow, fill height.

Table rows stay single-line on desktop. Actions that do not fit move into the 3-dot menu (Edit / Delete for admins). Preview and Download stay visible.

### Mobile Adapt (≤768px)

Desktop (≥769px) panels and tables stay unchanged. On phones:

- Full-bleed Operate panels; auth uses the same 768 breakpoint.
- No page-level horizontal scroll (`overflow-x: clip` on shell). Admin tab strip may scroll internally.
- Dense tables become stacked row-cards via CSS (`data-label` on cells); `thead` hidden.
- Headers, path bar, and footer stack; search and primary actions go full width.
- Safe-area insets for notch / home indicator; theme toggle clears the brand header.
- Touch / coarse pointer targets prefer ≥44px height.

## Elevation & Depth

Hybrid: soft ambient shadows plus hairline borders. Depth is structural for panels, not decorative glow.

### Shadow Vocabulary
- **Soft** (`0 10px 30px rgba(20, 24, 31, 0.08)`): Small chrome (theme toggle, menus).
- **Panel** (`0 18px 48px rgba(20, 24, 31, 0.1)`): Auth cards, dashboard/admin containers, modals.
- **Focus** (`0 0 0 3px rgba(230, 180, 34, 0.35)`): Keyboard focus using brand yellow.

**The Resting Flat Rule.** Rows and list items are flat. Lift belongs to the page panel and open menus/modals.

## Shapes

Gentle continuous radii: controls 8px, wells/tables 12px, page panels 18px. Theme toggle and some icon buttons use full pills. No hard neubrutal offset shadows. No Material circular FABs as primary language.

## Components

### Buttons
- **Shape:** Gently curved (8px).
- **Primary:** Ink fill, white text, 12×16 padding; hover to `#2a3444`. Dark mode flips primary to brand yellow with ink text.
- **Secondary:** Soft gray fill (`#eef1f4`).
- **Brand soft:** Mustard wash for Preview / Create folder.
- **Danger:** Soft red fill for Delete / Deny.
- **Focus:** Brand yellow ring.

### Cards / Containers
- **Corner:** 18px panel radius.
- **Background:** Paper white / dark charcoal.
- **Border:** Hairline `#dce3e8`.
- **Shadow:** Panel shadow.
- **Padding:** ~22×28 desktop.

### Inputs / Fields
- **Style:** Subtle well background, hairline border, 8px radius.
- **Focus:** Brand border + focus ring.
- **Labels:** Small muted semibold above fields.

### Navigation
- Admin tabs: muted default, active gets ink text + 3px brand underline.
- Dashboard header: logo + welcome + compact action cluster.

### Row action menu (signature)
- Vertical 3-dot trigger (34×32).
- Menu panel: paper surface, soft shadow, Edit path + Delete.
- Preview and Download remain inline.

### Upload dropzone
- Dashed border well; hover/drag uses brand border and brand-soft fill.

## Do's and Don'ts

### Do:
- **Do** keep brand yellow rare and meaningful (focus, active, soft fills).
- **Do** center Operate panels on mist; keep `#root` filling the viewport.
- **Do** collapse overflowing row actions into the 3-dot menu.
- **Do** use Assistant and sentence-case headings.
- **Do** preserve logo assets at `/assets/icons/banner-logo.webp` and dark variant.

### Don't:
- **Don't** reintroduce Material purple, Inter, or generic AI gradient heroes.
- **Don't** wrap four action buttons into multi-line table cells.
- **Don't** use emoji as icons; use the SVG set in `client/src/components/Icons.tsx`.
- **Don't** treat SPA routes like `/uploads` as API 404s (Flask/Vite prefix collision is a known trap).
- **Don't** bring back the challenge/puzzle shell unless product asks for it.
