---
name: threejs-build
description: Three.js / react-three-fiber 3D scaffolding for Nortropic Next.js 15 sites. Use only when a PROJECT-BRIEF.md explicitly calls for a 3D element on a Swedish local service site (rare — a product configurator, a rotating 3D logo/hero, a map-like scene). Covers react-three-fiber + drei, SSR-safe dynamic import, performance budget for the prelaunch gate, and reduced-motion / low-power fallback. Trigger with /threejs-build, or when asked to add a 3D scene to a client site.
argument-hint: "[component-or-page]"
---

# Three.js on a Nortropic site

**Default answer: don't.** A local plumber/electrician/cleaner lead-gen site almost never needs WebGL — it adds weight, drains battery, and risks the Lighthouse/CWV gate. Only build a 3D scene when the brief names a concrete conversion reason (e.g. a configurator that helps quote a job). If in doubt, use a video/image or a GSAP effect instead.

## Install (per project)

```bash
pnpm add three @react-three/fiber @react-three/drei
pnpm add -D @types/three
```

## SSR-safe rule (non-negotiable in App Router)

Three.js needs `window`/WebGL, which don't exist during SSR. The scene must be a `"use client"` component, **dynamically imported with `ssr: false`**, wrapped in a small loader placeholder so the page still statically renders its real content.

```tsx
// app/(page)/Scene.tsx  — "use client", the actual R3F canvas
"use client";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stage } from "@react-three/drei";

export default function Scene() {
  return (
    <Canvas dpr={[1, 2]} frameloop="demand" camera={{ position: [0, 0, 5] }}>
      <Stage>{/* mesh here */}</Stage>
      <OrbitControls makeDefault enablePan={false} />
    </Canvas>
  );
}
```

```tsx
// Usage in a Server Component page — never import Scene directly
import dynamic from "next/dynamic";
const Scene = dynamic(() => import("./Scene"), {
  ssr: false,
  loading: () => <div className="aspect-video animate-pulse rounded-lg bg-muted" />,
});
```

## Performance budget (the gate that usually fails)

- `three` + R3F + drei is **~600 KB+ gz**. This is the single heaviest thing you can add to a Nortropic site. It MUST be code-split (dynamic import above) and MUST NOT load on any page that doesn't use it.
- **`frameloop="demand"`** — render only on change/interaction, not a continuous rAF loop (saves battery, stops the fan spinning). Continuous loops only for genuinely animated scenes, and pause them when off-screen (IntersectionObserver) and when the tab is hidden.
- **`dpr={[1, 2]}`** to cap pixel ratio on retina; keep polygon counts and texture sizes small; compress GLTF/textures (draco/ktx2) before shipping.
- Verify the page still passes **Lighthouse Performance + CWV** in `nortropic-prelaunch`. If it drops below the gate, the 3D element is cut or replaced with a pre-rendered image/video.

## Accessibility & fallback

- **prefers-reduced-motion**: no auto-rotation/auto-animation when reduce is set — render a static frame or a fallback image.
- **Low-power / no-WebGL**: provide an `<img>`/`<video>` fallback (feature-detect WebGL). The scene is never the only way to get the site's message or the phone number.
- **Never trap focus or block the CTA.** The phone CTA (`<PhoneLink>`, sticky header, floating call button) stays visible and tappable regardless of the canvas.

## Nortropic fit

Acceptable: a single small hero object, a product/job configurator that genuinely aids the quote. Anti-slop: full-screen WebGL backgrounds, spinning logos, particle fields, anything that exists only to look "techy" on a tradesperson's site.

See also: `nortropic-antislop`, `nortropic-prelaunch`, `gsap-build` (lighter alternative), `imagegen-frontend-web`.
