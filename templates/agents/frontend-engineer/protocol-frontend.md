# Frontend Engineering Protocol

## Component Architecture

1. **Component-driven development** — build from atoms up. Each component: one responsibility, clear props interface, testable in isolation.
2. **Server vs client components** — use server components by default (Next.js/Nuxt/SvelteKit). Client components only when interactivity requires it (event handlers, state, browser APIs).
3. **State management** — local state first (useState/reactive). Lift state up when shared. Global store (Redux/Zustand/Jotai) only for truly global state (auth, theme, feature flags).
4. **Follow existing patterns** — check how the codebase structures components before creating new patterns.

## Accessibility (WCAG 2.2 AA)

Non-negotiable requirements:
- Semantic HTML — use `<button>` not `<div onClick>`, `<nav>` not `<div class="nav">`
- Keyboard navigation — all interactive elements focusable and operable via keyboard
- ARIA labels — for custom widgets, icon buttons, dynamic content updates
- Color contrast — minimum 4.5:1 for normal text, 3:1 for large text
- Focus management — visible focus indicators, logical tab order
- Run axe-core or similar automated audit tool as verification step

## Performance

1. **Core Web Vitals** — LCP < 2.5s, INP < 200ms, CLS < 0.1
2. **Bundle optimization** — code split by route, lazy-load below-the-fold components, tree-shake unused code
3. **Image optimization** — next/image or equivalent, WebP/AVIF formats, responsive srcset, lazy loading
4. **Avoid layout shifts** — explicit dimensions on images/videos, font-display: swap with size-adjust

## Styling

- Follow the existing approach (CSS modules, Tailwind, styled-components, etc.) — don't introduce a new system
- Design tokens for colors, spacing, typography — never hardcode values
- Responsive design — mobile-first, use breakpoints from the design system
