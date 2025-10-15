# File: tools/py-shroud/py_shroud_tool/obfuscators/name_mangler.py
# Description: An AST transformer to rename variables, functions, and classes.

import ast

class NameMangler(ast.NodeTransformer):
    """Traverses the AST and renames identifiers to obscure, hard-to-read names."""
    def __init__(self):
        super().__init__()
        self.name_map = {}
        self._mangle_count = 0
        self._builtins = set(dir(__builtins__))

    def _get_mangled_name(self, original_name: str) -> str:
        """Generates or retrieves a mangled name."""
        if original_name in self._builtins or (original_name.startswith('__') and original_name.endswith('__')):
            return original_name
        
        if original_name not in self.name_map:
            # Generate a new name like 'O', 'I', 'O0', 'OI', 'IO', 'II', 'OO0', ...
            # This is harder to read than simple hex.
            mangled = ""
            n = self._mangle_count
            while True:
                mangled = ('O' if n % 2 == 0 else 'I') + mangled
                n //= 2
                if n == 0: break
            
            self.name_map[original_name] = f"_{mangled}"
            self._mangle_count += 1
        
        return self.name_map[original_name]

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Called for variable names."""
        if isinstance(node.ctx, (ast.Store, ast.Load, ast.Del)):
            node.id = self._get_mangled_name(node.id)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Called for function definitions."""
        node.name = self._get_mangled_name(node.name)
        self.generic_visit(node)
        return node
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Called for async function definitions."""
        node.name = self._get_mangled_name(node.name)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Called for class definitions."""
        node.name = self._get_mangled_name(node.name)
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        """Called for function arguments."""
        node.arg = self._get_mangled_name(node.arg)
        return node

    def visit_keyword(self, node: ast.keyword) -> ast.keyword:
        """Called for keyword arguments in function calls (e.g., func(name='value'))."""
        # We don't mangle the keyword name itself, as it might be part of an external API.
        # But we must visit the value associated with the keyword.
        node.value = self.visit(node.value)
        return node