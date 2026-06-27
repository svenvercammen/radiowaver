---
name: Heritage Pulse
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#404848'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#717978'
  outline-variant: '#c0c8c8'
  surface-tint: '#3b6566'
  primary: '#002627'
  on-primary: '#ffffff'
  primary-container: '#0f3d3e'
  on-primary-container: '#7da8a8'
  inverse-primary: '#a3cfcf'
  secondary: '#b51c0d'
  on-secondary: '#ffffff'
  secondary-container: '#d93724'
  on-secondary-container: '#fffbff'
  tertiary: '#242213'
  on-tertiary: '#ffffff'
  tertiary-container: '#3a3727'
  on-tertiary-container: '#a5a08b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#beebeb'
  primary-fixed-dim: '#a3cfcf'
  on-primary-fixed: '#002020'
  on-primary-fixed-variant: '#224d4e'
  secondary-fixed: '#ffdad4'
  secondary-fixed-dim: '#ffb4a7'
  on-secondary-fixed: '#400100'
  on-secondary-fixed-variant: '#920600'
  tertiary-fixed: '#e9e2cc'
  tertiary-fixed-dim: '#cdc6b1'
  on-tertiary-fixed: '#1e1c0e'
  on-tertiary-fixed-variant: '#4a4736'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  headline-xl:
    fontFamily: Chivo
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Chivo
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-md:
    fontFamily: Chivo
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-lg:
    fontFamily: Work Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Work Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-bold:
    fontFamily: Work Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-sm:
    fontFamily: Work Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

This design system is built for a local radio station that bridges the gap between community heritage and modern broadcasting. The brand personality is **reliable, neighborly, and authoritative**, evoking the feeling of a trusted local voice that is always "on."

The visual style is **Modern Corporate with Editorial influences**. It avoids the sterile coldness of pure tech by utilizing a warm, paper-inspired background and structured layouts that feel like a contemporary gazette. It prioritizes high legibility and clear functional hierarchy to ensure accessibility for all age groups within the local community. The UI feels established and grounded, using substantial weights and clear boundaries to define the "Radio Waver" experience.

## Colors

The palette is derived directly from the station's heritage identity, focusing on high-contrast pairings for maximum readability.

- **Primary (Deep Sea Blue/Antraciet):** Used for primary navigation, headers, and the most critical interface containers. It provides the "anchor" for the design.
- **Secondary (Signal Red):** Reserved strictly for "Live" indicators, the primary radio play button, and urgent alerts. It creates a sense of immediacy.
- **Tertiary (Vintage Crème):** Used as the primary background color. It is softer on the eyes than pure white, providing a sophisticated, tactile feel reminiscent of classic broadcasting.
- **Neutral:** A range of deep grays for secondary text and borders to maintain professional clarity.

## Typography

The typography system relies on **Chivo** for headlines to provide a bold, confident, and slightly industrial character that mimics classic radio branding. **Work Sans** is used for body copy and labels because of its exceptional legibility at small sizes and its friendly, open apertures.

Hierarchy is strictly enforced. Large headlines use a heavier weight and tighter letter-spacing for a modern, impactful look. Body text maintains a generous line height to ensure that news articles and schedule lists remain readable for older audiences.

## Layout & Spacing

The design system utilizes a **Fixed Grid** model on desktop (12 columns) and a **Fluid Grid** on mobile (4 columns). The layout philosophy is "Information First," utilizing a structured 8px spacing scale to create clear groupings of content.

- **Desktop:** 1280px max-width container with 24px gutters.
- **Tablets:** Fluid widths with 24px gutters and 32px side margins.
- **Mobile:** Single column layout with 16px side margins.

Content blocks (such as the daily schedule or news feeds) use consistent vertical padding of 48px to 64px to allow the design to breathe, preventing the interface from feeling cluttered or "noisy."

## Elevation & Depth

To maintain a "Professional & Local" feel, the system avoids heavy drop shadows and modern blurs. Instead, it uses **Tonal Layering** and **Crisp Outlines**.

- **Level 0 (Base):** The Tertiary Crème background.
- **Level 1 (Cards/Sections):** White or slightly lighter crème surfaces with a 1px solid border in a low-opacity Neutral.
- **Level 2 (Active Elements):** Primary color containers for high-priority sections.
- **The Player Bar:** This element is permanently pinned to the bottom of the viewport with a high-contrast background (Primary Blue) and a sharp 2px top border to distinguish it from the content scrolling beneath it.

## Shapes

The shape language is **Soft (0.25rem)**. This subtle rounding maintains a professional and architectural feel while removing the "sharp edges" that can make a UI feel aggressive. 

Buttons and input fields follow this subtle rounding. The only exception is the **Main Play Button** in the radio player, which is a perfect circle to emphasize its status as the primary action of the entire platform.

## Components

### The Radio Player (Sticky)
The most prominent component. It should use the Primary Blue background with white text/icons. The Play/Pause button is a large, circular Secondary Red button with a white icon. Include a "Live" badge using a pulsing animation.

### Buttons
- **Primary:** Solid Primary Blue, White text, 4px radius.
- **Secondary:** Outline Primary Blue, 1px border, 4px radius.
- **Live Button:** Solid Red, used exclusively for the broadcast status.

### Cards
Cards for news or upcoming shows should use a white background with a 1px neutral border. Headline typography within cards should be `headline-md`.

### Schedule List
A vertical list with clear time indicators. Use `label-bold` for timestamps and `headline-sm` for show titles. Alternate row backgrounds slightly using a 5% opacity tint of the primary color to aid horizontal eye tracking.

### Input Fields
Strict, rectangular fields with a 4px radius and a 1px neutral-gray border. On focus, the border should thicken to 2px Primary Blue.