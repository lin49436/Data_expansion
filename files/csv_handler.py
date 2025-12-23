#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV文件操作模块
处理CSV文件的读写操作
"""

import csv
import os
from config import OUTPUT_DIR


def write_csv(filename, data, headers, comments):
    """
    写入CSV文件,包含字段名(英文)和注释(中文)
    
    Args:
        filename: 文件名
        data: 数据列表
        headers: 字段名列表
        comments: 字段注释字典
    """
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # 写入英文字段名
        writer.writeheader()
        
        # 写入中文注释
        comment_row = {header: comments.get(header, '') for header in headers}
        writer.writerow(comment_row)
        
        # 写入数据
        writer.writerows(data)
    
    print(f"已生成文件: {filename}, 记录数: {len(data)}")
