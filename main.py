from variablen import *
from tokenizer import *
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Main:
    def __init__(self):
        self.variablen = {}

        self.app = ctk.CTk()
        self.app.title("FoxLang")
        self.app.geometry("800x700")

        self.eingabe = None
        self.terminal_box = None
        self.commands = {
            "schreibe": self.schreibe,
            # "eingabe": selpf.eingabe,
        }

    def process_code(self):
        try:
            self.terminal()

            self.terminal_box.configure(state="normal")
            self.terminal_box.delete("1.0", "end")
            self.terminal_box.configure(state="disabled")

            self.variablen.clear()

            code = self.eingabe.get("1.0", "end-1c")

            tokens = tokenize(code)

            if tokens == "Fehler":
                self.error("Unvollständiger Befehl")
                return

            statements = self.split_code(tokens)

            for statement in statements:
                if len(statement) == 0:
                    continue
                #print(statement)
                #print(self.commands)
                self.execute(statement)

        except Exception as ex:
            self.error(ex)

    def execute(self, tokens):
        if self.is_variable(tokens):
            self.create_variable(tokens)

        elif self.is_command(tokens):
            self.execute_command(tokens)

        else:
            self.error(f"Unbekannter Befehl: {' '.join(map(str, tokens))}")

    def is_variable(self, tokens):
        return len(tokens) >= 3 and tokens[1] == "="

    def create_variable(self, tokens):
        var_name = tokens[0]

        var_value = self.eval_expressions(tokens[2:])

        if var_value == "Fehler":
            return

        if var_name in self.variablen:
            try:
                self.variablen[var_name].value = var_value
            except TypeError as ex:
                self.error(ex)
        else:
            self.variablen[var_name] = Variable(var_value)

    def eval_expressions(self, tokens):
        expression = []

        # Variablen ersetzen und Werte parsen
        for token in tokens:
            if token in self.variablen:
                expression.append(self.variablen[token].value)
            else:
                expression.append(self.parse_value(token))

        # Klammern auswerten
        while "(" in expression:
            start = None
            ende = None

            for i, token in enumerate(expression):
                if token == "(":
                    start = i
                elif token == ")" and start is not None:
                    ende = i
                    break

            if start is None or ende is None:
                self.error("Klammerfehler")
                return "Fehler"

            wert = self.eval_expressions(expression[start + 1:ende])

            expression = (
                expression[:start]
                + [wert]
                + expression[ende + 1:]
            )

        expression = self.calculate_mul_div(expression)
        expression = self.calculate_add_sub(expression)
        expression = self.compare(expression)

        return expression[0]

    def calculate_mul_div(self, tokens):
        expression = []
        i = 0

        while i < len(tokens):

            if tokens[i] == "*":
                result = expression.pop() * tokens[i + 1]
                expression.append(result)
                i += 2

            elif tokens[i] == "/":
                result = expression.pop() / tokens[i + 1]
                expression.append(result)
                i += 2

            else:
                expression.append(tokens[i])
                i += 1

        return expression

    def calculate_add_sub(self, tokens):
        result = tokens[0]

        i = 1

        while i < len(tokens):

            if tokens[i] == "+":
                result += tokens[i + 1]

            elif tokens[i] == "-":
                result -= tokens[i + 1]

            i += 2

        return [result]

    def compare(self, tokens):
        for i, token in enumerate(tokens):
            if token == "<":
                arg = tokens[i - 1] < tokens[i + 1]
                return "wahr" if arg == True else "falsch"
            elif token == ">":
                arg = tokens[i - 1] > tokens[i + 1]
                return "wahr" if arg == True else "falsch"
            elif token == "=":
                if tokens[i + 1] == "=":
                    arg = tokens[i - 1] == tokens[i + 2]
                    return "wahr" if arg == True else "falsch"
                
        return tokens


    def is_command(self, tokens):
        return len(tokens) > 0 and tokens[0] in self.commands

    def execute_command(self, tokens):
        command = self.commands[tokens[0]]

        # Kein Argument
        if len(tokens) == 1:
            command()
            return

        # Klammern entfernen
        if tokens[1] == "(" and tokens[-1] == ")":
            argument_tokens = tokens[2:-1]
        else:
            argument_tokens = tokens[1:]

        # Nur ein einzelnes Argument?
        if len(argument_tokens) == 1:
            arg = self.parse_value(argument_tokens[0])

            # Variable?
            if isinstance(arg, str):
                # String-Literal
                if argument_tokens[0].startswith('"') and argument_tokens[0].endswith('"'):
                    pass

                # Variable vorhanden
                elif arg in self.variablen:
                    arg = self.variablen[arg].value

                else:
                    self.error(f"Variable '{arg}' existiert nicht.")
                    return

        # Ausdruck (z.B. 1+2 oder a*5)
        else:
            arg = self.eval_expressions(argument_tokens)

            if arg == "Fehler":
                return

        command(arg)

    def parse_value(self, value):

        if not isinstance(value, str):
            return value

        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        return value
    
    def terminal(self):
        if self.terminal_box is None:
            self.terminal_box = ctk.CTkTextbox(
                self.tab.tab("Tab 1"),
                width=720,
                height=200
            )
            self.terminal_box.pack(padx=10, pady=0)

            self.eingabe.configure(height=305)

            self.terminal_box.configure(state="disabled")

    def split_code(self, code):
        lines = []
        start = 0

        for i, token in enumerate(code):
            if token == ";":
                if start < i:
                    lines.append(code[start:i])
                start = i + 1

        if start < len(code):
            lines.append(code[start:])

        return lines

    def schreibe(self, arg=""):
        self.terminal_box.configure(state="normal")
        self.terminal_box.insert("end", str(arg) + "\n")
        self.terminal_box.see("end")
        self.terminal_box.configure(state="disabled")

    def error(self, text):
        self.schreibe(f"[Fehler] {text}")


    def run(self):
        self.create_IDE()
        self.app.mainloop()

    def create_IDE(self):
        self.tab = ctk.CTkTabview(self.app)
        self.tab.add("Tab 1")
        self.tab.pack(pady=10, padx=10)

        submit_button = ctk.CTkButton(
            self.tab.tab("Tab 1"),
            text="▶",
            command=self.process_code,
            width=35,
            height=35
        )
        submit_button.pack(pady=5, anchor="ne", padx=10)

        self.eingabe = ctk.CTkTextbox(
            self.tab.tab("Tab 1"),
            width=720,
            height=500
        )
        self.eingabe.pack(pady=5, padx=10)

    


if __name__ == "__main__":
    main = Main()
    main.run()