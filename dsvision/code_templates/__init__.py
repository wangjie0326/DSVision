"""代码模板模块"""
from .cpp_templates import CODE_TEMPLATES, get_code_template, get_code_lines
from .python_templates import PYTHON_CODE_TEMPLATES, get_python_template
from .java_templates import JAVA_CODE_TEMPLATES, get_java_template

__all__ = [
    'CODE_TEMPLATES',
    'get_code_template',
    'get_code_lines',
    'PYTHON_CODE_TEMPLATES',
    'get_python_template',
    'JAVA_CODE_TEMPLATES',
    'get_java_template'
]
