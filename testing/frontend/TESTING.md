# Frontend Testing Guide

This frontend suite focuses on the user-facing flows that matter most:

- Authentication entry and mode switching
- Landing page conversation creation
- Chat page message loading and streaming response handling
- Menu/history navigation
- Account profile editing
- Route protection for authenticated pages

## Run Tests

From the `frontend` folder:

```bash
npm test -- --watchAll=false --runInBand
```

## What Is Covered

- `PageAuth`: sign up, sign in, Google auth trigger, validation errors
- `PageLanding`: create room, save first message, navigate to chat
- `PageChat`: load room history, stream assistant output, save user messages
- `NavBar`: open history, navigate to saved chats, delete chat history, go to account
- `PageAccount`: load profile, save profile, logout
- `RequireAuth`: redirect unauthenticated users

## Notes

- Tests use mocked services and router hooks so they stay fast and deterministic.
- Streaming chat tests stub `fetch()` with a manual chunked response.
- If the UI changes text labels or placeholders, update the tests and matrix together.

## Related Documents

- [Test Matrix Summary](TEST_CASES.md)
- [Detailed Test Appendix](TEST_CASES_APPENDIX.md)