*** Settings ***
Library    SeleniumLibrary
Library    Collections
Library    OperatingSystem

*** Variables ***
@{URLS}    https://searchlaw.ocs.go.th/council-of-state/#/public/doc/WGl0RzNRbzlyUzNZT2Vxd0U4NUtadz09    https://searchlaw.ocs.go.th/council-of-state/#/public/doc/VWxmNWlNYmk3QVVCek4xanliSThFZz09    https://searchlaw.ocs.go.th/council-of-state/#/public/doc/SWxpV2NWRzZCK29xZ3VvWTYxWGNhQT09    https://searchlaw.ocs.go.th/council-of-state/#/public/doc/alJWY29wVXFRUUo0WkF2MTEwSndpQT09

*** Test Cases ***
Extract Law Articles
    ${TARGET}=   Evaluate    next(iter(__import__('glob').glob('**/backend/database/input_process/act', recursive=True)), '../backend/database/input_process/act')
    FOR    ${url}    IN    @{URLS}
        Open Browser    ${url}    Chrome
        Sleep    1s
        Wait Until Page Contains Element    //div[@class="in-a4"]    timeout=10s
        ${act_name}=    Get Text    //div[@class="col-12 mb-3 line-ellipsis"]
        Log    Act Name: ${act_name}
        Create File    act_${act_name}.txt    ${act_name}\n
        ${section_count}=    Get Element Count    //div[@class="in-a4"]/div
        Log    Number of Sections: ${section_count}
        FOR    ${block}    IN RANGE    1    ${section_count} + 1
            ${paraphrases}=    Get Element Count    //div[@class="in-a4"]/div[${block}]/p
            Log    Number of Paragraphs in Section ${block}: ${paraphrases}
            ${section}=    Create List
            FOR    ${p}    IN RANGE    1    ${paraphrases} + 1
                ${text}=    Get Text    //div[@class="in-a4"]/div[${block}]/p[${p}]
                Append To List    ${section}    ${text}
                Append To File    ${TARGET}/act_${act_name}.txt    ${text}\n
            END
            Append To File    ${TARGET}/act_${act_name}.txt    ---------------------\n
            Log    Article: ${act_name}
            Log    Texts: ${section}
        END
        Close Browser
    END