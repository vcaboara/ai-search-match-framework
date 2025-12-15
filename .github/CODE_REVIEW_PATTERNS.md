# Code Review Anti-Patterns Guide

This guide documents common anti-patterns that AI code reviewers (GitHub Copilot, Ollama, etc.) should catch automatically during PR reviews. These patterns impact performance, code quality, and maintainability.

**Target Audience:** AI code reviewers, human reviewers, and developers
**Scope:** Python code in ASMF and downstream projects (ai-patent-eval, ai-grant-finder, etc.)

## Table of Contents

1. [Performance Anti-Patterns](#performance-anti-patterns)
2. [Code Quality Anti-Patterns](#code-quality-anti-patterns)
3. [Python-Specific Anti-Patterns](#python-specific-anti-patterns)
4. [Security Anti-Patterns](#security-anti-patterns)

---

## Performance Anti-Patterns

### 1. Regex Compilation Inside Loops

**Problem:** Compiling regex patterns repeatedly in loops wastes CPU cycles.

**Bad Example:**
```python
def process_documents(documents: list[str]) -> list[str]:
    results = []
    for doc in documents:
        # Compiles pattern on every iteration
        match = re.search(r'\b[A-Z]{2,}\b', doc)
        if match:
            results.append(match.group())
    return results
```

**Good Example:**
```python
# Compile once at module/class level
ACRONYM_PATTERN = re.compile(r'\b[A-Z]{2,}\b')

def process_documents(documents: list[str]) -> list[str]:
    results = []
    for doc in documents:
        match = ACRONYM_PATTERN.search(doc)
        if match:
            results.append(match.group())
    return results
```

**Rationale:** Regex compilation is expensive. Pre-compiling patterns at module or class level can improve performance by 10-100x in loops.

**Detection:** Look for `re.search()`, `re.match()`, `re.findall()`, `re.sub()` inside loop bodies.

---

### 2. Repeated Dictionary/List Lookups in Loops

**Problem:** Accessing the same dictionary or list element multiple times in a loop.

**Bad Example:**
```python
def calculate_scores(data: dict, items: list[str]) -> list[float]:
    scores = []
    for item in items:
        # Multiple lookups of data['weights']
        score = data['weights'][item] * data['weights']['multiplier']
        scores.append(score)
    return scores
```

**Good Example:**
```python
def calculate_scores(data: dict, items: list[str]) -> list[float]:
    scores = []
    weights = data['weights']  # Cache the lookup
    multiplier = weights['multiplier']
    for item in items:
        score = weights[item] * multiplier
        scores.append(score)
    return scores
```

**Rationale:** Dictionary lookups have O(1) average complexity but still involve hashing. Caching frequently accessed values reduces overhead.

**Detection:** Look for repeated `dict[key]` or `list[index]` accesses within loops where the key/index doesn't change.

---

### 3. String Concatenation in Loops

**Problem:** Using `+` or `+=` for string concatenation in loops creates intermediate string objects.

**Bad Example:**
```python
def format_results(items: list[str]) -> str:
    result = ""
    for item in items:
        result += f"{item}\n"  # Creates new string object each time
    return result
```

**Good Example:**
```python
def format_results(items: list[str]) -> str:
    # Use join() for efficient concatenation
    return "\n".join(items)

# Or if formatting is needed:
def format_results_with_prefix(items: list[str]) -> str:
    parts = [f"- {item}" for item in items]
    return "\n".join(parts)
```

**Rationale:** Strings are immutable in Python. Using `+=` in loops creates O(n²) string copies. `str.join()` is O(n).

**Detection:** Look for `string += ...` or `string = string + ...` inside loop bodies.

---

### 4. Repeated Function Calls with Same Arguments

**Problem:** Calling expensive functions repeatedly with identical arguments.

**Bad Example:**
```python
def process_data(items: list[dict], config_path: str) -> list[dict]:
    results = []
    for item in items:
        # load_config() called on every iteration
        config = load_config(config_path)
        processed = apply_config(item, config)
        results.append(processed)
    return results
```

**Good Example:**
```python
def process_data(items: list[dict], config_path: str) -> list[dict]:
    config = load_config(config_path)  # Call once
    results = []
    for item in items:
        processed = apply_config(item, config)
        results.append(processed)
    return results
```

**Rationale:** I/O operations, parsing, and heavy computations should be minimized. Cache results when inputs don't change.

**Detection:** Look for function calls inside loops where arguments are loop-invariant.

---

## Code Quality Anti-Patterns

### 5. Imports in Conditional Blocks

**Problem:** Placing imports inside if/else blocks or functions makes dependencies unclear.

**Bad Example:**
```python
def analyze_document(doc: str, use_ai: bool) -> dict:
    if use_ai:
        from asmf.providers import GeminiProvider  # Hidden dependency
        provider = GeminiProvider()
        return provider.analyze(doc)
    else:
        return basic_analysis(doc)
```

**Good Example:**
```python
from asmf.providers import GeminiProvider  # Clear dependency at top

def analyze_document(doc: str, use_ai: bool) -> dict:
    if use_ai:
        provider = GeminiProvider()
        return provider.analyze(doc)
    else:
        return basic_analysis(doc)
```

**Rationale:** PEP 8 requires imports at the top of the file. This makes dependencies explicit, easier to track, and prevents import-time side effects.

**Exception:** Lazy imports for optional dependencies or very heavy modules in CLI tools.

**Detection:** Look for `import` or `from ... import` statements inside function bodies or conditional blocks.

---

### 6. Deep Nesting (>3 Levels)

**Problem:** Deeply nested code is hard to read, test, and maintain.

**Bad Example:**
```python
def process_item(item: dict) -> dict | None:
    if item.get('enabled'):
        if item.get('data'):
            if item['data'].get('valid'):
                if item['data']['valid']:
                    result = transform(item['data'])
                    if result:
                        return result
    return None
```

**Good Example:**
```python
def process_item(item: dict) -> dict | None:
    # Early returns reduce nesting
    if not item.get('enabled'):
        return None
    
    if not item.get('data'):
        return None
    
    if not item['data'].get('valid'):
        return None
    
    result = transform(item['data'])
    return result if result else None
```

**Better Example (Extract Helper):**
```python
def is_valid_item(item: dict) -> bool:
    """Check if item is enabled and has valid data."""
    return (item.get('enabled') and 
            item.get('data') and 
            item['data'].get('valid'))

def process_item(item: dict) -> dict | None:
    if not is_valid_item(item):
        return None
    
    result = transform(item['data'])
    return result if result else None
```

**Rationale:** The Flake8 complexity checker flags functions with >3 nesting levels. Use early returns and extract helper methods.

**Detection:** Count indentation levels. Flag code blocks with >3 levels of nesting.

---

### 7. Bare Except Clauses

**Problem:** Catching all exceptions hides bugs and makes debugging difficult.

**Bad Example:**
```python
def load_data(filepath: str) -> dict:
    try:
        with open(filepath) as f:
            return json.load(f)
    except:  # Catches everything, including KeyboardInterrupt!
        return {}
```

**Good Example:**
```python
def load_data(filepath: str) -> dict:
    try:
        with open(filepath) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return {}
```

**Rationale:** Bare `except:` catches `SystemExit`, `KeyboardInterrupt`, and other critical exceptions. Always specify exception types.

**Detection:** Look for `except:` without an exception type.

---

### 8. Missing Error Handling in Type Conversions

**Problem:** Calling `int()`, `float()`, etc. without handling `ValueError`.

**Bad Example:**
```python
def parse_score(score_str: str) -> float:
    # Crashes if score_str is not a valid number
    return float(score_str)
```

**Good Example:**
```python
def parse_score(score_str: str) -> float | None:
    try:
        return float(score_str)
    except ValueError:
        logger.warning(f"Invalid score format: {score_str}")
        return None
```

**Better Example (with default):**
```python
def parse_score(score_str: str, default: float = 0.0) -> float:
    try:
        return float(score_str)
    except ValueError:
        logger.warning(f"Invalid score format: {score_str}, using default {default}")
        return default
```

**Rationale:** User input and external data are unreliable. Type conversions should always handle errors gracefully.

**Detection:** Look for `int()`, `float()`, `complex()` calls outside try/except blocks when processing external data.

---

### 9. Using Mutable Default Arguments

**Problem:** Mutable defaults (lists, dicts) are shared across function calls, causing unexpected behavior.

**Bad Example:**
```python
def add_item(item: str, items: list = []) -> list:
    items.append(item)  # Modifies the shared default list!
    return items

# Unexpected behavior:
result1 = add_item("a")  # ["a"]
result2 = add_item("b")  # ["a", "b"] - shares the same list!
```

**Good Example:**
```python
def add_item(item: str, items: list | None = None) -> list:
    if items is None:
        items = []
    items.append(item)
    return items

# Or use immutable default:
def add_item(item: str, items: tuple[str, ...] = ()) -> list:
    result = list(items)
    result.append(item)
    return result
```

**Rationale:** Default arguments are evaluated once at function definition time. Mutable defaults persist across calls.

**Detection:** Look for function signatures with `= []`, `= {}`, or `= set()` as defaults.

---

### 10. Silent Exception Handling

**Problem:** Catching exceptions without logging or re-raising.

**Bad Example:**
```python
def fetch_data(url: str) -> dict:
    try:
        response = requests.get(url)
        return response.json()
    except Exception:
        return {}  # Silently fails - no indication of what went wrong
```

**Good Example:**
```python
def fetch_data(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from {url}: {e}")
        return {}
```

**Rationale:** Silent failures make debugging impossible. Always log errors with context before swallowing exceptions.

**Detection:** Look for `except:` or `except Exception:` blocks that don't log, re-raise, or have explanatory comments.

---

## Python-Specific Anti-Patterns

### 11. List Comprehension with Exception Handling

**Problem:** Embedding try/except in list comprehensions reduces readability.

**Bad Example:**
```python
def parse_numbers(strings: list[str]) -> list[int]:
    # Hard to read and maintain
    return [int(s) if s.isdigit() else 0 for s in strings]

# Even worse:
def risky_parse(strings: list[str]) -> list[int]:
    # This won't work - try/except not allowed in list comp
    return [try_parse(s) for s in strings]  # Need try_parse wrapper
```

**Good Example:**
```python
def parse_numbers(strings: list[str]) -> list[int]:
    results = []
    for s in strings:
        try:
            results.append(int(s))
        except ValueError:
            results.append(0)
    return results

# Or with a helper function:
def safe_int(s: str, default: int = 0) -> int:
    try:
        return int(s)
    except ValueError:
        return default

def parse_numbers(strings: list[str]) -> list[int]:
    return [safe_int(s) for s in strings]
```

**Rationale:** List comprehensions should be simple and readable. Complex logic with error handling belongs in explicit loops or helper functions.

**Detection:** Look for complex conditional logic or nested function calls with error handling needs in list comprehensions.

---

### 12. Using `assert` for Data Validation

**Problem:** `assert` statements can be disabled with Python's `-O` flag and shouldn't be used for runtime validation.

**Bad Example:**
```python
def process_payment(amount: float) -> None:
    assert amount > 0, "Amount must be positive"  # Disabled in production!
    charge_card(amount)
```

**Good Example:**
```python
def process_payment(amount: float) -> None:
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")
    charge_card(amount)
```

**Rationale:** Assertions are for debugging and testing invariants, not for validating user input or external data.

**Detection:** Look for `assert` statements that validate function arguments or external data.

---

### 13. Not Using Context Managers for Resources

**Problem:** Forgetting to close files, connections, or other resources.

**Bad Example:**
```python
def read_file(filepath: str) -> str:
    f = open(filepath)
    content = f.read()
    f.close()  # Skipped if read() raises an exception!
    return content
```

**Good Example:**
```python
def read_file(filepath: str) -> str:
    with open(filepath) as f:
        return f.read()
```

**Rationale:** Context managers (`with` statement) guarantee cleanup even if exceptions occur.

**Detection:** Look for `open()`, database connections, or lock acquisitions without `with` statements.

---

### 14. String Formatting with `%` or `.format()` in Logs

**Problem:** Eagerly formatting log strings wastes CPU when logging is disabled.

**Bad Example:**
```python
def process_item(item: dict) -> None:
    # String formatted even if DEBUG is disabled
    logger.debug(f"Processing item: {expensive_repr(item)}")
```

**Good Example:**
```python
def process_item(item: dict) -> None:
    # Lazy formatting - only evaluated if DEBUG enabled
    logger.debug("Processing item: %s", item)
```

**Rationale:** Modern logging libraries support lazy evaluation. The string is only formatted if the log level is active.

**Detection:** Look for f-strings or `.format()` in `logger.debug()` calls.

---

## Security Anti-Patterns

### 15. SQL Injection via String Formatting

**Problem:** Building SQL queries with string formatting allows SQL injection attacks.

**Bad Example:**
```python
def get_user(username: str) -> dict:
    # SQL injection vulnerability!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)
```

**Good Example:**
```python
def get_user(username: str) -> dict:
    # Parameterized query prevents injection
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))
```

**Rationale:** Never trust user input. Use parameterized queries or ORM methods to prevent SQL injection.

**Detection:** Look for SQL keywords (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) in f-strings or `.format()` calls.

---

### 16. Unsafe Deserialization

**Problem:** Using `pickle.load()` or `eval()` on untrusted data allows arbitrary code execution.

**Bad Example:**
```python
def load_user_data(data: bytes) -> dict:
    # Arbitrary code execution vulnerability!
    return pickle.loads(data)
```

**Good Example:**
```python
def load_user_data(data: str) -> dict:
    # Use safe serialization formats
    return json.loads(data)
```

**Rationale:** `pickle`, `eval()`, and `exec()` can execute arbitrary code. Use JSON, YAML (with safe loaders), or other safe formats.

**Detection:** Look for `pickle.load()`, `eval()`, `exec()` calls on external data.

---

### 17. Hardcoded Credentials

**Problem:** Embedding API keys, passwords, or secrets in source code.

**Bad Example:**
```python
def connect_to_api() -> Client:
    api_key = "sk-1234567890abcdef"  # Hardcoded secret!
    return Client(api_key=api_key)
```

**Good Example:**
```python
import os

def connect_to_api() -> Client:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable not set")
    return Client(api_key=api_key)
```

**Rationale:** Secrets in source code can be leaked via version control, logs, or error messages. Use environment variables or secret managers.

**Detection:** Look for suspicious string patterns like `api_key = "..."`, `password = "..."`, or strings matching API key formats.

---

### 18. Path Traversal Vulnerabilities

**Problem:** Not validating user-provided file paths allows access to arbitrary files.

**Bad Example:**
```python
def read_user_file(filename: str) -> str:
    # Can access ../../../etc/passwd
    path = f"/app/uploads/{filename}"
    with open(path) as f:
        return f.read()
```

**Good Example:**
```python
from pathlib import Path

def read_user_file(filename: str) -> str:
    # Validate and normalize the path
    base_dir = Path("/app/uploads")
    file_path = (base_dir / filename).resolve()
    
    # Ensure the resolved path is still within base_dir
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Invalid file path")
    
    with open(file_path) as f:
        return f.read()
```

**Rationale:** User input can contain `..` or absolute paths. Always validate that paths stay within expected directories.

**Detection:** Look for file operations with user-provided paths that don't validate or normalize the path.

---

## Review Checklist

When reviewing code, check for:

### Performance
- [ ] Are regex patterns compiled outside loops?
- [ ] Are repeated dict/list lookups cached?
- [ ] Is `str.join()` used instead of `+=` in loops?
- [ ] Are expensive function calls moved outside loops?

### Code Quality
- [ ] Are all imports at the top of the file?
- [ ] Is nesting depth ≤3 levels?
- [ ] Are specific exceptions caught instead of bare `except:`?
- [ ] Do type conversions have error handling?
- [ ] Are mutable defaults avoided in function signatures?
- [ ] Are exceptions logged before being swallowed?

### Python-Specific
- [ ] Are list comprehensions kept simple?
- [ ] Is `raise ValueError` used instead of `assert` for validation?
- [ ] Are resources managed with `with` statements?
- [ ] Are log strings using lazy formatting?

### Security
- [ ] Are SQL queries parameterized?
- [ ] Is untrusted data never passed to `pickle`, `eval()`, or `exec()`?
- [ ] Are credentials loaded from environment variables?
- [ ] Are file paths validated to prevent traversal?

---

## References

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Anti-Patterns](https://docs.quantifiedcode.com/python-anti-patterns/)
- [Effective Python: 90 Specific Ways to Write Better Python](https://effectivepython.com/)

---

## Contributing

Found a new anti-pattern? Submit a PR with:
1. Clear bad and good examples
2. Rationale explaining the impact
3. Detection guidance for reviewers
4. Category assignment (performance/quality/security)

Patterns should be:
- **Common**: Appears in real PRs
- **Actionable**: Clear fix available
- **Impactful**: Measurable effect on code quality or performance
