# Frontend Test Case Appendix

## Auth

| Case | Behavior | Expected result |
| --- | --- | --- |
| Auth-01 | Submit empty form | Validation error is shown |
| Auth-02 | Submit sign-up form | `signUp` is called with email/password |
| Auth-03 | Switch to sign-in mode | Submit button changes to sign-in behavior |
| Auth-04 | Click Google button | Google auth handler is called |

## Landing

| Case | Behavior | Expected result |
| --- | --- | --- |
| Land-01 | Submit first message | Room is created, message is saved, and user navigates to chat |
| Land-02 | Loading state active | Chat input is disabled |

## Chat

| Case | Behavior | Expected result |
| --- | --- | --- |
| Chat-01 | Open chat room | Room title and history are loaded |
| Chat-02 | First message from landing | Streaming assistant response is started automatically |
| Chat-03 | Stream metadata arrives | Metadata is attached to assistant message |
| Chat-04 | Stream content arrives | Assistant text grows chunk by chunk |
| Chat-05 | Send a user message | User message is saved before streaming starts |

## Navigation

| Case | Behavior | Expected result |
| --- | --- | --- |
| Nav-01 | Open menu | Menu becomes visible |
| Nav-02 | Load history | User room list is fetched from service |
| Nav-03 | Click a room | Navigate to the selected chat room |
| Nav-04 | Delete history | Confirmation is required and room is removed |
| Nav-05 | Click account link | Navigate to account page |

## Account

| Case | Behavior | Expected result |
| --- | --- | --- |
| Acc-01 | Load account page | Profile data and option lists are fetched |
| Acc-02 | Save profile | Update payload is sent to service |
| Acc-03 | Logout | Logout handler is called |

## Guard

| Case | Behavior | Expected result |
| --- | --- | --- |
| Guard-01 | Unauthenticated access | Redirect to `/auth` |
| Guard-02 | Authenticated access | Children are rendered |

## Notes

- These tests intentionally mock router hooks and backend services.
- They are meant to protect the main user flows, not to replace backend API tests.