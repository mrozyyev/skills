# React Native Gifted Chat - UI Research Report

**Repo:** https://github.com/FaridSafi/react-native-gifted-chat  
**npm:** `react-native-gifted-chat`  
**Version:** 3.3.3  
**License:** MIT  
**Stars:** 14.4k

---

## 1. Architecture & Provider Hierarchy

```
GestureHandlerRootView
  -> SafeAreaProvider
    -> KeyboardProvider (react-native-keyboard-controller)
      -> GiftedChatContext.Provider
        -> ActionSheetProvider
          -> View (onLayout -> initialized)
            -> KeyboardAvoidingView
              -> MessagesContainer (AnimatedFlatList)
              -> InputToolbar
```

---

## 2. Component Hierarchy

```
GiftedChat
  └── MessagesContainer (AnimatedFlatList, inverted)
       ├── ListHeaderComponent (visual footer: typing indicator)
       ├── ListFooterComponent (visual header: load earlier)
       ├── CellRendererComponent (tracks day positions)
       │    └── Item per message
       │         ├── DayWrapper or AnimatedDayWrapper
       │         └── Message
       │              ├── ReanimatedSwipeable (swipe-to-reply)
       │              └── View
       │                   ├── Avatar (left)
       │                   ├── Bubble
       │                   │    ├── MessageReply (in-bubble reply)
       │                   │    ├── MessageImage / Video / Audio
       │                   │    ├── MessageText
       │                   │    ├── renderCustomView
       │                   │    └── bottomContainer (username + time + ticks)
       │                   └── Avatar (right)
       └── ScrollToBottomButton (FAB)
       └── DayAnimated (floating day header)
  └── InputToolbar
       ├── ReplyPreview (if reply active)
       ├── Actions (left side)
       ├── Composer (TextInput, flex: 1)
       └── Send (right side)
       └── Accessory (below, optional)
```

---

## 3. Header

- **No built-in header component** - the library is a self-contained chat UI
- Navigation header is expected to be provided by the consumer (React Navigation, etc.)
- `keyboardAvoidingViewProps={{ keyboardVerticalOffset: headerHeight }}` is the bridge between the consumer's header and the chat
- `useHeaderHeight()` from `@react-navigation/elements` returns `status bar + navigation header height`

```tsx
const headerHeight = useHeaderHeight();
<GiftedChat
  keyboardAvoidingViewProps={{ keyboardVerticalOffset: headerHeight }}
/>
```

---

## 4. Keyboard Avoidance (react-native-keyboard-controller)

### Provider Config
```tsx
<KeyboardProvider
  statusBarTranslucent={true}       // Android edge-to-edge
  navigationBarTranslucent={true}   // Android edge-to-edge
  {...keyboardProviderProps}
>
```

### KeyboardAvoidingView
```tsx
<KeyboardAvoidingView
  behavior='translate-with-padding'
  keyboardVerticalOffset={insets.top} // default = status bar height
  {...props.keyboardAvoidingViewProps}
>
```

- `behavior='translate-with-padding'` - native modal-style translation on iOS, padding on Android
- `keyboardVerticalOffset` defaults to `insets.top`. Set to nav header height for correct positioning
- Android: `statusBarTranslucent` and `navigationBarTranslucent` default `true`

### FlatList Keyboard Props
```tsx
keyboardDismissMode='interactive'     // smooth dismiss on swipe
keyboardShouldPersistTaps='handled'   // taps handled through keyboard
```

---

## 5. FlatList & Inverted Rendering

### Animated FlatList
```tsx
const RNGHAnimatedFlatList = Animated.createAnimatedComponent(FlatList);
```

- Uses `react-native-gesture-handler`'s FlatList wrapped with Reanimated
- `inverted={true}` (default): newest messages at bottom
- HeaderComponent -> visual footer (typing indicator)
- FooterComponent -> visual header (load earlier messages)

### Scroll Handling
- `useAnimatedScrollHandler` runs on UI thread via Reanimated worklet
- `runOnJS(handleOnScroll)(event)` bridges to JS thread
- `scrollEventThrottle={1}`

### Key FlatList Props
```tsx
automaticallyAdjustContentInsets={false}
scrollEventThrottle={1}
keyboardDismissMode='interactive'
keyboardShouldPersistTaps='handled'
onEndReached={onEndReached}
onEndReachedThreshold={0.1}
inverted={isInverted}
```

---

## 6. Input Toolbar / Composer

### InputToolbar Layout
```tsx
<View style={container}>  // borderTopWidth, dark mode support
  <ReplyPreview />        // if replyMessage exists
  <View style={{ flexDirection: 'row', alignItems: 'flex-end' }}>
    <Actions />           // left side action button
    <Composer />          // TextInput (flex: 1)
    <Send />              // send button
  </View>
  <Accessory />           // optional second line
</View>
```

### Composer (TextInput)
- From `react-native-gesture-handler` (not RN core)
- `multiline` enabled for auto-growing
- Placeholder: "Type a message..."
- Web: `onContentSizeChange` + manual height calc
- Styling: `fontSize: 16, lineHeight: 22, padding: 8`

### Send Button
- Animated opacity (`withTiming`, 200ms)
- Visible when: `isSendButtonAlwaysVisible || !!text.trim().length`
- Hidden state: `pointerEvents: 'none'`
- `isTextOptional` allows sending without text (for media)
- Custom `TouchableOpacity` using RNGH `BaseButton` + Reanimated opacity

### Actions Button
- Left side of input toolbar
- Triggers `onPressActionButton` or default action sheet
- Can render custom via `renderActions`

---

## 7. Message Bubbles

### Bubble Layout
```
View (containerStyle[position])
  ├── renderCustomView (if !isCustomViewBottom)
  ├── MessageReply (in-bubble reply, if present)
  ├── MessageImage
  ├── MessageVideo
  ├── MessageAudio
  ├── MessageText
  ├── renderCustomView (if isCustomViewBottom)
  └── View (bottomContainer)
       ├── renderUsername
       └── Time + Ticks (sent/received/pending)
```

### Styling Strategy
- **Position-based**: `getStyleWithPosition(styles, 'wrapper', position)` returns `wrapper` + `wrapper_left` or `wrapper_right`
- **Consecutive messages**: rounded corners adjust for same-user consecutive messages
- Default colors: left `#f0f0f0`, right `#0084ff`

### Message Text & Link Parser
- Parses URLs, emails, phone, hashtags, mentions
- Custom matchers supported via `messageTextProps.matchers`
- Overlap removal for links sharing index ranges
- `stripPrefix` removes `http://`/`https://` from display

### Status Ticks
- `sent` -> checkmark, `received` -> double check, `pending` -> clock
- Only for current user's messages

---

## 8. Avatars

- **Visibility**: `isUserAvatarVisible` (default false, only other users)
- **Grouping**: `isAvatarVisibleForEveryMessage` (default false - shows avatar only on last in group)
- **Position**: `isAvatarOnTop` - renders at top vs bottom of bubble
- **GiftedAvatar**: handles URL string, number (require), or render function
- **Fallback**: initials derived from `user.name` (up to 2 chars)
- **Background color**: deterministic from 7-color palette based on name char codes

---

## 9. Swipe-to-Reply

- Uses `ReanimatedSwipeable` from RNGH
- Direction: `'left'` (default) or `'right'`
- Custom action renderer via `swipe.renderAction`
- Default: blue circle with reply arrow icon (CSS border-based)
- Opens on swipe, auto-closes after activation
- Reply preview appears in InputToolbar with animated mount/unmount (200ms bezier easing)

### Reply Preview Animation
- `withTiming(1)` on mount (200ms bezier)
- `withTiming(0)` on clear, then `runOnJS(onClearReply)`
- Interpolates: height (0 -> contentHeight), opacity (0 -> 1), translateY (10 -> 0)

### Reply Preview Layout
```
Animated.View (wrapper)
  └── View (container)
       ├── View (blue left border indicator)
       └── View (content)
            ├── Image (if reply has image)
            ├── Text ("Replying to {name}")
            └── Text (reply text, 2 lines max)
       └── Pressable (X clear button)
```

---

## 10. Scroll-to-Bottom Button

- Floating Pressable: `absolute`, `right: 10`, `bottom: 30`, `zIndex: 999`
- 40x40 circle with shadow
- Visibility: throttled via `useCallbackThrottled` (50ms)
- Offset threshold: `scrollToBottomOffset` (default 200)
- Content: default "V" character, customizable via `scrollToBottomComponent`

---

## 11. Typing Indicator

- 3 animated dots using Reanimated `withRepeat(withSequence(withTiming(topY), withTiming(bottomY)), 0, true)`
- Dot 1: no delay, Dot 2: 100ms, Dot 3: 200ms stagger
- 500ms per cycle
- Container: slide-in animation (250ms, y 200->0)
- Controlled by `isTyping` prop
- Override via `renderTypingIndicator` or `renderFooter`

---

## 12. Day Separators

### Static Day
- Shows date between messages from different days
- Uses `dayjs` with `relativeTime` and `calendar` plugins
- Format: "Today" / "D MMMM" / "D MMMM YYYY" (different year)

### Animated Day (floating)
- Rendered outside FlatList, positioned absolute
- Fades in on scroll, fades out after 500ms idle
- Uses `useAnimatedReaction` + `daysPositions` shared value
- `useRelativeScrolledPositionToBottomOfDay` for positioning

---

## 13. Load Earlier Messages

- Button visible when `loadEarlierMessagesProps.isAvailable` = true
- `isInfiniteScrollEnabled` auto-triggers when reaching top
- Customizable via `renderLoadEarlier`

---

## 14. Data Model (Message Interface)

```typescript
interface IMessage {
  _id: string | number
  text: string
  createdAt: Date | number
  user: User
  image?: string
  video?: string
  audio?: string
  system?: boolean
  sent?: boolean
  received?: boolean
  pending?: boolean
  quickReplies?: QuickReplies
  replyMessage?: ReplyMessage
  location?: { latitude: number; longitude: number }
}

interface User {
  _id: string | number
  name?: string
  avatar?: string | number | (() => React.ReactNode)
}
```

---

## 15. Dependencies

### Runtime
| Package | Purpose |
|---|---|
| `@expo/react-native-action-sheet` ^4.1.1 | Native action sheet |
| `dayjs` ^1.11.19 | Lightweight dates/i18n |
| `lodash.isequal` ^4.5.0 | Deep equality |
| `react-native-zoom-reanimated` ^1.5.2 | Image pinch-to-zoom |

### Peer Dependencies
| Package | Min Version | Purpose |
|---|---|---|
| `react` | >=18.0.0 | Core |
| `react-native` | * | Core |
| `react-native-gesture-handler` | >=2.0.0 | Gestures, swipeable, FlatList |
| `react-native-keyboard-controller` | >=1.0.0 | Keyboard avoidance |
| `react-native-reanimated` | >=3.0.0 or ^4.0.0 | All animations |
| `react-native-safe-area-context` | >=5.0.0 | Safe area insets |

---

## 16. Animation Strategy Summary

| Feature | Technology | Details |
|---|---|---|
| Send button visibility | Reanimated `withTiming` | 200ms opacity |
| Typing indicator dots | `withRepeat/withSequence/withTiming` | 500ms cycle, 100ms stagger |
| Typing container | Reanimated `withTiming` | 250ms slide in/out |
| Reply preview mount | Reanimated `interpolate` + `withTiming` | 200ms bezier easing |
| Scroll-to-bottom visibility | Reanimated `withTiming` | 250ms opacity |
| Day animated fade | Reanimated `withTiming` | 500ms fade, 500ms delay |
| Touchable press | Reanimated `withTiming` | 150ms to active, 150ms back |
| Swipe-to-reply | RNGH `ReanimatedSwipeable` | Native gesture, worklet animations |
| Scroll handling | Reanimated `useAnimatedScrollHandler` | UI thread |

---

## 17. Key Architecture Patterns

1. **Provider Hierarchy**: GestureHandlerRootView > SafeAreaProvider > KeyboardProvider > GiftedChatContext > ActionSheetProvider
2. **Render Prop System**: Every UI element has a `render*` prop with default fallback
3. **Controlled/Uncontrolled**: `text` and `reply.message` can be externally controlled or internal
4. **Generic Typing**: `<TMessage extends IMessage>` for custom message types
5. **Memoization**: Heavy `useMemo`, `useCallback`, `useDerivedValue` usage
6. **Thread Safety**: Reanimated worklets for UI thread, `runOnJS` bridge for JS state
7. **Init Delay**: Shows loading until first `onLayout` fires (container height > 0)

---

## 18. Installation

```bash
# Expo
npx expo install react-native-gifted-chat react-native-reanimated react-native-gesture-handler react-native-safe-area-context react-native-keyboard-controller

# Bare RN
yarn add react-native-gifted-chat react-native-reanimated react-native-gesture-handler react-native-safe-area-context react-native-keyboard-controller
```

Requires `react-native-reanimated` babel plugin in `babel.config.js`.
