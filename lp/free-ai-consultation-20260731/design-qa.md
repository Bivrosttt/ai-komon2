# Construction editorial hero responsive QA

## Comparison target

- Source visual truth: `/var/folders/l8/d8zmnc8x3zsf4nn0r9l0pfzm0000gn/T/TemporaryItems/NSIRD_screencaptureui_KVCu2I/スクリーンショット 2026-07-31 23.02.57.png`
- Latest issue evidence: `/var/folders/l8/d8zmnc8x3zsf4nn0r9l0pfzm0000gn/T/TemporaryItems/NSIRD_screencaptureui_BUbJmY/スクリーンショット 2026-07-31 23.15.28.png` and `/var/folders/l8/d8zmnc8x3zsf4nn0r9l0pfzm0000gn/T/TemporaryItems/NSIRD_screencaptureui_8yELID/スクリーンショット 2026-07-31 23.15.55.png`
- Latest bridge-section reference: `/var/folders/l8/d8zmnc8x3zsf4nn0r9l0pfzm0000gn/T/TemporaryItems/NSIRD_screencaptureui_9bUtpo/スクリーンショット 2026-07-31 23.37.56.png`
- Rendered implementation: `http://127.0.0.1:4173/lp/free-ai-consultation-20260731/kensetsu.html?layout=editorial`
- Combined comparison: `/tmp/kensetsu-qa-comparison.png`; latest implementation captures: `/tmp/kensetsu-v4-1440.png`, `/tmp/kensetsu-v4-390.png`
- State: construction editorial hero, top of page, no interaction state
- Viewport: 749 x 865 CSS px
- Source pixels: 1498 x 1730, normalized to 749 x 865 from the supplied 2x screenshot
- Implementation pixels: 749 x 865, browser screenshot at 1x

## Evidence

- Full-view comparison: the supplied screenshot is on the left of the combined comparison and the revised implementation is on the right. The revised copy keeps the same visual hierarchy, colors, CTA treatment, and editorial/photo split while removing the broken mid-phrase wrapping.
- Focused region comparison: hero title, lead, offer, and CTA were readable at the normalized viewport. A separate focused crop was not needed because the entire above-the-fold hero remained legible at 749 x 865.
- Responsive checks: at 390 x 844, `scrollWidth === clientWidth === 390`; at 749 x 865, `scrollWidth === clientWidth === 749`; at 1440 x 900, `scrollWidth === clientWidth === 1440`.
- Primary CTA check: all four `[data-cta]` links resolve to `/lp-zukai.html?from=free_consult_kensetsu#contact`.
- Browser console/page errors: none reported by `agent-browser errors`.
- Latest visual check: the two newly supplied issue screenshots were reviewed against the v4 captures. The media image keeps a 1.777 aspect ratio at both desktop and tablet crops, and the hero no longer renders the duplicate offer row.

## Findings

- [P1] The previous implementation hid the semantic hero on desktop and relied on a fixed raster creative, while the narrower responsive state allowed the headline to break at `いまの業務...` in the middle of the phrase. This caused the screenshot's visible overflow and made the copy difficult to read.
  - Fix: keep the hero as HTML at every breakpoint, use the photo only as the media visual, remove the desktop raster-artboard handoff, enable the intended line breaks, and scale the headline with `clamp()`.
- [P2] The previous mobile/tablet rules suppressed authored `<br>` elements and used fixed headline sizing, so the same copy behaved differently across viewport widths.
  - Fix: retain authored line breaks, use `word-break: keep-all`, responsive headline/lead sizing, and constrained CTA width.
- [P1] The media photo was previously scaled with independent background width/height values, visibly distorting the people and room.
  - Fix: render the source creative as a positioned image, preserve its native 1672:941 ratio, and crop the non-photo side instead of stretching it.
- [P2] The hero repeated the same offer in the orange offer label and the CTA.
  - Fix: hide the redundant hero offer row and use `コンサル1回分を無料申し込み` as the CTA text across the page.

## Comparison history

1. Before: at 749 x 865, the headline rendered as `AIを使いたい。まずは、い / まの業務を聞かせてくださ / い。`; the photo was below the fold and the layout had no reliable narrow-width composition.
2. Fix: replaced fixed desktop-artboard display with responsive HTML composition and updated breakpoint typography/wrapping rules.
3. After: at 749 x 865, the headline renders as `AIを使いたい。 / まずは、いまの業務を / 聞かせてください。`; at 390 x 844 it remains readable with no horizontal overflow; at 1440 x 900 the editorial split and photo render correctly.
4. Second fix: replaced independently-sized background rendering with aspect-ratio-preserving image cropping; removed the repeated offer row; changed the CTA to `コンサル1回分を無料申し込み`; rechecked at 1440 x 900 and 390 x 844 with no overflow or browser errors.
5. Bridge update: changed the abstract section headline to `例えば、こんな業務を効率化できます。`, added 12 construction-specific candidate tasks in a bullet-card grid, and retained the photo-ledger quote as a clearly labeled industry example. Verified at 749 x 865 and 1440 x 900.

## Latest bridge-section QA

- Implementation screenshots: `/tmp/kensetsu-bridge-749b.png` at 749 x 865 and `/tmp/kensetsu-bridge-1440.png` at 1440 x 900.
- Full-view evidence: the section now leads with a concrete promise, shows the candidate work in a scan-friendly 3-column desktop grid / 1-column mobile list, then presents the construction example and supporting image.
- Content evidence: 12 task items rendered from `data.js`; the example quote remains separate from the broad candidate list.
- Responsive evidence: `scrollWidth === clientWidth` at both 749 and 1440; no browser errors reported.
- Finding resolved: the previous section asked the visitor to infer what AI might do from a single photo-ledger story. The new list makes the possible scope visible without promising every item will apply to every company.
- Cross-industry check: `fudosan.html`, `seizo.html`, `unsou.html`, and `shukuhaku.html` each render the same concrete heading, 12 industry-specific tasks, and an industry-labeled example at 390 x 844 with no horizontal overflow.

## Latest first-view alignment QA

- Reference implementation: `/tmp/kensetsu-v4-1440.png` (approved construction editorial hero).
- Comparison implementation: `/tmp/seizo-editorial-1440.png` and `/tmp/seizo-editorial-390.png`.
- Verified pages: `kensetsu.html`, `fudosan.html`, `seizo.html`, `unsou.html`, and `shukuhaku.html`.
- At 1440px, all pages use `layout-editorial`, the same hero photo, title line breaks, CTA text, hidden duplicate offer row, and no horizontal overflow.
- At 390px, the same editorial composition stacks responsively with no horizontal overflow; the industry label is the only first-view copy variation.
- Finding resolved: non-construction pages previously used the generic hero by default. `app.js` now defaults every industry page to the approved editorial layout, while preserving `?layout=poster` as an explicit alternate.

## Latest industry-image QA

- The editorial layout remains identical, but the hero image now changes by industry: `kensetsu-bg.png`, `fudosan-bg.png`, `seizo-bg.png`, `unsou-bg.png`, and `shukuhaku-bg.png`.
- Rendered checks at 1440px confirmed the five distinct image URLs, matching industry scenes, identical copy layout, and no horizontal overflow.
- Rendered checks at 390px confirmed the same five image assignments, responsive image crops, and `scrollWidth === clientWidth` for every page.
- The shared image was removed from the default editorial and poster hero assignments; the industry-specific background remains the only visual variation in the first view besides the industry label.

## Required fidelity surfaces

- Fonts and typography: preserved the existing Hiragino/Yu Gothic stack, navy hierarchy, weight contrast, and negative tracking; corrected responsive size and wrapping.
- Spacing and layout rhythm: retained the screenshot's left-column hierarchy, offer-to-CTA relationship, and media split; made padding and hero media height responsive.
- Colors and visual tokens: preserved the off-white background, navy text/CTA, and ochre accent.
- Image quality and asset fidelity: retained the supplied editorial consultation image as a native-ratio positioned image; no placeholder or CSS-drawn image was introduced.
- Copy and content: preserved the requested construction message and authored line breaks; CTA is `コンサル1回分を無料申し込み` and the duplicate hero offer is removed.

## Implementation checklist

- [x] Responsive HTML hero at desktop, tablet, and mobile widths
- [x] Natural Japanese line breaks without horizontal overflow
- [x] Desktop photo split preserved
- [x] Mobile image remains visible below the copy
- [x] CTA destination verified
- [x] Browser errors checked
- [x] Industry-specific candidate work list rendered
- [x] Bridge section verified at tablet and desktop widths

## Follow-up Polish

- [P3] The screenshot and browser render use different device pixel densities, so pixel-level antialiasing will naturally differ after normalization.

final result: passed
