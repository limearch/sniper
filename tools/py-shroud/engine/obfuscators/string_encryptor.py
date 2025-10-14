# File: tools/py-shroud/engine/obfuscators/string_encryptor.py (Final Architectural Fix v2)
import ast
import base64

class StringEncryptor(ast.NodeTransformer):
    """
    Traverses the AST to replace string constants and injects its own
    decryption function at the top of the module to ensure it's defined first.
    """
    def __init__(self):
        super().__init__()
        self.string_count = 0

    def get_decryptor_node(self) -> ast.AST:
        """Generates the AST node for the decryption function."""
        decryptor_code = "import base64; _d = lambda s: base64.b64decode(s).decode('utf-8')"
        return ast.parse(decryptor_code).body[0]

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """
        Called once for the entire file. Injects the decryption function
        after all other transformations are complete.
        """
        self.generic_visit(node)
        if self.string_count > 0:
            node.body.insert(0, self.get_decryptor_node())
        return node

    # --- START: THE FINAL, CORRECT FIX FOR F-STRINGS ---
    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.JoinedStr:
        """
        Custom visitor for f-strings (JoinedStr).
        We must recursively visit the expressions inside the f-string
        (e.g., the 'name' in f"Hello {name}") but we must explicitly
        SKIP transforming the literal string parts.
        """
        # The 'values' attribute is a list of Constant (string part) and
        # FormattedValue (expression part) nodes.
        for child_node in node.values:
            # We ONLY visit the FormattedValue nodes, which contain the expressions.
            if isinstance(child_node, ast.FormattedValue):
                # The 'visit' method will correctly traverse inside the expression.
                self.visit(child_node)
        
        # By not calling generic_visit and not visiting the Constant nodes
        # in the 'values' list, we prevent their encryption.
        # We return the node itself, with its inner expressions potentially transformed.
        return node
    # --- END: THE FINAL, CORRECT FIX ---

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        """
        This method is called for every 'Constant' node in the AST.
        It will now be correctly skipped for constants that are part of an f-string.
        """
        if isinstance(node.value, str) and node.value:
            self.string_count += 1
            
            original_bytes = node.value.encode('utf-8')
            encoded_bytes = base64.b64encode(original_bytes)
            
            new_node = ast.Call(
                func=ast.Name(id='_d', ctx=ast.Load()),
                args=[ast.Constant(value=encoded_bytes)],
                keywords=[]
            )
            return ast.copy_location(new_node, node)
            
        return node