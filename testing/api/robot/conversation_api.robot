*** Settings ***
Library    RequestsLibrary
Library    Collections

*** Variables ***
${BASE_URL}         http://127.0.0.1:8000
${TOKEN}            eyJhbGciOiJFUzI1NiIsImtpZCI6IjRiOWJiZjE3LThkNTYtNGZlNC04NmM3LTc0ZjgyZTFkNjhiNyIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3NpeWp6aXlqY3BqeGdxZWtid3VnLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJjZTlhZThiNy03ZjVmLTRiZjMtYTliYy1kOTc3NTc3ZDk0ZTYiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzc1NTgyOTM2LCJpYXQiOjE3NzU1NzkzMzYsImVtYWlsIjoidGVzdEBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoidGVzdEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiJjZTlhZThiNy03ZjVmLTRiZjMtYTliYy1kOTc3NTc3ZDk0ZTYifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc3NTU3OTMzNn1dLCJzZXNzaW9uX2lkIjoiY2NmY2E2OWYtZDg3NC00NDJhLWExYWMtODUwNTc5MGVjYzY0IiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.DXVydNk-GsWxsfWuQJXTiJSjIauUS_bJ-YwtLQGOjq511tCFJbB18eLa3xyuTY25ZHf4xEHwJA4me5u91xCk4w
${USER_ID}          ce9ae8b7-7f5f-4bf3-a9bc-d977577d94e6
${ROOM_TITLE}       ห้องจากโรบอท

*** Test Cases ***
Create Room Then Add And Get Messages
    ${headers}=    Create Dictionary    Authorization=Bearer ${TOKEN}    Content-Type=application/json

    ${create_body}=    Create Dictionary    user_id=${USER_ID}    title=${ROOM_TITLE}
    ${create_resp}=    POST    ${BASE_URL}/api/conversations/rooms    json=${create_body}    headers=${headers}
    Should Be Equal As Integers    ${create_resp.status_code}    200
    ${room}=    Set Variable    ${create_resp.json()}
    Dictionary Should Contain Key    ${room}    id
    ${room_id}=    Set Variable    ${room}[id]

    ${meta}=    Create Dictionary    source=robot
    ${msg_body}=    Create Dictionary    sender=user    message=hello from robot    metadata=${meta}
    ${msg_resp}=    POST    url=${BASE_URL}/api/conversations/rooms/${room_id}/messages    json=${msg_body}    headers=${headers}
    Should Be Equal As Integers    ${msg_resp.status_code}    200

    ${list_resp}=    GET    url=${BASE_URL}/api/conversations/rooms/${room_id}/messages?limit=10    headers=${headers}
    Should Be Equal As Integers    ${list_resp.status_code}    200
    ${messages}=    Set Variable    ${list_resp.json()}
    ${length}=    Get Length    ${messages}
    Should Be Equal As Integers    ${length}    1