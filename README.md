# Compiler Construction - Lexer and LL(1) Parser

This project implements two core front-end compiler phases for a mini Python-like language:

- Lexical analysis (scanner): converts source text into a token stream
- Syntax analysis (table-driven LL(1) parser): validates token order and builds a parse tree

It is a compiler construction practice project focused on tokenization, grammar preparation,
FIRST/FOLLOW computation, predictive parsing table construction, and panic-mode recovery.

## Features

### Scanner

The scanner recognizes:

- Keywords: `if`, `else`, `while`
- Identifiers
- Numbers (integer and decimal forms)
- Double-quoted strings
- Operators: `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- Separators: `(`, `)`, `{`, `}`, `;`, `,`, `:`
- End-of-file token: `EOF`

Behavior notes:

- Line tracking is included for diagnostics.
- Unterminated strings raise a lexical error.
- Unknown single characters are emitted as `Unidentified` tokens.

### Parser

The parser is table-driven LL(1) (predictive, stack-based).

- Grammar start symbol: `<program>`
- Grammar preparation includes direct left-recursion elimination and left factoring.
- FIRST and FOLLOW sets are computed for all nonterminals.
- LL(1) parsing table is built and checked for conflicts.
- Parse tree is printed in an ASCII tree format.
- Panic-mode error recovery is used to continue after syntax errors.

## Project Structure

- `src/lexer.py` - `Scanner` implementation
- `src/parser.py` - parse tree node model, grammar utilities, LL(1) parser
- `src/tokens.py` - `Token` class and token category constants
- `src/main.py` - command-line entry point that runs scanner and parser
- `src/sample_code.mpy` - sample input program

## How To Run

1. Open a terminal in the project root.

Linux/macOS:

```bash
cd /your_project_path/compiler
```

Windows (PowerShell or Command Prompt):

```powershell
cd C:\path\to\compiler
```

2. (Optional) Create and activate a virtual environment.

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt (CMD):

```bat
python -m venv venv
venv\Scripts\activate.bat
```

3. Run with the default sample file:

```bash
python3 src/main.py
```

Windows:

```powershell
python src/main.py
```

4. Run with a custom input file:

```bash
python3 src/main.py path/to/your_input_file.mpy
```

Windows:

```powershell
python src/main.py path\to\your_input_file.mpy
```

## Runtime Output

The program prints several sections in order:

1. `---- Scanner Output ----`
2. Token table (`Line`, `Lexeme`, `Token`)
3. `----Parse Tree ----`
4. `---- FIRST Sets ----`
5. `---- FOLLOW Sets ----`
6. `---- LL(1) Parsing Table (filled entries) ----`
7. Parse tree and final parse status

Status messages:

- `SUCCESS: Input successfully parsed`
- or `PARSING COMPLETED WITH RECOVERY` followed by collected syntax issues

## Example Input

The included sample program in `src/sample_code.mpy` contains assignment, `while`, and `if/else` statements and is suitable for demonstrating both tokenization and parsing.

