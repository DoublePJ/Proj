*** Settings ***
Library    SeleniumLibrary
Library    Collections
Library    OperatingSystem
Library    String
Library    RPA.PDF
Library    RequestsLibrary
Library    ./function.py

*** Variables ***
${URL}    https://lbudtc.coj.go.th/th/content/article/index/id/12404
${UL}    //ul[@class="pagination bootpag"]

*** Test Cases ***
Extract Judgment Articles
    Open Browser    ${URL}    edge
    Sleep    1s
    Maximize Browser Window
    
    WHILE    ${True}
        Wait Until Element Is Visible    //div[@id="result-sublist"]    timeout=10s
        ${articles_count}=    Get Element Count    //div[@id="result-sublist"]//div[@class="inforow"]
        FOR    ${i}    IN RANGE    1    ${articles_count} + 1
            Wait Until Element Is Enabled    //div[@id="result-sublist"]//div[@class="inforow"][${i}]//a    timeout=10s
            Scroll Element Into View    //div[@id="result-sublist"]//div[@class="inforow"][${i}]//a
            Wait Until Element Is Visible    //div[@id="result-sublist"]//div[@class="inforow"][${i}]//a    timeout=10s
            ${article_title}=    Get Text    //div[@id="result-sublist"]//div[@class="inforow"][${i}]//a
            ${article_title_sanitized}=    Replace String    ${article_title}    /    -
            ${article_title_sanitized}=    Evaluate    re.sub(r'[^\d\-]', '', '${article_title_sanitized}')    modules=re
            ${aleary_exists}=    Run Keyword And Return Status    File Should Exist    ./database/input_process/judgments/text/${article_title_sanitized}.txt
            Continue For Loop If    ${aleary_exists}
            Click Element    //div[@id="result-sublist"]//div[@class="inforow"][${i}]//a
            Sleep    1s
            TRY
                ${pdf_link}=    Get Element Attribute    //div[@class="docname"]//a    href
                Sleep    1s
                # สร้าง session สำหรับดาวน์โหลด
                Create Session    pdfsession    ${pdf_link}
                ${response}=    Get Request    pdfsession    /
                Log    ${response}
                Log    ${response.content}
                # sanitize filename and ensure output directory exists, then build path (adds .pdf)
                ${rawfile}=    Write Pdf    ./database/input_process/judgments/pdf    ${article_title_sanitized}.pdf    ${response.content}
                Open Pdf    ${rawfile}
                ${pdf_info}=    Get PDF Info    ${rawfile}
                TRY
                    Close Pdf    ${rawfile}
                EXCEPT
                    Log    Could not close PDF file: ${rawfile}
                END
                @{pages}=    Create List
                FOR    ${p}    IN RANGE    1    ${pdf_info['Pages']} + 1
                    Append To List    ${pages}    ${p}
                END
                ${extracted_text}=    Extract Text    ${rawfile}    pages=${pages}
                Log    ${extracted_text}
                ${textfile}=    Write Text    ./database/input_process/judgments/text    ${article_title_sanitized}.txt    ${extracted_text}
            EXCEPT    ANY
                Log    No PDF found, trying to extract text from webpage.
            END
            Go Back
        END
        Wait Until Page Contains Element    ${UL}    timeout=10s
        Scroll Element Into View    ${UL}
        Wait Until Element Is Visible    //div[@id="result-sublist"]    timeout=10s
        ${current_page}=    Get Text    ${UL}/li[@class="active"]/a
        ${next_page}=    Evaluate    int(${current_page}) + 1
        ${check_next}=    Run Keyword And Return Status    Element Should Be Visible    ${UL}/li/a[text()="${next_page}"]
        IF    ${check_next}
            Wait Until Element Is Enabled    ${UL}/li/a[text()="${next_page}"]    timeout=10s
            Click Element    ${UL}/li/a[text()="${next_page}"]
        ELSE
            BREAK
        END
    END
    