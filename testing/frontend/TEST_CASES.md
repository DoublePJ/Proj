# Frontend Test Matrix Summary

| Area | Critical coverage | Status |
| --- | --- | --- |
| Auth | sign up, sign in, Google auth, required field validation | Done |
| Landing | create room, store first message, route to chat | Done |
| Chat | load history, stream assistant reply, save user message | Done |
| NavBar | open history, navigate to chat, delete history, account link | Done |
| Account | load profile, save profile, logout | Done |
| Route guard | redirect unauthenticated access to `/auth` | Done |

## Scope

This matrix is intentionally focused on production paths that affect real users.
It does not try to cover every visual state or CSS variation.

## Test Strategy

- Unit-level component tests for form behavior and route guards
- Mocked integration-style tests for service calls and streaming chat flow
- Deterministic router/service mocks instead of live backend calls

## Priority Gaps

- PageChat metadata rendering can be expanded later if UI logic changes
- MessageList link handling can get its own dedicated tests if those interactions grow
- Library browsing flows can be added next if frontend coverage needs to expand