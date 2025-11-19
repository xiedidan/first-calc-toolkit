"""
测试导出API的文件名编码
"""
from urllib.parse import quote

# 测试中文文件名编码
filename = "科室业务价值汇总_2025-10.xlsx"
encoded_filename = quote(filename)

print(f"原始文件名: {filename}")
print(f"编码后: {encoded_filename}")
print(f"\nContent-Disposition header:")
print(f"attachment; filename*=UTF-8''{encoded_filename}")
