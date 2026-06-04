---
name: ui-architect
description: Analyze any UI component, screen, or page from any framework (React Native, SwiftUI, Flutter, web, etc.) and produce a complete, detailed technical specification an agent can follow to reproduce the exact UX. Trigger this skill whenever the user asks you to analyze a UI, reverse-engineer a UI pattern, create a technical spec for a UI component, or figure out how some UI is built — even if they just say "how does this UI work" or "break down this component". Also trigger when they ask about installing/using libraries but actually need to understand a UI implementation. Do NOT trigger for pure backend or logic-only tasks.
---

# UI Architect

A skill for analyzing any user interface — from any framework, platform, or codebase — and producing comprehensive technical specifications that another agent can follow to recreate the exact user experience.

This skill was inspired by real-world research on chat UIs from libraries like `react-native-gifted-chat`, `stream-chat-react-native`, and `expo-ai`. The methodology generalizes to any UI.

## Core Philosophy

The goal is not to describe what the UI looks like (that's a designer's job). The goal is to document **how it works** — the architecture, component tree, scrolling mechanics, keyboard handling, animations, dependencies, and edge cases — so an agent implementing it has everything they need to match the production UX.

A good UI spec answers:
1. **What are the layers?** — Provider hierarchy, context, navigation
2. **How does it scroll?** — FlatList vs ScrollView, inverted or not, keyboard avoidance
3. **How does the input work?** — TextInput behavior, send flow, attachments, animations
4. **How does the header behave?** — What's in it, transparency, animations
5. **What are the dependencies?** — Every package and why
6. **What are the edge cases?** — Empty states, keyboard transitions, loading, errors
7. **What's the data model?** — Message types, user types, state shape

## How to Use This Skill

### Phase 1: Identify the Target

First, determine what the user wants analyzed. Ask clarifying questions if needed:

- **What is the UI?** (a library, a component, a screen, a pattern)
- **Where is it?** (GitHub URL, npm package, local path, just a description)
- **What framework?** (React Native, SwiftUI, Flutter, web, unknown)
- **What specific aspects?** (everything, or just the header, scrolling, input, etc.)
- **What's the output format?** (single markdown file, multi-file report, inline)

### Phase 2: Research (Fetcher Phase)

Gather information from all available sources. Use subagents for parallel research.

**For GitHub repos:**
- Read the README
- Read `package.json` / `pubspec.yaml` / `Podfile` / `build.gradle` (dependencies)
- Explore the source directory structure
- Read the main component files (look for the orchestrator)
- Read individual UI component files
- Look at example apps and tests for usage patterns

**For npm/PyPI/pub packages:**
- Fetch the npm page or package registry page
- Read documentation site if available
- Search for example usage patterns

**For source code files:**
- Read the code directly
- Trace the component hierarchy from top to bottom
- Look for keyboard handling, scroll listeners, animation code

**For documentation sites:**
- Fetch the docs
- Look for component API references
- Find installation guides and prop tables

### Phase 3: Analysis Dimensions

Analyze every aspect of the UI. Use these dimensions as a checklist.

#### 1. Architecture & Component Tree
- Full component hierarchy (parent to leaf)
- Provider/context wrapping order
- State management (local state, context, Redux, etc.)
- Navigation/routing structure
- Screen registration and deep linking

#### 2. Layout Structure (Top to Bottom)
```
┌─────────────────────────┐
│  HEADER / NAV BAR       │
├─────────────────────────┤
│  CONTENT AREA           │
│  ┌───────────────────┐  │
│  │ List/Scroll       │  │
│  │   - Item 1        │  │
│  │   - Item 2        │  │
│  └───────────────────┘  │
├─────────────────────────┤
│  INPUT TOOLBAR / CTA    │
└─────────────────────────┘
```

#### 3. Header / Navigation Bar
- How is it implemented? (stack navigator header, custom component, native nav)
- What content does it contain? (back button, title, actions, avatars)
- Is it transparent, blurred, solid? Any animation?
- How does it handle safe area insets?
- How does it behave when keyboard opens? (collapses, hides, stays)

#### 4. Scroll Behavior
- FlatList, ScrollView, ListView, LazyVStack, etc.
- Is it inverted? (newest at bottom vs top)
- Scroll-to-bottom: What triggers it? How is it implemented?
- Auto-scroll on content change: debounce/animation strategy
- Pagination: load more, infinite scroll implementation
- Scroll position preservation (for streaming/AI content)

#### 5. Keyboard Handling
- How does the view avoid the keyboard?
  - `KeyboardAvoidingView` / `KeyboardCompatibleView`
  - `useAnimatedKeyboard` + translate transform
  - Native `adjustResize` / `adjustPan`
  - `KeyboardController` / custom implementation
- What is the `keyboardVerticalOffset`? How is it calculated?
- `keyboardDismissMode` and `keyboardShouldPersistTaps` values
- Does the keyboard animate smoothly? (Reanimated or native driver)
- Android-specific handling (translucent status bar, IME padding)
- Does tapping outside/on messages dismiss the keyboard?

#### 6. Input Bar / Composer
- Position: absolute at bottom or part of layout?
- TextInput props: multiline, placeholder, returnKeyType, blurOnSubmit
- Send button: visibility conditions, animation, disabled state
- Attachments: file picker, image picker, camera
- Character limit, mentions, commands
- Auto-growing text input: min/max height, scroll behavior
- Placeholder text and styling

#### 7. Content / Message Rendering
- How is each item rendered? (flexbox layout, alignment left/right)
- Avatar rendering: position, visibility rules, fallback (initials)
- Content types: text, image, video, audio, file, link previews, custom cards
- Status indicators: sent/delivered/read/failed ticks
- Timestamps: format, position, localization
- Grouping: consecutive messages from same user
- Reactions, replies (threads), swipe-to-reply

#### 8. Animations & Transitions
- Typing indicator: dot animation details
- Reply preview: mount/unmount animation
- Send button: visibility fade
- Day separator: scroll-based fade
- Smooth scrolling: `scrollToEnd`, `scrollToIndex`
- Gesture-driven animations (swipe-to-reply, pull-to-refresh)

#### 9. Edge Cases & UX States
- Empty state (no messages)
- Loading state (initial load)
- Error state (send failure, network error)
- Keyboard opening while scrolling
- Rapid message sending / streaming content
- Offline support
- Accessibility (VoiceOver/TalkBack labels)

#### 10. Data Model
- Message interface: all fields and their types
- User interface
- State shape
- API response format (if applicable)
- Local storage / caching schema

#### 11. Dependencies
Every package with its purpose. Separate into:
- Core framework
- UI components (navigation, modals, bottom sheets)
- Network/API
- Animations
- Media (images, video, audio)
- Utilities (dates, i18n, IDs)
- Storage

### Phase 4: Write the Report

Structure the report using this template. The goal is **actionable detail** — an agent should be able to implement the UI from this document alone.

#### Report Template

```markdown
# [UI Name] - Technical Spec

**Analyzed from:** [source URL/path]  
**Framework:** [React Native / SwiftUI / Flutter / Web]  
**Version analyzed:** [version/commit]  

---

## 1. Architecture Overview

[Component hierarchy diagram using indentation or ASCII art]

## 2. Provider / Context Tree

[Wrapping order, what each provider does]

## 3. Screen Layout

```
┌─────────────────────────┐
│  HEADER                 │
├─────────────────────────┤
│                         │
│  CONTENT AREA           │
│                         │
├─────────────────────────┤
│  INPUT / FOOTER         │
└─────────────────────────┘
```

## 4. Header

[Full implementation details]

## 5. Scrolling

[All scroll mechanics]

## 6. Keyboard Handling

[How keyboard is avoided, offset values, platform differences]

## 7. Input Bar

[TextInput config, send button, attachments]

## 8. Content Rendering

[Item layout, avatars, bubbles, status, timestamps]

## 9. Animations

[Every animation with timing values and technology used]

## 10. Edge Cases

[Empty, loading, error, streaming, offline]

## 11. Data Model

[TypeScript interfaces or equivalent]

## 12. Dependencies

| Package | Version | Purpose |
|---|---|---|
| ... | ... | ... |

## 13. Key Implementation Notes

[Things that would be easy to miss: platform differences, gotchas, required configurations]
```

### Phase 5: Provide Implementation Guidance

After the report, include a section with actionable implementation guidance:

```markdown
## Implementation Steps

1. **Setup:** Install dependencies, configure babel/native modules
2. **Providers:** Wrap app in required providers
3. **Screen:** Create the screen with header configuration
4. **Content List:** Set up the list/scroll component
5. **Input Bar:** Create the input toolbar
6. **Message Items:** Implement item rendering
7. **Keyboard:** Configure keyboard avoidance
8. **Edge Cases:** Handle empty/loading/error states
9. **Polish:** Add animations, typing indicator, scroll-to-bottom
```

## Framework-Specific Guidance

### React Native / Expo
- Dependencies typically include: `react-native-reanimated`, `react-native-gesture-handler`, `react-native-safe-area-context`, `react-native-keyboard-controller`
- Use `useAnimatedKeyboard` for smooth keyboard tracking
- FlatList `inverted` for chat
- `react-native-keyboard-controller` > `KeyboardAvoidingView` for modern apps
- Always check: `keyboardVerticalOffset`, `keyboardShouldPersistTaps`, `keyboardDismissMode`

### Flutter
- Use `ListView.builder` with `reverse: true` for chat
- `TextField` with `maxLines` for auto-growing input
- `MediaQuery.of(context).viewInsets.bottom` for keyboard height
- `Dismissible` for swipe-to-reply
- `AnimatedList` for smooth message insertions

### SwiftUI / UIKit
- `UITableView` with inverted or `scrollToRow(at: .bottom)` for chat
- `UIResponder.keyboardWillShowNotification` for keyboard tracking
- `inputAccessoryView` for keyboard-attached toolbar (iOS)
- `List` or `ScrollView` with `ScrollViewReader` for scroll-to-bottom

### Web (React)
- `overflow-y: auto` container with flexbox column-reverse or scroll-to-bottom
- `contentEditable` or textarea for input
- `IntersectionObserver` for load-more pagination
- `scrollIntoView({ behavior: 'smooth' })` for auto-scroll

## Key Principles for Writing Good Specs

1. **Be specific, not generic.** Don't say "the header has a title" — say "the header uses a transparent navigation bar with a blurred background (systemChromeMaterial), left gear icon linking to /settings, and a right new-chat button visible only when messages exist."
2. **Explain the why.** "The keyboard offset equals `insets.top + headerHeight` because the KeyboardAvoidingView needs to know the distance from screen top to the chat container."
3. **Note platform differences.** "On iOS, uses `useHeaderHeight()` from react-navigation. On Android, keyboardVerticalOffset is not needed because `adjustResize` handles it natively."
4. **Include dependencies with versions.** Not just "react-native-reanimated" but "react-native-reanimated ~4.1.1 (peer dep, requires babel plugin)"
5. **Show key code patterns.** Not the full file, but the critical 5-10 lines that show how something works.
6. **Document the data model completely.** Every field, its type, and whether it's optional.

## Examples & Reference

The `references/` directory contains full example reports. Read them before starting to understand the expected depth and format:

- `references/chat-ui-expo-ai.md` — Expo Router server-component-based AI chat
- `references/chat-ui-gifted-chat.md` — react-native-gifted-chat library
- `references/chat-ui-stream-chat.md` — Stream Chat React Native SDK

These show the level of detail and structure expected from this skill. Your reports should match this standard.

## Folder Structure for Output

Save reports in a structured directory:

```
ui-research/
├── 01-[ui-name].md            # Main report
└── references/                 # (optional) Supporting files
    └── ...
```

Name the file descriptively: `01-expo-ai-chat.md`, `02-swiftui-message-list.md`, `03-flutter-chat-input.md`, etc.
