def tokenize(code):
    tokens = []
    klammern = []
    current_token = ""
    in_string = False
    string_delimiter = ""

    oeffnende_klammern = "([{"
    schliessende_klammern = ")] }"
    klammerpaare = {
        ")": "(",
        "]": "[",
        "}": "{",
    }
    sonderzeichen = ".,:+-*/=%<>!;"

    for char in code:
        if char in ('"', "'"):
            if in_string:
                current_token += char
                if char == string_delimiter:
                    tokens.append(current_token)
                    current_token = ""
                    in_string = False
            else:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                in_string = True
                string_delimiter = char
                current_token += char

        elif in_string:
            current_token += char

        elif char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ""

        elif char in oeffnende_klammern:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            klammern.append(char)
            tokens.append(char)

        elif char in schliessende_klammern:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            if not klammern or klammern[-1] != klammerpaare[char]:
                raise ValueError(f"Ungültige schließende Klammer: {char}")
            klammern.pop()
            tokens.append(char)

        elif char in sonderzeichen:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)

        else:
            current_token += char

    if current_token:
        tokens.append(current_token)

    if klammern:
        return("Fehler")

    return tokens