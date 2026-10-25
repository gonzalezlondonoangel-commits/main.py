
# CLASSNOTE
# Aplicación matemática creada por Ángel
# Python + Kivy para Pydroid 3

import ast
import math
import operator as op
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# COLORES DE CLASSNOTE
AZUL = (0.02, 0.16, 0.95, 1)
AZUL_VIVO = (0, 0.35, 1, 1)
AMARILLO = (1, 0.88, 0.05, 1)
ROJO = (0.95, 0.04, 0.08, 1)
NEGRO = (0.025, 0.025, 0.04, 1)
BLANCO = (1, 1, 1, 1)
GRIS = (0.8, 0.8, 0.8, 1)

# OPERACIONES PERMITIDAS
OPERACIONES = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}

UNARIAS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
    ast.Not: op.not_,
}

COMPARACIONES = {
    ast.Eq: op.eq,
    ast.NotEq: op.ne,
    ast.Lt: op.lt,
    ast.LtE: op.le,
    ast.Gt: op.gt,
    ast.GtE: op.ge,
}


def promedio(*numeros):
    if not numeros:
        raise ValueError("Escribe los números del promedio.")
    return sum(numeros) / len(numeros)


def porcentaje(porcentaje, cantidad):
    return porcentaje * cantidad / 100


FUNCIONES = {
    "raiz": math.sqrt,
    "sqrt": math.sqrt,
    "abs": abs,
    "promedio": promedio,
    "prom": promedio,
    "porcentaje": porcentaje,
}


def preparar(texto):
    texto = texto.strip().lower()

    texto = texto.replace("×", "*")
    texto = texto.replace("÷", "/")
    texto = texto.replace("−", "-")
    texto = texto.replace("^", "**")

    texto = re.sub(r"\bverdadero\b", "True", texto)
    texto = re.sub(r"\bfalso\b", "False", texto)

    # 20% se convierte en 20/100
    texto = re.sub(
        r"(?<![\w.])(\d+(?:\.\d+)?)\s*%",
        r"(\1/100)",
        texto
    )

    # Multiplicación implícita: 5(7), (2+3)(4)
    texto = re.sub(r"(\d|\))\s*\(", r"\1*(", texto)

    return texto


def evaluar(nodo):
    if isinstance(nodo, ast.Expression):
        return evaluar(nodo.body)

    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, (int, float, bool)):
            return nodo.value

    if isinstance(nodo, ast.Num):
        return nodo.n

    if isinstance(nodo, ast.BinOp):
        tipo = type(nodo.op)

        if tipo not in OPERACIONES:
            raise ValueError("Operación no permitida.")

        izquierda = evaluar(nodo.left)
        derecha = evaluar(nodo.right)

        if isinstance(nodo.op, ast.Div) and derecha == 0:
            raise ZeroDivisionError(
                "No se puede dividir entre cero."
            )

        if isinstance(nodo.op, ast.Pow) and abs(derecha) > 1000:
            raise ValueError("Exponente demasiado grande.")

        resultado = OPERACIONES[tipo](izquierda, derecha)

        if isinstance(resultado, complex):
            raise ValueError("Resultado complejo no admitido.")

        if isinstance(resultado, float) and not math.isfinite(resultado):
            raise ValueError("Resultado fuera de rango.")

        return resultado

    if isinstance(nodo, ast.UnaryOp):
        tipo = type(nodo.op)

        if tipo not in UNARIAS:
            raise ValueError("Operación no permitida.")

        return UNARIAS[tipo](evaluar(nodo.operand))

    if isinstance(nodo, ast.BoolOp):
        if isinstance(nodo.op, ast.And):
            resultado = True

            for valor in nodo.values:
                resultado = evaluar(valor)

                if not resultado:
                    return resultado

            return resultado

        if isinstance(nodo.op, ast.Or):
            resultado = False

            for valor in nodo.values:
                resultado = evaluar(valor)

                if resultado:
                    return resultado

            return resultado

    if isinstance(nodo, ast.Compare):
        izquierda = evaluar(nodo.left)

        for operador, comparador in zip(
            nodo.ops, nodo.comparators
        ):
            derecha = evaluar(comparador)
            tipo = type(operador)

            if tipo not in COMPARACIONES:
                raise ValueError("Comparación no permitida.")

            if not COMPARACIONES[tipo](izquierda, derecha):
                return False

            izquierda = derecha

        return True

    if isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name):
            raise ValueError("Función no permitida.")

        nombre = nodo.func.id.lower()

        if nombre not in FUNCIONES:
            raise ValueError("Función desconocida.")

        if nodo.keywords:
            raise ValueError("Usa argumentos separados por comas.")

        argumentos = [evaluar(a) for a in nodo.args]

        return FUNCIONES[nombre](*argumentos)

    if isinstance(nodo, ast.Name):
        if nodo.id in ("True", "true"):
            return True

        if nodo.id in ("False", "false"):
            return False

    raise ValueError("Revisa la expresión matemática.")


def calcular(expresion):
    expresion = preparar(expresion)
    arbol = ast.parse(expresion, mode="eval")
    return evaluar(arbol)


# BOTONES PERSONALIZADOS
class Tecla(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = NEGRO
        self.color = AMARILLO
        self.bold = True
        self.font_size = "19sp"

        with self.canvas.after:
            Color(*ROJO)
            self.borde = Line(
                rectangle=(
                    self.x, self.y,
                    self.width, self.height
                ),
                width=1.5
            )

        self.bind(
            pos=self.actualizar_borde,
            size=self.actualizar_borde
        )

    def actualizar_borde(self, *args):
        self.borde.rectangle = (
            self.x, self.y, self.width, self.height
        )


# APLICACIÓN PRINCIPAL
class CLASSNOTE(App):

    title = "CLASSNOTE"

    def build(self):
        Window.clearcolor = AZUL
        Window.softinput_mode = "below_target"

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        # ENCABEZADO Y LOGO
        encabezado = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10)
        )

        logo = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(90),
            padding=dp(3)
        )

        with logo.canvas.before:
            Color(*ROJO)
            logo.fondo = RoundedRectangle(
                pos=logo.pos,
                size=logo.size,
                radius=[dp(10)]
            )

        logo.bind(
            pos=lambda w, p: setattr(w.fondo, "pos", p),
            size=lambda w, s: setattr(w.fondo, "size", s)
        )

        logo.add_widget(Label(
            text="[b]A[/b]",
            markup=True,
            color=AZUL_VIVO,
            font_size="42sp"
        ))

        logo.add_widget(Label(
            text="[b]+[/b]",
            markup=True,
            color=BLANCO,
            font_size="34sp"
        ))

        encabezado.add_widget(logo)

        bienvenida = Label(
            text=(
                "[b]CLASSNOTE[/b]\n"
                "Adelante, bienvenido a CLASSNOTE, "
                "una app matemática hecha con dedicación "
                "por Ángel para el cálculo de tus problemas."
            ),
            markup=True,
            color=AMARILLO,
            font_size="14sp",
            halign="left",
            valign="middle"
        )

        bienvenida.bind(
            size=lambda w, s: setattr(w, "text_size", s)
        )

        encabezado.add_widget(bienvenida)
        principal.add_widget(encabezado)

        # PANTALLA DE EXPRESIONES
        self.entrada = TextInput(
            hint_text="Ingrese amablemente tu número o expresión...",
            multiline=False,
            size_hint_y=None,
            height=dp(58),
            font_size="20sp",
            background_normal="",
            background_active="",
            background_color=NEGRO,
            foreground_color=AMARILLO,
            cursor_color=BLANCO,
            hint_text_color=GRIS,
            padding=[dp(10), dp(14), dp(10), dp(10)]
        )

        principal.add_widget(self.entrada)

        self.resultado = Label(
            text="Resultado: listo para calcular",
            color=AMARILLO,
            font_size="18sp",
            size_hint_y=None,
            height=dp(45),
            halign="left",
            valign="middle"
        )

        self.resultado.bind(
            size=lambda w, s: setattr(w, "text_size", s)
        )

        principal.add_widget(self.resultado)

        # TECLADO MATEMÁTICO
        desplazamiento = ScrollView(
            do_scroll_x=False
        )

        teclado = GridLayout(
            cols=4,
            spacing=dp(6),
            padding=dp(2),
            size_hint_y=None
        )

        teclado.bind(
            minimum_height=teclado.setter("height")
        )

        filas = [
            ["AC", "DEL", "(", ")"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["0", ".", "%", "+"],
            ["^", "√", "=", "-"],
            ["and", "or", "not", "*"],
            [">", "<", ">=", "<="],
            ["==", "!=", "**", "/"],
        ]

        for fila in filas:
            for simbolo in fila:
                boton = Tecla(
                    text=simbolo,
                    size_hint_y=None,
                    height=dp(52)
                )

                if simbolo == "=":
                    boton.background_color = (
                        0.02, 0.30, 0.08, 1
                    )
                    boton.color = BLANCO

                if simbolo in ("AC", "DEL"):
                    boton.color = BLANCO

                boton.bind(
                    on_release=lambda instancia, valor=simbolo:
                    self.pulsar(valor)
                )

                teclado.add_widget(boton)

        desplazamiento.add_widget(teclado)
        principal.add_widget(desplazamiento)

        # FUNCIONES EXTRA
        principal.add_widget(Label(
            text="[b]FUNCIONES MATEMÁTICAS[/b]",
            markup=True,
            color=BLANCO,
            size_hint_y=None,
            height=dp(30)
        ))

        extras = GridLayout(
            cols=2,
            spacing=dp(6),
            size_hint_y=None,
            height=dp(100)
        )

        opciones = [
            ("Promedio", "promedio("),
            ("Raíz", "raiz("),
            ("% de cantidad", "porcentaje("),
            ("Limpiar", "AC"),
        ]

        for nombre, valor in opciones:
            boton = Tecla(
                text=nombre,
                font_size="15sp",
                size_hint_y=None,
                height=dp(46)
            )

            boton.bind(
                on_release=lambda instancia, v=valor:
                self.funcion_extra(v)
            )

            extras.add_widget(boton)

        principal.add_widget(extras)

        principal.add_widget(Label(
            text=(
                "Ej.: 5(7) | 2+(4*7)/8 | 2^5 | "
                "raiz(81) | promedio(5,7,9)"
            ),
            color=BLANCO,
            font_size="11sp",
            size_hint_y=None,
            height=dp(32)
        ))

        return principal

    # INSERTAR TEXTO EN LA PANTALLA
    def insertar(self, texto):
        self.entrada.text += texto
        self.entrada.focus = True

    # ACCIONES DEL TECLADO
    def pulsar(self, tecla):

        if tecla == "AC":
            self.entrada.text = ""
            self.resultado.text = "Resultado: listo para calcular"

        elif tecla == "DEL":
            self.entrada.text = self.entrada.text[:-1]

        elif tecla == "=":
            self.resolver()

        elif tecla == "√":
            self.insertar("raiz(")

        else:
            conversiones = {
                "×": "*",
                "÷": "/",
                "−": "-"
            }

            self.insertar(
                conversiones.get(tecla, tecla)
            )

    def funcion_extra(self, funcion):

        if funcion == "AC":
            self.pulsar("AC")
        else:
            self.insertar(funcion)

    # CALCULAR RESULTADO
    def resolver(self):
        expresion = self.entrada.text.strip()

        if not expresion:
            self.resultado.text = (
                "Ingrese amablemente tu número o expresión."
            )
            return

        try:
            valor = calcular(expresion)

            if (
                isinstance(valor, float)
                and math.isfinite(valor)
                and valor.is_integer()
            ):
                valor = int(valor)

            self.resultado.text = "Resultado: " + str(valor)

            # print() muestra el cálculo en la consola de Pydroid.
            print("CLASSNOTE:", expresion, "=", valor)

        except ZeroDivisionError:
            self.resultado.text = (
                "Error: no se puede dividir entre cero."
            )

        except Exception as error:
            self.resultado.text = (
                "Revisa la expresión: " + str(error)
            )


if __name__ == "__main__":
    CLASSNOTE().run()
