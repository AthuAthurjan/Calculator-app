
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
import ast
import operator
import re

Window.clearcolor = (0.97, 0.97, 0.97, 1)

OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_calculate(node):
    if isinstance(node, ast.Expression):
        return safe_calculate(node.body)

    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return node.value
        raise ValueError("Invalid number")

    if isinstance(node, ast.BinOp):
        operation = OPERATIONS.get(type(node.op))
        if operation is None:
            raise ValueError("Invalid operator")
        return operation(
            safe_calculate(node.left),
            safe_calculate(node.right)
        )

    if isinstance(node, ast.UnaryOp):
        operation = OPERATIONS.get(type(node.op))
        if operation is None:
            raise ValueError("Invalid operator")
        return operation(safe_calculate(node.operand))

    raise ValueError("Invalid calculation")


def calculate(expression):
    tree = ast.parse(expression, mode="eval")
    result = safe_calculate(tree)

    if isinstance(result, float) and result.is_integer():
        return str(int(result))

    return str(round(result, 10))


class RedmiCalculator(App):

    def build(self):
        self.expression = ""

        root = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=10
        )

        self.display = Label(
            text="0",
            color=(0.12, 0.12, 0.12, 1),
            font_size="48sp",
            halign="right",
            valign="bottom",
            size_hint_y=0.30
        )
        self.display.bind(
            size=lambda obj, size:
            setattr(obj, "text_size", size)
        )
        root.add_widget(self.display)

        grid = GridLayout(
            cols=4,
            spacing=9,
            size_hint_y=0.70
        )

        buttons = [
            "AC", "DEL", "%", "÷",
            "7", "8", "9", "×",
            "4", "5", "6", "−",
            "1", "2", "3", "+",
            "±", "0", ".", "="
        ]

        for symbol in buttons:
            if symbol in ("÷", "×", "−", "+", "="):
                bg = (1.0, 0.60, 0.18, 1)
                fg = (1, 1, 1, 1)
            elif symbol in ("AC", "DEL", "%", "±"):
                bg = (0.88, 0.89, 0.91, 1)
                fg = (0.20, 0.20, 0.20, 1)
            else:
                bg = (1, 1, 1, 1)
                fg = (0.10, 0.10, 0.10, 1)

            button = Button(
                text=symbol,
                font_size="25sp",
                background_normal="",
                background_down="",
                background_color=bg,
                color=fg
            )
            button.bind(on_press=self.press)
            grid.add_widget(button)

        root.add_widget(grid)
        return root

    def press(self, button):
        key = button.text

        if key == "AC":
            self.expression = ""

        elif key == "DEL":
            self.expression = self.expression[:-1]

        elif key == "±":
            match = re.search(r"(\d+(?:\.\d*)?|\.\d+)$",
                              self.expression)
            if match:
                start = match.start()
                number = match.group()
                before = self.expression[:start]
                if number.startswith("-"):
                    number = number[1:]
                else:
                    number = "-" + number
                self.expression = before + number
            elif not self.expression:
                self.expression = "-"

        elif key == "=":
            try:
                expr = self.expression
                expr = expr.replace("÷", "/")
                expr = expr.replace("×", "*")
                expr = expr.replace("−", "-")
                self.expression = calculate(expr)
            except ZeroDivisionError:
                self.expression = "Cannot divide by zero"
            except Exception:
                self.expression = "Error"

        elif key == "%":
            try:
                expr = self.expression
                expr = expr.replace("÷", "/")
                expr = expr.replace("×", "*")
                expr = expr.replace("−", "-")
                self.expression = str(
                    float(calculate(expr)) / 100
                )
            except Exception:
                self.expression = "Error"

        else:
            if self.expression in (
                "Error", "Cannot divide by zero"
            ):
                self.expression = ""

            if key == ".":
                last_number = re.split(
                    r"[+\-×÷%]", self.expression
                )[-1]
                if "." in last_number:
                    return

            self.expression += key

        self.display.text = self.expression or "0"


if __name__ == "__main__":
    RedmiCalculator().run()
