---
name: ui-architect
description: Given any existing UI (from a GitHub repo, npm package, URL, pasted code, or even a screenshot/description), analyze it and produce a complete, future-proof replication guide that another agent can follow to BUILD the UI from scratch using the LATEST versions of everything. Trigger this whenever the user asks you to analyze, break down, reverse-engineer, or replicate a UI — phrases like "how does this UI work", "build me something like this", "what's the architecture of this", "can you recreate this screen", "what dependencies does this use", "figure out how this is built". Also trigger when the user pastes code or a URL and asks you to study it. Do NOT trigger for pure backend, API, or logic-only tasks with no UI component.
---

# UI Architect

A skill that takes any existing user interface — from any framework, any platform, any age — and produces a **future-proof replication spec**: a detailed technical document another agent can follow to BUILD that UI from scratch with the latest versions of all dependencies.

## Why This Exists

Codebases rot. A tutorial from 2022 uses `react-native-gifted-chat@1.0.0`, but the world is at `3.3.3` now. A Flutter chat UI from 2023 uses an old `provider` pattern, but `riverpod` is the modern approach. A SwiftUI example from last year used `@available(iOS 15, *)` APIs, but now iOS 18 changes everything.

This skill exists so that when someone says "build me a chat like this one" and points at a 2-year-old repo, the agent doesn't just copy-paste the obsolete code. Instead, it:

1. **Researches the original** — understands what the UI does at a functional level
2. **Maps to the present** — finds the LATEST versions of every library, framework, and API
3. **Documents the gap** — notes what changed, what broke, what's better now
4. **Produces a build-ready spec** — so another agent (or the same agent later) can implement it fresh

## The Core Workflow

```
User: "Here's a UI. Build me a replication guide."
  │
  ▼
Phase 1: INPUT — Determine what the user provided
  │ (URL? GitHub repo? npm package? Code snippet? Screenshot?)
  ▼
Phase 2: RESEARCH — Deep-dive into the original
  │ (Source code, docs, dependencies, architecture)
  ▼
Phase 3: MODERNIZE — Find latest equivalents
  │ (npm registry, pub.dev, Swift Package Index, web search)
  ▼
Phase 4: REPORT — Write the replication spec
  │ (Comprehensive markdown saved to filesystem)
  ▼
Phase 5: HANDOFF — Tell the user where the report is
  (They can now build from it or hand it to another agent)
```

---

## Phase 1: Identify the Input

The user might give you the UI in many forms. Figure out which one and adjust your approach.

### Type A: GitHub Repository URL
Someone built it. You can read the source.
- Clone or fetch the repo (read only, don't modify)
- Read `package.json`, `pubspec.yaml`, `Podfile`, `build.gradle` — get the dependency list
- Read the README — what is this thing?
- Explore the source tree — find the main UI components
- Trace the component hierarchy from entry point to leaf
- Look at the example app if there is one

### Type B: npm / PyPI / pub.dev Package
Someone published it. It's a library or a starter template.
- Fetch the package page — read description, version, dependencies
- Read the docs site if linked
- Look for a GitHub link and read the source
- Check the tag for the latest version

### Type C: Raw Code Snippet
The user pasted code directly.
- Read the code carefully
- Identify the framework (RN, SwiftUI, Flutter, web)
- Note any imports/requires — these reveal dependencies
- Infer the component structure from the code

### Type D: Screenshot / Description
No code, just a visual or a description.
- Ask clarifying questions if needed
- Infer the framework from context clues
- Research similar UIs in the likely framework
- Document your assumptions in the report

### Type E: URL to a Live App
- Use web fetch to understand what's there
- Note it's a live app so you can only observe behavior, not read internals
- Document what you can observe: animations, scroll behavior, keyboard handling, layout

---

## Phase 2: Deep Research

Once you have access to the source (or as much as you can get), research these aspects. Each of these goes into the report.

### 2.1 — What Is This UI? (Metadata)
| Field | What to capture |
|---|---|
| Name | What is this UI/screen/component called? |
| Source | Where did we get it? (URL, path, etc.) |
| Original Framework | React Native, Flutter, SwiftUI, Web (React, Vue, Svelte), etc. |
| Original Versions | Every dependency with its EXACT version from the original |
| Purpose | What does this UI do? (chat, feed, form, dashboard, etc.) |

### 2.2 — Architecture
- Full component/provider hierarchy
- How is the screen assembled? Which components wrap which?
- Navigation approach (stack, tab, custom navigator)
- State management (Context, Redux, Riverpod, ObservableObject, etc.)

### 2.3 — Dependencies (Original)
List every dependency the original uses, with versions. Group by category:
- **Framework**: react-native@0.72.0, flutter 3.10, etc.
- **UI Components**: react-native-gifted-chat@1.0.0, etc.
- **Navigation**: react-navigation, Router, Navigator 2.0, etc.
- **Animations**: react-native-reanimated, Lottie, SwiftUI animations
- **Media**: image picker, video player, audio recorder
- **Network**: Apollo, tRPC, axios, URLSession, etc.
- **Utilities**: dayjs, zod, i18next, etc.

### 2.4 — UI Behavior (Functional Analysis)
This is the most important part. Document what the UI DOES, not just what it IS:

**Header:**
- What's in it? (back button, title, icons, avatars, etc.)
- How does it look? (transparent, blurred, solid, gradient)
- Does it change on scroll? (collapse, hide, color shift)
- How does the keyboard affect it?

**Input Bar (if applicable):**
- Where is it positioned? (absolute bottom, part of layout)
- TextInput behavior: multiline? placeholder? returnKeyType?
- Send button: when visible? animation? disabled state?
- Attachments: image picker, file picker, camera, voice?
- Auto-grow: min/max height, scroll when tall?
- Submit flow: what happens on send?

**Scrolling:**
- What's the container? (FlatList, ScrollView, UICollectionView, List)
- Is it inverted? (newest at bottom)
- Auto-scroll on new content? Animated? Debounced?
- Scroll-to-bottom button? When visible?
- Pagination / load more?

**Keyboard Handling:**
- How does the UI avoid the keyboard?
- Any keyboardVerticalOffset? How is it calculated?
- keyboardDismissMode? keyboardShouldPersistTaps?
- Platform differences?

**Content Items:**
- How is each item laid out? (flexDirection, alignment)
- Avatar: position, visibility rules, fallback (initials, icon)
- Text: link detection, markdown, custom fonts
- Media: gallery grid, video player, audio player
- Status indicators: ticks for sent/delivered/read/failed
- Reactions: position, style, interaction
- Replies/threads: how are they shown?

**Animations:**
- Typing indicator: how do the dots animate?
- Message insertion: fade in, slide in, instant?
- Reply preview: mount/unmount animation?
- Day separator: scroll-based fade?
- Any gesture-driven animations?

**Edge Cases:**
- Empty state
- Loading state
- Error state (send failure, network)
- Streaming content (AI typing)
- Offline behavior
- Accessibility features

---

## Phase 3: Modernization Research

This is what makes the skill different from a simple analysis. For EVERY dependency found in Phase 2, you MUST:

### 3.1 — Find the Latest Version
For each package, determine the CURRENT latest stable version. Use:
- `npm view <package> version` (if Node/npm available)
- Web search "[package] npm latest version"
- pub.dev, Swift Package Index, Maven Central, etc.

### 3.2 — Map to Modern Equivalent
Some libraries are deprecated or superseded. If so, find the modern replacement:
- `react-navigation` -> `expo-router` (in Expo projects)
- `Redux` -> `Zustand` / `Jotai` / Context
- `axios` -> `fetch` / `tRPC`
- Old animation patterns -> Reanimated 4 worklets
- `Provider` (Flutter) -> `Riverpod`

### 3.3 — Document Breaking Changes
For each package where the version changed significantly:
- What breaking changes happened between original version and latest?
- What does a migration look like?
- Are there new setup steps? (babel plugins, config files, native module linking)

### 3.4 — Research Gotchas
Search for known issues with the latest versions:
- "react-native-keyboard-controller version X issues"
- "react-native-reanimated 4 migration problems"
- "X library not compatible with Y framework version"
- Android-specific and iOS-specific gotchas

### 3.5 — Build the Version Table

```markdown
## Dependency Map: Original → Latest

| Package | Original | Latest | Breaking? | Notes |
|---|---|---|---|---|
| react-native | 0.72.0 | 0.81.5 | Yes | New architecture enabled by default |
| react-native-gifted-chat | 1.0.0 | 3.3.3 | Yes | Now requires reanimated + gesture-handler + keyboard-controller |
| react-native-reanimated | 2.x | 4.2.1 | Yes | New babel plugin, worklets syntax changes |
| ... | ... | ... | ... | ... |
```

---

## Phase 4: Write the Replication Spec

Save the report to a file. Use this naming convention:

```
ui-specs/ui-name-<descriptive-name>.md
```

For example:
- `ui-specs/chat-ui-expo-ai.md`
- `ui-specs/photo-feed-instagram-clone.md`
- `ui-specs/e-commerce-product-page.md`

### Report Structure

```markdown
# [UI Name] — Replication Spec

**Analyzed from:** [source]
**Analysis date:** [YYYY-MM-DD]
**Target framework:** [React Native / Flutter / SwiftUI / Web]
**Target platform:** [iOS / Android / Web / Cross-platform]
**Estimated effort:** [rough estimate, e.g. "2-3 days for experienced dev"]

---

## 1. What This UI Does

[A 2-3 sentence summary of the UI's purpose and key interactions]

## 2. Recommended Stack (Build Fresh)

### Framework
| Choice | Version | Why |
|---|---|---|
| React Native | 0.81.5 | Latest stable, new arch enabled |
| Expo SDK | 54 | Manages native builds, OTA updates |
| TypeScript | 5.x | Type safety |

### Dependencies

| Package | Version | Category | Purpose |
|---|---|---|---|
| expo-router | ~6.x | Routing | File-based navigation |
| react-native-gifted-chat | 3.3.3 | UI | Chat messages & bubbles |
| react-native-reanimated | ~4.2.x | Animation | Keyboard tracking, transitions |
| react-native-gesture-handler | ~2.30.x | Gestures | Swipe-to-reply, touch handling |
| react-native-safe-area-context | ~5.x | Layout | Safe area insets |
| react-native-keyboard-controller | 1.x | Keyboard | Smooth keyboard avoidance |
| ... | ... | ... | ... |

### Installation Command
```bash
npx create-expo-app@latest MyApp --template blank-typescript
npx expo install react-native-gifted-chat react-native-reanimated react-native-gesture-handler react-native-safe-area-context react-native-keyboard-controller
```

## 3. Architecture

### Component Tree
```
App
  └── GestureHandlerRootView
       └── SafeAreaProvider
            └── KeyboardProvider
                 └── NavigationContainer / Expo Router
                      └── ChatScreen
                           ├── Stack.Navigator (header config)
                           ├── MessagesFlatList (inverted)
                           │    ├── MessageBubble (left/right)
                           │    ├── DaySeparator
                           │    ├── TypingIndicator
                           │    └── ScrollToBottomButton
                           └── InputToolbar
                                ├── ActionsButton
                                ├── Composer (TextInput)
                                └── SendButton
```

### Provider Hierarchy
```
GestureHandlerRootView
  └── SafeAreaProvider (react-native-safe-area-context)
       └── KeyboardProvider (react-native-keyboard-controller)
            └── Navigation provider
                 └── Screen content
```

## 4. Implementation Guide

### 4.1 — Setup & Providers

[Step-by-step code for setting up the required providers]

### 4.2 — Screen / Header

[How to configure the navigation header or custom header component]

### 4.3 — Message List

[How to set up the FlatList/ScrollView with inverted rendering, scroll-to-bottom, etc.]

### 4.4 — Keyboard Handling

[How to configure keyboard avoidance — exact offset values, props to pass]

### 4.5 — Input Toolbar

[How to build the input bar — TextInput config, send button, attachments]

### 4.6 — Message Bubbles

[How to render messages — layout, avatars, text, media, status]

### 4.7 — Animations

[Every animation with code snippets — typing indicator, reply preview, etc.]

### 4.8 — Edge Cases

[How to handle empty state, loading, errors, streaming]

## 5. Gotchas & Migration Notes

[The critical things that WILL go wrong if someone doesn't know about them]

### From the Original Version Analysis:
- The original used `react-native-gifted-chat@1.x` which had a different prop API. In v3.x, you now need `keyboardAvoidingViewProps`, the `reply` prop is restructured, and `react-native-keyboard-controller` is a required peer dep.
- `react-native-reanimated@4.x` requires a different babel plugin path than v2.x
- Android edge-to-edge changes in RN 0.76+ affect keyboard handling

### General Gotchas:
- `keyboardVerticalOffset` MUST include the navigation header height
- On Android with edge-to-edge, set `statusBarTranslucent` and `navigationBarTranslucent`
- Inverted FlatList means `ListHeaderComponent` renders at the visual bottom
- If using Expo, some native modules need Expo dev client (not Go)

## 6. Data Model

[TypeScript interfaces for the data driving this UI]

## 7. Original Analysis Reference

[Brief reference to the original source — what we analyzed, where it came from, the old dependency versions]
```

### What Makes a Great Spec

**DO:**
- Use imperative language for implementation steps ("Install X. Configure Y. Add Z.")
- Show real code snippets for critical parts (5-15 lines, not full files)
- Explain WHY something is done a certain way
- Include the EXACT installation commands
- Note every platform difference (iOS vs Android vs Web)
- Be specific about version numbers

**DON'T:**
- Don't just describe what you see — prescribe how to build it
- Don't copy old code verbatim — rewrite it for the latest APIs
- Don't say "the user should figure out keyboard offset" — tell them exactly what value to use and how to calculate it

---

## Phase 5: Handoff

When the report is written and saved, tell the user:

> "I've analyzed **[original UI name]** and produced a replication spec at **[file path]** . It covers:
> - **Architecture** — component tree, provider hierarchy, navigation
> - **Recommended stack** — latest versions of everything, with breaking changes mapped
> - **Implementation guide** — step-by-step with code snippets
> - **Gotchas** — what will trip you up if you're not careful
> - **Data model** — the shape of your data
>
> The spec is designed so that you (or another agent) can build this UI from scratch without ever looking at the original code. Want me to walk through any section, or start implementing?"

---

## Reference Files

The `references/` directory contains example specs produced by this skill. Read them before starting if you want to see the expected depth:

- `references/chat-ui-gifted-chat.md` — A spec for chat UI using react-native-gifted-chat
- `references/chat-ui-expo-ai.md` — A spec for Expo AI chat with RSC streaming
- `references/chat-ui-stream-chat.md` — A spec for Stream Chat React Native SDK
- `references/methodology.md` — The analysis methodology in detail (11 dimensions)

---

## Tips for Good Results

1. **Use subagents for parallel research** — while you read the original source, have another agent checking npm for latest versions and searching for gotchas. Don't do this sequentially.

2. **If npm view fails**, search the web for the latest version. Don't guess.

3. **If the original code has known bugs or issues**, note them in the gotchas section so the new implementation avoids them.

4. **If the original is very complex**, focus on the core UX patterns and note where the user might want to simplify or improve.

5. **If the user gives you a screenshot only**, document your assumptions clearly. Mark them as "ASSUMPTION" in the report.

6. **Always check React Native 0.76+ new architecture implications** — this affects keyboard handling, scroll behavior, and native module compatibility.
