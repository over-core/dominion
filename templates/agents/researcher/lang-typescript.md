# TypeScript Research Patterns

When researching TypeScript projects:

- Use `package.json` / `tsconfig.json` for project structure analysis
- Check strict mode: `strict: true` in tsconfig indicates mature project
- Note framework: React, Next.js, Express, NestJS, Fastify
- Check bundler: webpack, vite, esbuild, turbopack
- Identify state management: Redux, Zustand, Jotai, MobX
- Check test framework: Jest, Vitest, Playwright, Cypress

## TypeScript-Specific Risks

- `any` type proliferation defeating type safety
- Module resolution issues (ESM vs CJS)
- Bundle size regressions from large dependency additions
- Missing null checks despite strict mode
