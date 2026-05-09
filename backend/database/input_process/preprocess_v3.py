import re
import glob

thai_to_arabic = str.maketrans("๑๒๓๔๕๖๗๘๙๐","1234567890")
thai_number_words = r"(หนึ่ง|สอง|สาม|สี่|ห้า|หก|เจ็ด|แปด|เก้า|สิบ|สิบเอ็ด|สิบสอง)"
ordinal_suffixes = r"(ทวิ|ตรี|จัตวา|เบญจ|ฉ|สัปต|อัฏฐ|นพ|ทศ)"
thai_word_map = {
                    "หนึ่ง": 1, "สอง": 2, "สาม": 3, "สี่": 4, "ห้า": 5,
                    "หก": 6, "เจ็ด": 7, "แปด": 8, "เก้า": 9,
                    "สิบ": 10, "สิบเอ็ด": 11, "สิบสอง": 12
                }

file_names = glob.glob("../*/backend/database/input_process/act/act_*.txt")

def clean_text(text):
    text = text.translate(thai_to_arabic)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def find_references_in_text(text, key):
    # detect references like:
    # - มาตรา 41
    # - มาตรา 100/1
    # - มาตรา 47 ทวิ
    # - มาตรา 50 วรรค 2
    # - มาตรา 50 วรรค 2 (1)
    # - วรรคสาม
    # - วรรค 3
    # - (2)
    # - (ก)
    text = text[1:]
    
    # Combined pattern for all reference types
    pattern = re.compile(
        r"""
        (                                                           # Group 1: Section + optional paragraph + item
            มาตรา\s*(\d+)(?:/(\d+))?                    # Section and optional sub-section (multi-digit allowed)
            (?:\s*(ทวิ|ตรี|จัตวา|เบญจ|ฉ|สัปต|อัฏฐ|นพ|ทศ))?       # Optional ordinal suffix
            (?:\s*วรรค\s*(\d+|หนึ่ง|สอง|สาม|สี่|ห้า|หก|เจ็ด|แปด|เก้า|สิบ))?  # Optional paragraph (Thai-letter limited to one)
            (?:\s*(\((?:[ก-ฮ]|\d+)\)))?                             # Optional item reference (parenthesis content restricted)
        )
        |
        (วรรค\s*(\d+|หนึ่ง|สอง|สาม|สี่|ห้า|หก|เจ็ด|แปด|เก้า|สิบ))  # Group 2: Standalone paragraph (Thai-letter single)
        |
        (\((?:[ก-ฮ]|\d+)\))                                                 # Group 3: Standalone item (single Thai letter or multi-digit number)
        """,
        re.VERBOSE
    )

    finds = []
    for m in pattern.finditer(text):
        # ignore a leading parenthesis that marks the start-of-line item (we don't want to treat that as an inline reference)
        if m.group(9) and m.start() == 0:
            continue
        
        info = {"pos": m.start(), "match": m.group(0)}
        
        if m.group(1):  # Section-based reference
            info["type"] = "section"
            sec = m.group(2)
            sub = m.group(3)
            suffix = m.group(4)
            para = m.group(5)
            item = m.group(6)
            
            ref = f"{sec}" + (f"/{sub}" if sub else "") + (f" {suffix}" if suffix else "")
            info["ref"] = ref
            info["section"] = int(sec)
            if sub:
                info["sub_section"] = sub
            if suffix:
                info["suffix"] = suffix
            if para:
                # convert thai word to number if possible
                if para.isdigit():
                    num = int(para)
                else:
                    num = thai_word_map.get(para, None)
                if num is not None:
                    info["paragraph"] = num
            if item:
                info["item_text"] = item
                
        elif m.group(7):  # Standalone paragraph reference
            info["type"] = "paragraph"
            grp = m.group(8)
            # convert thai word to number if possible
            if grp.isdigit():
                num = int(grp)
            else:
                num = thai_word_map.get(grp, None)
                for i in range(1, 10):
                    print("group", i, m.group(i))
                print("grp, num", grp, num)
            info["ref"] = str(num) if num is not None else grp
            if num is not None:
                info["paragraph"] = num
                
        elif m.group(9):  # Standalone item reference
            info["type"] = "parenthesis"
            val = m.group(9).strip("()")
            info["ref"] = val
            info["item"] = val
            
        finds.append(info)

    if not finds:
        return key

    # sort by position and append to key
    finds.sort(key=lambda x: x["pos"])
    key += "\"references\":{"
    i = 0
    last_section = None
    last_index = 0
    while i < len(finds):
        f = finds[i]
        
        # section reference (อาจมี paragraph ในตัวแล้วจาก regex)
        if f["type"] == "section":
            sec = f.get("section")
            last_section = sec
            pos = f["pos"]
            text = f["match"].replace('"', '\\"')
            entry = '{"original_text":"' + text + '"'
            entry += f',"section_number":{sec}'
            if "sub_section" in f:
                entry += f',"sub_section":"{f["sub_section"]}"'
            if "suffix" in f:
                entry += f',"ordinal_suffix":"{f["suffix"]}"'
            if "paragraph" in f:
                entry += f',"paragraph_number":{f["paragraph"]}'
            entry += '}'
            key += f'{pos+1}:{entry},'
            last_index = pos + len(text)
            i += 1
            continue

        # paragraph without preceding section -> standalone paragraph
        if f["type"] == "paragraph":
            pos = f["pos"]
            orig = f["match"]
            entry = '{"original_text":"' + orig.replace('"', '\\"') + '"'
            if (last_section is not None) and (pos - last_index < 8):  # only inherit section if it's not too close (to avoid capturing the starting parenthesis of a section item)
                entry += f',"section_number":{last_section}'
            if "paragraph" in f:
                entry += f',"paragraph_number":{f["paragraph"]}'
            entry += '}'
            key += f'{pos+1}:{entry},'
            i += 1
            continue

        # parenthesis (item), create separate entry and inherit last_section if available
        if f["type"] == "parenthesis":
            pos = f["pos"]
            orig = f["match"]
            entry = '{"original_text":"' + orig.replace('"', '\\"') + '"'
            entry += f',"item_order":"{f["item"]}"'
            if last_section is not None:
                entry += f',"section_number":{last_section}'
            entry += '}'
            key += f'{pos+1}:{entry},'
            i += 1
            continue

        # fallback
        i += 1

    key += "},"
    return key

def find_citations_in_text(text, key):
    # Find all citations like [1] and record their positions (do not skip start)
    finds = list(re.finditer(r'\[(\d+)\]', text))
    if not finds:
        return key
    key += "\"citations\":{"
    for f in finds:
        citation_num = f.group(1)
        pos = f.start()
        key += f"{pos}:{{\"citation\":{citation_num}}},"
    # remove all citation markers from the text
    text = re.sub(r'\[\d+\]', '', text)
    act[i] = text
    key += "},"
    return key

def parse_book_key(text, key):
    global current_part, i_book, i_group, i_super
    m = re.match(r"บรรพ\s+([0-9]+)", text)
    book = m.group(1)
    key += f"\"book\":{book},"
    i_book = book
    i_group, i_super = 0, 0
    current_part = f"\"book\":{book},"
    return key

def parse_group_key(text, key):
    global current_part, i_book, i_group, i_super
    m = re.match(r"ลักษณะ\s+([0-9]+)", text)
    group = m.group(1)
    key += f"\"book\":{i_book},\"group\":{group},"
    i_group = group
    i_super = 0
    current_part = f"\"book\":{i_book},\"group\":{group},"
    return key

def parse_super_section_key(text, key):
    global current_part, i_book, i_group, i_super
    m = re.match(r"หมวด\s+([0-9]+)", text)
    super_section = m.group(1)
    key += f"\"book\":{i_book},\"group\":{i_group},\"super_section\":{super_section},"
    i_super = super_section
    current_part = f"\"book\":{i_book},\"group\":{i_group},\"super_section\":{super_section},"
    return key

def parse_intro_key(key):
    global current_part, i_intro
    key += f"\"intro\":true,\"paragraph\":{i_intro},"
    i_intro += 1
    current_part = None
    return key

def parse_section_key(text, key):
    global current_part
    m = re.match(rf"มาตรา\s+([0-9]+)(?:/([0-9]+))?(?:\s*{ordinal_suffixes})?", text)
    section = m.group(1)
    sub_section = m.group(2) if m.group(2) else m.group(3) if m.group(3) else None
    key += f"\"book\":{i_book},\"group\":{i_group},\"super_section\":{i_super},\"section\":{section}," + (f"\"sub_section\":\"{sub_section}\"," if sub_section else "")
    current_part = f"\"book\":{i_book},\"group\":{i_group},\"super_section\":{i_super},\"section\":{section}," + (f"\"sub_section\":\"{sub_section}\"," if sub_section else "")
    return key

def parse_item_key(text, key):
    global current_part
    m = re.match(r'^\(\s*([ก-ฮ/\d]+)\s*\)', text)
    item = m.group(1)
    key += current_part + f"\"item\":\"{item}\","
    return key

def parse_citation_key(text, key):
    m = re.match(r'^\[(\d+)\]', text)
    if not m:
        return key
    citation = m.group(1)
    key = f"{{\"citation\":{citation}"
    return key

def connect_paragraphs(key, i):
    key += "};" + act[i] + r"\n"
    while act[i+1] != "---------------------":
        i+=1
        act[i] = clean_text(act[i])
        key += act[i] + r"\n"
    results.append(key[:-2] + "\n")
    i+=1
    return key, i

for file_name in file_names:
    print(f"Processing {file_name}...")
    with open(file_name, "r", encoding="utf-8") as f:
        act = f.read()
        act = act.splitlines()
    results = []
    i = 0
    i_intro, i_book, i_group, i_super, i_section = 0, 0, 0, 0, 0
    current_part = None
    while i < len(act)-1:
        if act[i] == "---------------------":
            paragraph_number = 1
            i+=1
            continue
        else:
            act[i] = clean_text(act[i])
            key = "{"
            # print(f"Processing line {i}: {act[i]}")
            if act[i].startswith("มาตรา"):
                key = parse_section_key(act[i], key)
            elif act[i].startswith("("):
                paragraph_number-=1
                key = parse_item_key(act[i], key)
            elif act[i].startswith("หมวด"):
                key = parse_super_section_key(act[i], key)
                key, i = connect_paragraphs(key, i)
                continue
            elif act[i].startswith("ลักษณะ"):
                key = parse_group_key(act[i], key)
                key, i = connect_paragraphs(key, i)
                continue
            elif act[i].startswith("บรรพ"):
                key = parse_book_key(act[i], key)
                key, i = connect_paragraphs(key, i)
                continue
            elif act[i].startswith("["):
                key = parse_citation_key(act[i], key)
                key += "};"
                results.append(key + act[i] + "\n")
                i+=1
                continue
            elif current_part is None:
                # Other introductory lines
                key = parse_intro_key(key)
                key += "};"
                results.append(key + act[i] + "\n")
                i+=1
                continue
            else:
                key += current_part
            key += f"\"paragraph\":{paragraph_number},"
            print(f"Processing line {i}: with key: {key}")
            print(f"Current line: {act[i]}")
            key = find_citations_in_text(act[i], key)
            key = find_references_in_text(act[i], key)
            key += "};"
            results.append(key + act[i] + "\n")
            paragraph_number += 1
            i+=1

    fn = file_name.replace("act\\act_", "preprocessv3\\preprocess_")
    print(f"Writing results to {fn}...")
    with open(fn, "w", encoding="utf-8") as f:
        for line in results:
            f.write(line)
