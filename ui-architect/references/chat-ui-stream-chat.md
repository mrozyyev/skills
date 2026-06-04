# Stream Chat React Native - UI Research Report

**Repo:** https://github.com/GetStream/stream-chat-react-native  
**npm:** `stream-chat-react-native` (RN CLI) / `stream-chat-expo` (Expo)  
**Version:** v9.3.0  
**License:** Proprietary (SEE LICENSE)  
**Stars:** 1.2k

---

## 1. Architecture & Provider Hierarchy

```
GestureHandlerRootView (required)
  OverlayProvider (ImageGallery, Theme, Translation)
    Chat (WebSocket connection, ChatContext, ThemeContext, TranslationContext)
      WithComponents (optional custom component overrides)
        Channel (9+ contexts: Channel, Keyboard, Messages, MessageInput, etc.)
          KeyboardCompatibleView (built-in keyboard handling)
            ChannelHeader (custom, built by consumer)
            MessageList (FlatList-based, inverted)
            MessageComposer (input bar)
```

---

## 2. Component Tree (Full Detail)

```
OverlayProvider
  Chat
    Channel
      KeyboardCompatibleView
        ChannelHeader (custom consumer implementation)
        MessageList (FlatList, inverted)
          ├── FooterComponent (visual top -> LoadEarlier indicator)
          ├── HeaderComponent (visual bottom -> loadRecent indicator)
          ├── MessageItemView (per message)
          │    ├── MessageAuthor (avatar)
          │    ├── swipable wrapper (swipe-to-reply)
          │    ├── MessageContent (the bubble)
          │    │    ├── MessagePinnedHeader
          │    │    ├── MessageHeader
          │    │    ├── ReactionList (top/bottom/clustered)
          │    │    ├── Gallery / FileAttachmentGroup / Giphy / URLPreview / Audio
          │    │    ├── MessageTextContainer
          │    │    └── MessageFooter
          │    ├── MessageReplies (thread count + avatars)
          │    ├── MessageStatus (timestamp + read receipts)
          │    └── MessageSpacer
          ├── TypingIndicator (footer, non-inverted)
          └── ScrollToBottomButton (floating FAB)
        MessageComposer
          ├── MessageInputHeaderView (reply/edit preview)
          ├── InputButtons (AttachButton + CommandsButton)
          ├── AutoCompleteSuggestionList (mentions/commands/emojis)
          ├── LinkPreviewList
          ├── AttachmentUploadPreviewList
          ├── AudioRecorder
          ├── OutputButtons (CooldownTimer, EditButton, SendButton)
          └── StopMessageStreamingButton (AI)
```

---

## 3. Header (ChannelHeader)

- **No built-in header component** - consumer is expected to build one
- SDK provides hooks for building custom headers:
  - `useChannelPreviewDisplayName` - channel display name
  - `useChannelPreviewDisplayPresence` - online presence
  - `useChannelPreviewData` - preview data (latest message)
  - `useChannelMembersState` - member state
  - `useChannelOnlineMemberCount` - online member count

### Typical Custom Header Pattern
```tsx
const ChannelHeader = ({ onBack }) => {
  const displayName = useChannelPreviewDisplayName();
  const isOnline = useChannelPreviewDisplayPresence();
  return (
    <View>
      <TouchableOpacity onPress={onBack}>
        <BackIcon />
      </TouchableOpacity>
      <ChannelAvatar channel={channel} />
      <View>
        <Text>{displayName}</Text>
        <Text>{isOnline ? 'Online' : 'Offline'}</Text>
      </View>
    </View>
  );
};
```

---

## 4. Keyboard Handling (KeyboardCompatibleView)

### Behavior
- Built into `Channel` component - wraps children automatically
- Listens to `keyboardWillShow`/`keyboardWillHide` (iOS) and `keyboardDidShow`/`keyboardDidHide` (Android)
- Adjusts channel container height to keep MessageComposer above keyboard
- Provides `KeyboardContext` with keyboard state

### Configuration via Channel Props
```tsx
<Channel
  keyboardVerticalOffset={headerHeight}  // nav header height
  keyboardBehavior='padding'             // 'height' | 'position' | 'padding'
  disableKeyboardCompatibleView={false}  // true = handle yourself
  additionalKeyboardAvoidingViewProps={{}}
  dismissKeyboardOnMessageTouch={true}   // default true
  bottomInset={0}                        // for attachment picker
  topInset={0}                           // for attachment picker sizing
>
```

### v9 Improvements
- No need for negative offsets (`keyboardVerticalOffset={-300}`) on Android
- Set `keyboardVerticalOffset` to actual header height on both platforms
- No wrapping MessageComposer in extra SafeAreaView
- Pair `keyboardVerticalOffset` with `topInset` for attachment picker

### Custom Override
```tsx
<Channel KeyboardCompatibleView={CustomKeyboardCompatibleView}>
```

---

## 5. MessageList

### FlatList Configuration
- `inverted={true}` (default): newest at bottom
- HeaderComponent at visual bottom (recent loading)
- FooterComponent at visual top (older loading)

### Key Props
```tsx
<MessageList
  inverted={true}
  additionalFlatListProps={{}}
  setFlatListRef={fn}
  onListScroll={fn}
  onThreadSelect={fn}
  threadList={false}
  noGroupByUser={false}
  isListActive={true}
  isLiveStreaming={false}
/>
```

### Pagination
- `PaginatedMessageListContext` manages pagination state
- `FooterComponent` -> `InlineLoadingMoreIndicator` (loading older)
- `HeaderComponent` -> `InlineLoadingMoreRecentIndicator` (loading recent)
- `loadingMore` / `loadingMoreRecent` flags

### ScrollToBottomButton
- Floating FAB, appears when scrolled from latest
- Props: `onPress`, `showNotification`, `unreadCount`
- Override via `WithComponents overrides={{ ScrollToBottomButton: Custom }}`

---

## 6. MessageComposer (Input Bar)

### Full Layout (Left to Right)
```
[LeadingView] [InputButtons: Attach + Commands] [InputHeaderView: reply/edit preview]
[AutoCompleteInput] [TrailingView] [LinkPreviewList] [AttachmentUploadPreviewList]
[AudioRecorder] [ComposerTrailingView] [OutputButtons: Cooldown/Edit/Send]
[StopStreamingButton] [ThreadCheckbox]
```

### CommandsButton
- Toggles autocomplete for `/` commands
- Controlled by `hasCommands` prop on Channel

### AutoCompleteInput
- Handles `@` mentions, `:` emoji, `/` commands
- `AutoCompleteSuggestionList` with suggestion items

### AttachButton
- Opens `AttachmentPicker` bottom sheet
- Controlled by `hasImagePicker`, `hasFilePicker`, `hasCameraPicker`

### SendButton / EditButton
- `SendButton` triggers `sendMessage()`
- `EditButton` shown when editing
- `CooldownTimer` during message cooldown

### Attachment Upload Preview
- `AttachmentUploadPreviewList` shows pending uploads
- `AttachmentRemoveControl` (X button)
- `AttachmentUploadProgressIndicator`

### Audio Recording
- `AudioRecordingButton` (long-press mic)
- `AudioRecordingInProgress` (waveform + duration + lock)
- `AudioRecordingPreview` (playback + retry)

### Link Previews
- Auto-detected in input text
- Controlled by `urlPreviewType` ('full' | 'compact')

---

## 7. Message Bubbles

### Layers (top to bottom)
```
MessageItemView
  alignment: 'left' | 'right' (based on sender vs current user)
  groupStyles: 'top' | 'bottom' | 'middle' | 'single'
  MessageAuthor (avatar, last in group only)
  [swipe-to-reply wrapper]
  MessageContent
    MessagePinnedHeader ("Pinned by...")
    MessageContentTopView (slot)
    MessageHeader
    ReactionList (top/bottom/clustered)
    Gallery / FileAttachmentGroup / Giphy / URLPreview / AudioAttachment
    MessageTextContainer
    MessageContentBottomView (slot)
    MessageFooter
    ReactionList (if position='bottom')
  MessageReplies (thread reply count + avatars)
  MessageStatus (timestamp + read receipts: sent/delivered/read/failed)
  MessageSpacer
```

### Alignment Rules
- Default: received = left, sent = right
- Override with `forceAlignMessages` on Channel
- `alignment` prop from context per message

### Grouping
- Consecutive same-user messages grouped
- `groupStyles`: `'top'`, `'middle'`, `'bottom'`, `'single'`
- Avatar on last message in group only
- Controlled by `enableMessageGroupingByUser` (default true)
- `maxTimeBetweenGroupedMessages` controls max gap
- Custom `getMessageGroupStyle` function possible

### Reactions
- Types: `ReactionListTop`, `ReactionListBottom`, `ReactionListClustered`
- Position: `reactionListPosition` = 'top' | 'bottom'
- Style: `reactionListType` = 'clustered' | 'simple'
- `supportedReactions` array, `enforceUniqueReaction`, `selectReaction`

### Thread Replies
- `MessageReplies` shows reply count + avatars
- Tapping calls `onThreadSelect` on MessageList

### Status Indicators
- `MessageStatus` - time + checkmarks (sent, delivered, read, failed)
- `MessageTimestamp` - time display
- `MessageEditedTimestamp` - edited indicator
- `MessageError` / `MessageDeleted` / `MessageBounce` / `MessageBlocked` states

### Content Slots (customization around bubble)
- `MessageContentTopView` - slot above
- `MessageContentBottomView` - slot below
- `MessageContentLeadingView` - slot left
- `MessageContentTrailingView` - slot right

---

## 8. Typing Indicator

- Rendered inside MessageList (at bottom, since inverted)
- Reads state from `TypingContext`
- `useTypingString` hook provides display text: "Jane is typing..." / "Jane and 2 others..."
- Controlled by `disableTypingIndicator` on Channel
- Override via `WithComponents overrides={{ TypingIndicator: Custom }}`

---

## 9. Attachments

### Attachment Types in `messageContentOrder`
```typescript
['quoted_reply', 'gallery', 'files', 'poll', 'ai_text', 'attachments', 'text', 'location']
```

### Image/Video Gallery
- Grid layout (1, 2, 3+ images)
- `VideoThumbnail` play icon overlay
- Full-screen viewer via `OverlayProvider`

### File Attachments
- `FileAttachmentGroup` + `FileAttachment` (icon, name, size, download)
- `FileIcon` for file type

### Audio
- `AudioAttachment` - player with play/pause, progress, speed, waveform

### Giphy
- Animated GIF with attribution badge

### Link Previews
- `URLPreview` (full) / `URLPreviewCompact`

---

## 10. Channel Props Reference (Key Customization)

| Prop | Default | Purpose |
|---|---|---|
| `keyboardVerticalOffset` | - | Nav header height |
| `keyboardBehavior` | - | 'height' | 'position' | 'padding' |
| `disableKeyboardCompatibleView` | false | Disable built-in keyboard handling |
| `enableMessageGroupingByUser` | true | Group consecutive messages |
| `forceAlignMessages` | false | 'left' | 'right' | false |
| `hideDateSeparators` | false | Hide date separators |
| `hideStickyDateHeader` | false | Hide sticky date header |
| `disableTypingIndicator` | false | Disable typing indicator |
| `dismissKeyboardOnMessageTouch` | true | Dismiss keyboard on message tap |
| `enableSwipeToReply` | true | Enable swipe-to-reply |
| `supportedReactions` | reactionData | Available reactions |
| `reactionListPosition` | 'top' | 'top' | 'bottom' |
| `reactionListType` | 'clustered' | 'clustered' | 'simple' |
| `enforceUniqueReaction` | false | One reaction per user |
| `audioRecordingEnabled` | false | Voice recording support |
| `hasImagePicker` | true | Show image picker |
| `hasFilePicker` | true | Show file picker |
| `hasCommands` | true | Enable /commands |
| `allowSendBeforeAttachmentsUpload` | follows offline | Send before uploads finish |
| `doSendMessageRequest` | - | Override send API |
| `doFileUploadRequest` | - | Custom CDN upload |
| `initialScrollToFirstUnreadMessage` | false | Start at first unread |

---

## 11. Dependencies

### Direct Dependencies
| Package | Version | Purpose |
|---|---|---|
| `@gorhom/bottom-sheet` | 5.2.9 | Attachment picker bottom sheet |
| `dayjs` | 1.11.13 | Date formatting |
| `emoji-regex` | ^10.4.0 | Emoji detection |
| `i18next` | ^25.2.1 | Internationalization |
| `linkifyjs` | ^4.3.2 | Link parsing in text |
| `lodash-es` | 4.18.1 | Utilities |
| `react-native-markdown-package` | 1.8.2 | Markdown rendering |
| `stream-chat` | ^9.44.2 | Stream JS client |

### Required Peer Dependencies
| Package | Min Version | Purpose |
|---|---|---|
| `react-native` | >=0.76.0 | Core |
| `@react-native-community/netinfo` | >=11.3.1 | Network state |
| `react-native-gesture-handler` | >=2.18.0 | Gestures |
| `react-native-reanimated` | >=3.16.0 | Animations |
| `react-native-svg` | >=15.8.0 | SVG rendering |
| `react-native-teleport` | >=0.5.4 | Portal system |
| `react-native-safe-area-context` | >=5.4.1 | Safe area |

### Optional Peer Dependencies
- `@shopify/flash-list` >=2.1.0 (high-perf message list)
- `@op-engineering/op-sqlite` >=14.0.0 (offline support)
- `emoji-mart` >=5.4.0 (emoji picker)

### Installation
```bash
# RN CLI
yarn add stream-chat-react-native
yarn add @react-native-community/netinfo react-native-gesture-handler react-native-reanimated react-native-teleport react-native-worklets react-native-svg react-native-safe-area-context

# Expo
npx expo install stream-chat-expo
npx expo install @react-native-community/netinfo expo-image-manipulator react-native-gesture-handler react-native-reanimated react-native-svg react-native-teleport react-native-safe-area-context
```

Requires `react-native-reanimated/plugin` in babel config.

---

## 12. Contexts Overview

| Context | Provider | Hook | Key Values |
|---|---|---|---|
| `ChannelContext` | Channel | `useChannelContext` | channel, members, watchers, loading |
| `ChatContext` | Chat | `useChatContext` | client, connection status |
| `ThemeContext` | OverlayProvider + Chat | `useTheme` | theme object, styles |
| `TranslationContext` | OverlayProvider + Chat | `useTranslationContext` | t() function, locale |
| `MessagesContext` | Channel | `useMessagesContext` | message rendering config |
| `MessageInputContext` | Channel | `useMessageInputContext` | text, sendMessage, editing, attachments |
| `PaginatedMessageListContext` | Channel | `usePaginatedMessageListContext` | messages, loadingMore, loadMore |
| `AttachmentPickerContext` | Channel | `useAttachmentPickerContext` | bottomInset, topInset, open/close |
| `KeyboardContext` | Channel | `useKeyboardContext` | keyboardHeight, isKeyboardVisible |
| `TypingContext` | Channel | `useTypingContext` | typing users |
| `ThreadContext` | Channel | `useThreadContext` | thread message, replies |
| `ImageGalleryContext` | OverlayProvider | `useImageGalleryContext` | images, open/close gallery |
| `MessageComposerAPIContext` | Channel | `useMessageComposerAPIContext` | composer state |

---

## 13. Component Override System

Uses `WithComponents` to inject custom component overrides:

```tsx
<WithComponents overrides={{
  // MessageList overrides
  FooterComponent: CustomLoadingMore,
  HeaderComponent: CustomLoadingRecent,
  ScrollToBottomButton: CustomScrollButton,
  TypingIndicator: CustomTyping,
  DateHeader: CustomDateHeader,

  // Message rendering
  Attachment: CustomAttachment,
  FileAttachment: CustomFile,
  Gallery: CustomGallery,
  MessageTextContainer: CustomTextContainer,

  // Composer overrides
  AutoCompleteInput: CustomAutoComplete,
  TextInputComponent: CustomTextInput,
  SendButton: CustomSend,
  AttachButton: CustomAttach,
  CommandsButton: CustomCommands,

  // Overlay overrides
  ImageGalleryHeader: CustomGalleryHeader,
  MessageActions: CustomMessageActions,
}}>
  <OverlayProvider>
    <Chat>
      <Channel>
        <MessageList />
        <MessageComposer />
      </Channel>
    </Chat>
  </OverlayProvider>
</WithComponents>
```

---

## 14. Scrolling When Keyboard Opens

### Flow
1. User taps TextInput -> keyboard opens
2. `KeyboardCompatibleView` adjusts layout height
3. MessageList re-sizes, composer moves up
4. If scrolled to bottom: latest messages visible above keyboard
5. If scrolled up: position maintained, composer slides up
6. Tapping message dismisses keyboard (default)
7. Attachment picker: opens as bottom sheet, list shifts up

### Key Props for Correct Behavior
```tsx
<Channel
  keyboardVerticalOffset={headerHeight}
  topInset={headerHeight}
  dismissKeyboardOnMessageTouch={true}
  disableKeyboardCompatibleView={false}
/>
```

---

## 15. Message Data Model

```typescript
interface Message {
  id: string
  text: string
  user: UserResponse
  created_at: string
  updated_at: string
  attachments: Attachment[]
  reaction_counts?: Record<string, number>
  reaction_scores?: Record<string, number>
  own_reactions?: Reaction[]
  reply_count?: number
  parent_id?: string
  mentioned_users?: UserResponse[]
  pinned?: boolean
  pinned_at?: string
  pin_expires?: string
  silent?: boolean
  type: 'regular' | 'system' | 'ephemeral' | 'deleted' | 'error'
  status?: 'sending' | 'failed'
  // ... many more fields
}
```

Note: Stream uses its own message model from `stream-chat` JS client, not the simpler `IMessage` interface from gifted-chat.
