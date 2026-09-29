"""林地面积导入模板生成模块（拆分后的同名包）。"""

from .generate_forest_template import generate_forest_template, FOREST_COLUMNS

__all__ = [
    "generate_forest_template",
    "FOREST_COLUMNS",
]
