import os
import csv


def compare_csv_headers_detail(dir1, dir2):
    files1 = sorted([f for f in os.listdir(dir1) if f.endswith('.csv')])
    files2 = sorted([f for f in os.listdir(dir2) if f.endswith('.csv')])

    min_count = min(len(files1), len(files2))

    print(f"{'序号':<4} | {'文件名':<40} | {'比对结果'}")
    print("-" * 100)

    for i in range(min_count):
        file1_path = os.path.join(dir1, files1[i])
        file2_path = os.path.join(dir2, files2[i])

        # 尝试常见编码，防止中文乱码导致比对失败
        try:
            # 建议先尝试 utf-8-sig (自动处理BOM)，再尝试 gbk
            with open(file1_path, mode='r', encoding='utf-8-sig') as f1, \
                    open(file2_path, mode='r', encoding='utf-8-sig') as f2:

                reader1 = csv.reader(f1)
                reader2 = csv.reader(f2)

                # 获取表头并去除每个字段前后的空格
                h1 = [col.strip() for col in next(reader1, [])]
                h2 = [col.strip() for col in next(reader2, [])]

                if h1 == h2:
                    print(f"{i + 1:<4} | {files1[i]:<40} | ✅ 完全一致")
                else:
                    print(f"{i + 1:<4} | {files1[i]:<40} | ❌ 不一致")

                    # 找出具体的列差异
                    only_in_1 = [col for col in h1 if col not in h2]
                    only_in_2 = [col for col in h2 if col not in h1]

                    if only_in_1:
                        print(f"      [!] 文件夹1 特有: {only_in_1}")
                    if only_in_2:
                        print(f"      [!] 文件夹2 特有: {only_in_2}")

                    if len(h1) == len(h2) and h1 != h2:
                        print(f"      [!] 提示: 列数相同但顺序不同或名称有细微差异")
                        for idx, (c1, c2) in enumerate(zip(h1, h2)):
                            if c1 != c2:
                                print(f"          第 {idx + 1} 列: '{c1}' vs '{c2}'")
                    print("-" * 60)

        except Exception as e:
            print(f"{i + 1:<4} | {files1[i]:<40} | ⚠️ 读取出错: {e}")

# --- 使用示例 ---
path_a = r'D:\Users\23093\OneDrive\benliu_computer\1.工作\6.云南电网\新型台区计量终端表计的风险预测与动态运维技术研究\9.系统所需数据\系统验收后数据扩充\outputs\electric_meter_data'
path_b = r'D:\Users\23093\OneDrive\benliu_computer\1.工作\6.云南电网\新型台区计量终端表计的风险预测与动态运维技术研究\9.系统所需数据\系统验收后数据扩充\csv(2)'
compare_csv_headers_detail(path_a, path_b)