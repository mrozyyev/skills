# UI Analysis Methodology

This reference documents the 11-dimension analysis framework used by UI Architect. Each dimension represents a category of questions you must answer for any UI you analyze.

---

## The 11 Dimensions

### 1. Architecture & Component Tree
Trace the full component hierarchy from top-level providers down to leaf components. Document:
- Every wrapper/provider and what it contributes
- The rendering order (which component contains which)
- State management approach (Context, Redux, Jotai, local state)
- Navigation/routing structure
- Screen registration and deep linking setup

### 2. Layout Structure
Draw an ASCII diagram showing the three main zones:
- Header/Nav Bar
- Content Area (scrollable list, grid, etc.)
- Input Toolbar / Footer / CTA

### 3. Header
Headers come in many forms. Determine:
- Is it the platform's native navigation bar or a custom component?
- What's in it (back button, title, actions, avatars, search)?
- Visual treatment (transparent, blurred, solid color, gradient)?
- Safe area handling (insets.top usage)?
- Behavior during keyboard show (collapse, hide, or stay)?
- Any animations (large title collapse, scroll-based transparency)?

### 4. Scroll Behavior
The most critical dimension for list-based UIs:
- **Component**: FlatList, ScrollView, ListView, UICollectionView, LazyVStack, etc.
- **Inverted**: Is the list inverted (new content at bottom)? If so, how is inversion handled?
- **Auto-scroll**: When new content arrives, does it auto-scroll? With what animation? Any debounce?
- **Scroll-to-bottom**: Is there a button? What triggers its visibility? Offset threshold?
- **Pagination**: Load more on scroll to top? Infinite scroll? What's the threshold?
- **Position preservation**: For streaming content (AI chat), does it maintain scroll position if user is reading history?
- **Scroll event handling**: Any listeners on scroll events? What for?

### 5. Keyboard Handling
Decode how the UI avoids keyboard overlap:
- **Method**: KeyboardAvoidingView, useAnimatedKeyboard, KeyboardController, native adjustResize/adjustPan, custom
- **Offset**: keyboardVerticalOffset — what value and how calculated (status bar + header height)?
- **Dismiss modes**: keyboardDismissMode (interactive, on-drag, none), keyboardShouldPersistTaps (always, handled, never)
- **Platform differences**: iOS vs Android behavior
- **Animation**: Is the keyboard follow smooth? Is it on the native thread (Reanimated) or JS thread?
- **Edge-to-edge**: Android status bar/nav bar translucent configuration
- **Dismiss triggers**: Does tapping messages, scrolling, or tapping outside dismiss the keyboard?

### 6. Input Bar / Composer
The interactive element at the bottom:
- **Positioning**: Absolute (pinned to bottom, translated by keyboard) or relative (part of flex layout)?
- **TextInput**: multiline? placeholder? returnKeyType? blurOnSubmit? keyboardAppearance?
- **Auto-grow**: minHeight/maxHeight? How is height calculated (onContentSizeChange)?
- **Send button**: When visible (always or only when text present)? Disabled state styling? Animation? Icon vs text?
- **Attachments**: Any attach button? What pickers (image, file, camera)? Upload progress?
- **Other features**: Mentions (@), commands (/), emoji picker, quick replies, suggestions
- **Submit flow**: What happens on send? (clear input, optimistic update, API call, haptic feedback)
- **Edge cases**: Send without text (for media), rapid sending, character limit

### 7. Content / Item Rendering
How individual items are displayed:
- **Layout**: Flex direction, alignment (left/right based on sender), padding, margins
- **Avatars**: Position (left, right, both)? Visibility rules (own messages, grouped messages)? Fallback (initials, default icon)? Size and shape?
- **Bubble styling**: Background color (per sender), border radius, shadows, consecutive message corner treatment
- **Text rendering**: Link detection (URLs, emails, phones, hashtags, mentions), markdown support, custom link handlers
- **Media**: Image handling (gallery grid, tap to fullscreen), video playback, audio player, file attachments
- **Status indicators**: Sent/delivered/read/failed ticks — position and style
- **Timestamps**: Format (dayjs, DateFormat), position (inside bubble, below), localization
- **Grouping**: Are consecutive messages from same user grouped? How is the boundary determined? How do styles change? (e.g., no avatar, rounded corners adjust)
- **Reactions**: Emoji reactions — position (top/bottom of bubble), style (clustered, inline), add/remove interaction
- **Replies/Threads**: In-bubble reply display, thread reply count, navigation to thread
- **Swipe actions**: Swipe-to-reply, swipe-to-delete — direction, animation, action widget

### 8. Animations & Transitions
Every animated interaction in the UI:
- **Typing indicator**: Dot animation (bounce, fade, scale), stagger delay, container slide-in/out
- **Reply preview**: Mount/unmount animation (expand from 0 height, fade in)
- **Send button**: Fade in/out based on text presence
- **Day separators**: Scroll-based fade in/out, position tracking
- **Scroll-to-bottom button**: Fade in when scrolled up, fade out at bottom
- **Message insertions**: Animated list items or instant appearance?
- **Gesture animations**: Swipe-to-reply follow gesture, pull-to-refresh
- **Technology used**: Reanimated (withTiming, withSpring, withSequence, withRepeat), native animations (UIView.animate, Animation.spring), CSS transitions

### 9. Edge Cases & UX States
States beyond the happy path:
- **Empty state**: What's shown when there are no items? (illustration, text, suggestions, prompt)
- **Loading state**: Initial load spinner, skeleton, shimmer
- **Error state**: Send failure (retry UI), network error (banner), permission denied
- **Streaming**: For AI/incremental content — how does partial content render? Cursor animation?
- **Offline**: Does it show offline indicator? Queue messages for later?
- **Keyboard during scrolling**: What happens if keyboard is open and user scrolls?
- **Rapid interactions**: Debouncing repeated sends, handling rapid typing
- **Accessibility**: VoiceOver/TalkBack labels, roles, keyboard navigation support

### 10. Data Model
The shape of the data driving the UI:
- **Message type**: All fields (_id, text, createdAt, user, image, video, audio, system flags, status flags, reactions, replies, etc.)
- **User type**: _id, name, avatar (string URL, number asset, or function)
- **State shape**: How messages are stored (array, map, normalized), how state updates work
- **API contracts**: Request/response format if backed by an API
- **Local storage**: Any caching, offline queue, draft persistence

### 11. Dependencies
Full dependency table with versions and purpose:

| Package | Version | Category | Purpose |
|---|---|---|---|
| react-native | 0.x.x | Core | Framework |
| ... | ... | UI | ... |
| ... | ... | Animation | ... |
| ... | ... | Network | ... |
| ... | ... | Media | ... |
| ... | ... | Utility | ... |

Categories: Core, UI/Navigation, Animation, Network/API, Media, Storage, Utility, Dev/Build

---

## Research Sources

When researching a UI, consult these sources in order of importance:

1. **Source code** — The most reliable source. Read the actual implementation files.
2. **README / Documentation** — Intent and API surface, but may not match reality.
3. **package.json / Podfile / build.gradle** — Exact dependencies and versions.
4. **Examples / Tests** — Shows real usage patterns and common configurations.
5. **Issues / PRs** — Known problems, workarounds, and design decisions.
6. **Official docs** — For libraries, the API reference is authoritative for props and behavior.

## Verification

Before finalizing a report, verify:
- Can you trace the full rendering path from app entry point to leaf component?
- Is every dependency accounted for with its purpose?
- Are platform differences (iOS, Android, Web) noted?
- Are edge cases (empty, loading, error, streaming) covered?
- Would an agent with this report be able to reproduce the exact UX without looking at the original source?
