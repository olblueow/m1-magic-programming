from compiler.lexer import Lexer
from compiler.translator import Translator
from compiler.generator import XMLGenerator

def main():
    # 1. This is your pure High-Level Python-like code!
    source_code = """
    # Allocation de la mémoire en blocs de 4-bits
    x = 5
    y = 2

    # Opérations mathématiques
    x += 1
    
    move(y, x)
    """

    print("🔧 Compiling Pure Python script to Magic Cards...")
    
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
    
    translator = Translator()
    decklist = translator.translate(tokens)
    
    XMLGenerator.build_cod_file(decklist, "data/python_compiled.cod", "Python Compiled Script")

if __name__ == "__main__":
    main()