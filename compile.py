from compiler.lexer import Lexer
from compiler.translator import Translator
from compiler.generator import XMLGenerator

def main():
    source_code = """
    x = 5
    y = 2

    x += 1     # x devient 6
    y += 5     # y devient 7
    y -= 2     # y re-devient 5
    x *= 2     # x devient 12
    x = 1 * 2  # x est écrasé et devient 2
    """

    
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
    
    translator = Translator()
    decklist = translator.translate(tokens)
    
    XMLGenerator.build_cod_file(decklist, "data/python_compiled.cod", "Python Compiled Script")

if __name__ == "__main__":
    main()