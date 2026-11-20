"""原模块的模块级常量。"""
from ._imports import *

FIELD_OPTIONS = [
    ('', '不填写'),
    ('name', '姓名'),
    ('id_card', '身份证号'),
    ('hu_hao', '户号'),
    ('age', '年龄'),
    ('phone', '电话'),
    ('address', '地址'),
    ('group_name', '小组'),
    ('relation', '与户主关系'),
    ('is_dead', '是否死亡'),
    ('remark', '备注'),
    ('poor_type', '困难类型'),
    ('disability', '是否残疾'),
    ('disability_type', '残疾类型'),
    ('dis_level', '残疾等级'),
    ('dibao', '低保'),
    ('tekun', '特困'),
    ('tekun_type', '特困类型'),
    ('jisheng', '计生'),
    ('social_card1', '社保卡1'),
    ('social_card2', '社保卡2'),
    ('social_card3', '社保卡3'),
    ('social_card2_source', '社保卡2来源'),
    ('social_card3_source', '社保卡3来源'),
    ('is_migrated', '是否迁移'),
    ('migration_date', '迁移日期'),
    ('migration_place', '迁移地点'),
    ('migration_reason', '迁移原因'),
    ('updated_at', '更新时间'),
    ('land_area', '土地面积'),
    ('land_area_change_reason', '土地面积变更原因'),
    ('land_area_change_time', '土地面积变更时间'),
    ('local_welfare_forest_area', '地方公益林面积'),
    ('local_welfare_forest_change_reason', '地方公益林变更原因'),
    ('local_welfare_forest_change_time', '地方公益林变更时间'),
    ('national_welfare_forest_area', '国家公益林面积'),
    ('national_welfare_forest_change_reason', '国家公益林变更原因'),
    ('national_welfare_forest_change_time', '国家公益林变更时间'),
    ('commercial_forest_area', '非国有天然商品林面积'),
    ('commercial_forest_change_reason', '非国有天然商品林变更原因'),
    ('commercial_forest_change_time', '非国有天然商品林变更时间'),
]

MATCH_BY_NAME = 'name'

MATCH_BY_ID_CARD = 'id_card'

__all__ = ['FIELD_OPTIONS', 'MATCH_BY_NAME', 'MATCH_BY_ID_CARD']
