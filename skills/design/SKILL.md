# skills/design — Premium UI Component Generation

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-DSN-001

---

## 1. Business Objective

Generate production-ready React/TypeScript UI components — with shadcn/ui, three.js, framer-motion, and Tailwind CSS — in under 30 seconds, following brand guidelines and responsive mobile-first patterns.

## 2. Inputs (Gherkin)

```gherkin
Given a user request for a UI component (hero, dashboard, card, form, etc.)
And the design system context is available (colors, typography, spacing)
When the component specification includes layout and interaction requirements
```

## 3. Outputs (Gherkin)

```gherkin
Then a complete .tsx component file is generated with all imports
And the component uses Tailwind classes (no inline styles)
And shadcn/ui primitives are used for base elements
And three.js with drei helpers is used for 3D components
And framer-motion handles all animations
```

## 4. Events

```
Events:
- design:component:created: a new UI component was generated
- design:pattern:applied: a design pattern was used
```

## 5. Dependencies

```
Dependencies:
- shadcn/ui: data — component primitives
- @react-three/drei: data — 3D helpers
- framer-motion: data — animation library
- Tailwind CSS: data — utility classes
- lucide-react: data — icons
```

## 6. Tools

```
Tools:
- llm_chat: generates component code from specification
```

## 7. Policies

```
Policies:
- Never generate full applications — only components/pages
- Never use inline styles — always Tailwind classes
- Never truncate code — always complete, runnable output
- Include exact imports for every library used
- Dark mode enabled by default (dark class on html)
- Responsive mobile-first layout required
- One component per file, one file per component
```

## 8. Success Metrics

```gherkin
Success Metrics:
- generation_time: Given request When component generated Then seconds
  Target: < 30 sec
- zero_modification: Given generated component When reviewed Then no manual edits needed
  Target: > 80%
- compile_rate: Given generated code When compiled Then zero TypeScript errors
  Target: > 95%
```

## 9. Failure Conditions

```
Failure Conditions:
- Missing imports: generated code references undeclared libraries (detect via TypeScript check)
- Type mismatch: prop types incompatible (detect via tsc compilation)
- Runtime animation error: framer-motion conflict (detect via browser console)
- Three.js WebGL incompatibility: canvas render error (detect via error event)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. Re-request generation with more specific constraints
2. If TypeScript errors → manually add missing imports, retry
3. If animation errors → simplify motion props, fall back to CSS transitions
4. If WebGL fails → provide non-3D fallback component
5. Log failures to state/logs/skills/design.log
```

## 11. Business Value

```
Business Value: Premium UI components in under 30 seconds.
```

## 12. Parent OS

```
Parent OS: Dev
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-2026-DSN-001
- Events: design:component:created, design:pattern:applied
- Logs: state/logs/skills/design.log
```
