# Expo AI - Chat UI Research Report

**Repo:** https://github.com/EvanBacon/expo-ai  
**Stack:** Expo Router 6 + React 19.1 + React Native 0.81 + RSC + AI SDK (Vercel) + Tailwind + Reanimated  
**Type:** AI chat app (not a reusable library)

---

## 1. Architecture Overview

```
app/index.tsx
  -> actions/render-root.tsx (React Server Function)
    -> <AI> provider (ai/rsc createAI)
      -> <ChatUI>
        -> <ChatContainer>
        -> Stack.Screen (header options)
        -> <MessagesScrollView>
          -> <KeyboardFriendlyScrollView>
            -> message list (user-message, assistant-message, rich cards)
        -> <ChatToolbar>
          -> <ChatToolbarInner>
            -> <FirstSuggestions> (empty state prompt chips)
            -> <TextInput> + <SendButton>
```

---

## 2. Header Implementation

### Root Layout (`app/_layout.tsx`)
- Uses custom `<Stack>` navigator wrapping `@react-navigation/native-stack`
- Default iOS header: `headerTransparent: true`, `headerBlurEffect: "systemChromeMaterial"`
- Left: gear icon (`TouchableBounce` with haptics) -> settings route
- Right: "new chat" button (`square.and.pencil` icon) conditionally shown via `Stack.Screen` `options.headerRight`

### Key Code Pattern
```tsx
<Stack.Screen
  name="index"
  options={{
    headerLargeStyle: { backgroundColor: AC.systemGroupedBackground },
    headerTransparent: false,
    headerLeft: () => (
      <Link href="/settings" asChild>
        <TouchableBounce sensory>
          <IconSymbol name="gear" color={AC.label} />
        </TouchableBounce>
      </Link>
    ),
  }}
/>
```

### HeaderButton Component
- Wraps `PlatformPressable` from `@react-navigation/elements`
- hitSlop: 16px on non-iOS (for larger touch targets)

---

## 3. Scroll View & Keyboard Handling

### KeyboardFriendlyScrollView
Uses `react-native-reanimated`'s `useAnimatedKeyboard` hook:

```tsx
const keyboard = useAnimatedKeyboard();
// keyboard.state.value - OPEN | CLOSING | OPENING | CLOSED
// keyboard.height.value - current keyboard height
```

### Scroll-on-Keyboard Logic
- **Keyboard opens without drag**: auto-scroll to `MAX_SAFE_INTEGER` (bottom)
- **Keyboard opens with user drag**: respects `isScrollViewControlled`
- Uses `useDerivedValue` for UI-thread scroll adjustments

### Auto-scroll on New Messages
- `onContentSizeChange` triggers `scrollToEnd({ animated: true })` with **15ms debounce**
- Guards: skips if keyboard mid-transition or native is controlling scroll

### Keyboard Blur Underlay
- Animated spacer view matching keyboard height
- Ensures last message remains visible above keyboard

### ScrollView Props
```tsx
<KeyboardFriendlyScrollView
  keyboardDismissMode="interactive"
  keyboardShouldPersistTaps="handled"
  contentInsetAdjustmentBehavior="automatic"
  showsVerticalScrollIndicator={false}
  contentContainerStyle={{
    paddingTop: top + HEADER_HEIGHT + 24,
    paddingBottom: textInputHeight,
    gap: 16,
  }}
>
```

---

## 4. Input Toolbar / Composer

### Position & Keyboard Tracking
```tsx
<Animated.View style={[
  { position: "absolute", bottom: 0, left: 0, right: 0 },
  useAnimatedStyle(() => ({
    transform: [{ translateY: -keyboard.height.value }]
  }))
]}>
```

### Blur Background
- `expo-blur` with system chrome material (light/dark adaptive)
- Animated paddingBottom for smooth transition

### TextInput
- Pill shape (`borderRadius: 999`)
- `returnKeyType="send"`, `blurOnSubmit={false}`
- `keyboardAppearance` follows theme
- `outline: "none"` for web

### Send Button
- Circular (borderRadius: 999, aspectRatio: 1)
- `arrow.up` SF Symbol
- 50% opacity when disabled
- Haptic feedback on iOS (`Haptics.impactAsync(.Medium)`)

### Submit Flow
```
1. Haptic feedback
2. Clear input immediately
3. Optimistically add <UserMessage> to UI state
4. Call onSubmit server action (streams AI response)
5. Append AI response message on resolution
```

### Empty State (FirstSuggestions)
- Suggestion chips: "What's the weather", "Things to do around me", "Trending movies"
- Asymmetric chat bubble style (`borderRadius: 16, borderBottomLeftRadius: 4`)
- FadeInDown stagger animation (3-index * 100ms delay)
- On press: adds UserMessage, calls onSubmit

---

## 5. Message Rendering

### UI State Model
```typescript
type UIState = { id: string; display: React.ReactNode }[];
```

Each message `display` is a streamed React node from the server:
- **User messages**: `<UserMessage>` text component
- **AI text**: `<MarkdownText>` using `react-native-markdown-display`
- **Weather**: `<WeatherCard>` with gradient, hourly forecast
- **Movies**: `<MoviesCard>` with horizontal posters, circular ratings
- **Maps**: `<MapCard>` with native maps (Apple/Google) or MapKit JS on web

No FlatList - uses a plain `ScrollView` with React nodes. Each message is a distinct React component streamed from the server side.

---

## 6. Dependencies

| Package | Purpose |
|---|---|
| `expo-router` ~6.0.17 | File-based routing, RSC |
| `react` / `react-dom` 19.1.0 | React 19 (RSC support) |
| `react-native` 0.81.5 | RN core |
| `react-native-web` ^0.21.0 | Web rendering |
| `ai` ^3.4.33 + `@ai-sdk/openai` | Vercel AI SDK |
| `react-native-reanimated` ~4.1.1 | Animations, keyboard tracking |
| `react-native-safe-area-context` ~5.6.0 | Safe area insets |
| `react-native-gesture-handler` ~2.28.0 | Gesture support |
| `expo-blur` ~15.0.8 | Blur view for toolbar |
| `expo-haptics` ~15.0.8 | Haptic feedback |
| `expo-symbols` ~1.0.8 | SF Symbols |
| `@bacons/apple-colors` ^0.0.8 | Apple system colors |
| `react-native-markdown-display` ^7.0.2 | Markdown rendering |
| `zod` ^3.24.1 | AI tool param validation |
| `react-native-maps` / `mapkit-react` | Map rendering |

---

## 7. Key UX Patterns

### Platform Adaptivity
- `process.env.EXPO_OS` checks throughout codebase
- Platform file convention (`.tsx` vs `.web.tsx` vs `.native.tsx`)
- Tailwind only on web (`tw` utility returns `null` on native)
- Maps: `react-native-maps` native vs `mapkit-react` web

### TouchableBounce
- iOS: native `TouchableBounce` from RN
- Web: `TouchableOpacity` fallback
- `sensory` prop triggers haptic feedback

### Icon System
- iOS: `expo-symbols` (SF Symbols)
- Others: `@expo/vector-icons/MaterialIcons` mapping

### Apple Colors
- `@bacons/apple-colors` provides system colors (`AC.label`, `AC.separator`, `AC.systemBackground`, etc.)
- Maps to native iOS P3 colors, Material equivalents on Android, CSS vars on web

---

## 8. Unique Architecture Notes

- **React Server Components**: Chat UI is rendered on the server and streamed down as React nodes
- **No FlatList**: Uses plain ScrollView because messages are streamed React nodes, not FlatList items
- **Absolute Positioning**: Toolbar is `position: absolute` at bottom, translated by keyboard height
- No navigation header in the traditional sense -- uses Expo Router's `Stack.Screen` options
- Not a reusable component library; designed for this specific AI chat use case
