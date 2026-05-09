*** Settings ***
Library    SeleniumLibrary
Library    Collections

Suite Setup       Open Frontend Browser
Suite Teardown    Close Browser

*** Variables ***
${FRONTEND_URL}           http://localhost:3000
${BROWSER}                Chrome
${RUN_REGISTER}           ${False}
${TEST_EMAIL}             test@gmail.com
${TEST_PASSWORD}          123456789
${CHAT_MESSAGE}           สอบถามสิทธิการลาพักร้อนจาก Robot UI

*** Keywords ***
Open Frontend Browser
    Open Browser    ${FRONTEND_URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Timeout    20s
    Set Selenium Implicit Wait    0.5s
    Wait Until Keyword Succeeds    20s    1s
    ...    Initial Page Should Be Ready

Initial Page Should Be Ready
    ${on_auth}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="auth-email-input"]
    ${on_landing}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="landing-page"]
    ${on_chat}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="chat-page"]
    ${ok}=    Evaluate    ${on_auth} or ${on_landing} or ${on_chat}
    IF    not ${ok}
        Fail    Initial page is not ready yet.
    END

Go To Sign In Mode
    ${has_switch}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="auth-switch-to-signin"]
    IF    ${has_switch}
        Click Element    css=[data-testid="auth-switch-to-signin"]
    END

Register With Email Password
    [Arguments]    ${email}    ${password}
    Wait Until Page Contains Element    css=[data-testid="auth-email-input"]
    Input Text    css=[data-testid="auth-email-input"]    ${email}
    Input Password    css=[data-testid="auth-password-input"]    ${password}
    Click Element    css=[data-testid="auth-submit-button"]

Login With Email Password
    [Arguments]    ${email}    ${password}
    ${already_landing}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="landing-page"]
    ${already_chat}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="chat-page"]
    ${already_logged_in}=    Evaluate    ${already_landing} or ${already_chat}
    IF    ${already_logged_in}
        RETURN
    END
    Go To Sign In Mode
    Wait Until Page Contains Element    css=[data-testid="auth-email-input"]
    Input Text    css=[data-testid="auth-email-input"]    ${email}
    Input Password    css=[data-testid="auth-password-input"]    ${password}
    Click Element    css=[data-testid="auth-submit-button"]

Ensure Logged In
    Wait Until Keyword Succeeds    30s    2s
    ...    Authenticated Page Should Be Visible

Authenticated Page Should Be Visible
    ${on_landing}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="landing-page"]
    ${on_chat}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="chat-page"]
    ${ok}=    Evaluate    ${on_landing} or ${on_chat}
    IF    not ${ok}
        Fail    Authenticated page is not visible yet.
    END

Send First Chat Message
    [Arguments]    ${message}
    Wait Until Page Contains Element    css=[data-testid="chat-input-field"]
    Input Text    css=[data-testid="chat-input-field"]    ${message}
    Click Element    css=[data-testid="chat-send-button"]
    Wait Until Location Contains    /chat/
    Wait Until Page Contains    ${message}    5m
    Wait Until Element Is Enabled    css=[data-testid="chat-input-field"]    3m
    Wait Until Element Is Visible    xpath=//*[contains(@class,"message-metadata")]    3m

Click Visible Test Id
    [Arguments]    ${test_id}
    ${clicked}=    Run Keyword And Return Status
    ...    Click Element    css=[data-testid="${test_id}"]
    IF    not ${clicked}
        ${clicked}=    Execute JavaScript    const els=[...document.querySelectorAll('[data-testid="${test_id}"]')]; const el=els.find(e=>e.offsetParent!==null && getComputedStyle(e).visibility!=='hidden' && getComputedStyle(e).display!=='none'); if(el){el.click(); return true;} return false;
    END
    IF    not ${clicked}
        Fail    Could not click visible element for test-id: ${test_id}
    END

Open Menu
    ${opened}=    Run Keyword And Return Status
    ...    Click Visible Test Id    menu-open-button
    IF    not ${opened}
        ${opened}=    Run Keyword And Return Status
        ...    Execute JavaScript    document.querySelector('[data-testid="menu-open-button"]')?.click();
    END
    IF    ${opened}
        Wait Until Page Contains Element    css=[data-testid="menu-panel"]
    END

Open Library From Menu
    Open Menu
    Click Visible Test Id    menu-library-button
    Wait Until Location Contains    /library
    Wait Until Page Contains Element    css=[data-testid="library-page-title"]

Open First Law Card
    Wait Until Page Contains Element    css=[data-testid^="law-card-act-"]
    Click Element    css=[data-testid^="law-card-act-"]
    Wait Until Location Contains    /library/act/

Open History In Menu
    Open Menu
    Click Visible Test Id    menu-history-button
    Wait Until Page Contains Element    css=.menu-subitem

Open Profile Settings From Menu
    Open Menu
    Click Visible Test Id    menu-account-button
    Wait Until Location Contains    /account
    Wait Until Page Contains Element    css=[data-testid="account-page-title"]

Update Profile Settings
    Wait Until Page Contains Element    css=[data-testid="account-birthdate-input"]
    Wait Until Element Is Enabled    css=[data-testid="account-birthdate-input"]    30s
    Wait Until Element Is Enabled    css=[data-testid="account-startdate-input"]    30s
    Wait Until Element Is Enabled    css=[data-testid="account-job-select"]    30s
    Wait Until Element Is Enabled    css=[data-testid="account-jobtype-select"]    30s
    Scroll Element Into View    css=[data-testid="account-birthdate-input"]
    Execute JavaScript    document.querySelector('[data-testid="account-birthdate-input"]').value='1990-01-01'; document.querySelector('[data-testid="account-birthdate-input"]').dispatchEvent(new Event('input', {bubbles:true})); document.querySelector('[data-testid="account-birthdate-input"]').dispatchEvent(new Event('change', {bubbles:true}));
    Execute JavaScript    document.querySelector('[data-testid="account-startdate-input"]').value='2020-01-01'; document.querySelector('[data-testid="account-startdate-input"]').dispatchEvent(new Event('input', {bubbles:true})); document.querySelector('[data-testid="account-startdate-input"]').dispatchEvent(new Event('change', {bubbles:true}));
    Select From List By Index    css=[data-testid="account-job-select"]    1
    Select From List By Index    css=[data-testid="account-jobtype-select"]    1
    Scroll Element Into View    css=[data-testid="account-save-button"]
    Wait Until Element Is Enabled    css=[data-testid="account-save-button"]    30s
    Click Element    css=[data-testid="account-save-button"]

Logout From Account Page
    Click Element    css=[data-testid="account-logout-button"]
    Wait Until Keyword Succeeds    20s    1s
    ...    Logged Out State Should Be Visible

Logged Out State Should Be Visible
    ${on_auth_input}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="auth-email-input"]
    ${on_auth_page}=    Run Keyword And Return Status
    ...    Page Should Contain Element    css=[data-testid="auth-page"]
    ${on_auth_route}=    Run Keyword And Return Status
    ...    Location Should Contain    /auth
    ${ok}=    Evaluate    ${on_auth_input} or ${on_auth_page} or ${on_auth_route}
    IF    not ${ok}
        Fail    Logged-out state is not visible yet.
    END

*** Test Cases ***
End To End User Journey Register Login Chat Library History Profile Logout
    ${email}=    Set Variable    ${TEST_EMAIL}

    IF    ${RUN_REGISTER}
        ${on_auth}=    Run Keyword And Return Status
        ...    Page Should Contain Element    css=[data-testid="auth-email-input"]
        IF    ${on_auth}
            ${stamp}=    Evaluate    __import__('time').strftime('%Y%m%d%H%M%S')
            ${email}=    Set Variable    robot.e2e.${stamp}@example.com
            Register With Email Password    ${email}    ${TEST_PASSWORD}
        ELSE
            Log    Skip register because current page is already authenticated state.
        END
    END

    Login With Email Password    ${email}    ${TEST_PASSWORD}
    Ensure Logged In
    Send First Chat Message    ${CHAT_MESSAGE}
    Open Library From Menu
    Open First Law Card
    Open History In Menu
    Open Profile Settings From Menu
    Update Profile Settings
    Logout From Account Page