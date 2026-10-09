import akshare as ak
import pandas as pd
import time
import sys

def get_all_stocks(max_retries=3, wait_seconds=10):
    """获取全市场A股实时行情，带自动重试"""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[尝试 {attempt}/{max_retries}] 正在获取全市场股票数据...")
            df = ak.stock_zh_a_spot_em()
            print(f"成功获取 {len(df)} 只股票数据")
            return df
        except Exception as e:
            print(f"第 {attempt} 次获取失败：{e}")
            if attempt < max_retries:
                print(f"等待 {wait_seconds} 秒后重试...")
                time.sleep(wait_seconds)
            else:
                print("\n连续多次获取失败，可能原因：")
                print("1. 数据源临时限流（等 5-10 分钟再试）")
                print("2. 网络代理/防火墙干扰（检查是否开了VPN）")
                print("3. akshare 版本过旧（运行 pip install --upgrade akshare）")
                sys.exit(1)

def screen_stocks(df):
    """多因子筛选器"""
    print("正在筛选股票...")
    
    numeric_cols = ['成交额', '涨跌幅', '换手率']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    selected = df[
        (df['成交额'] > 5e8) &
        (df['涨跌幅'] > 2) & (df['涨跌幅'] < 9.8) &
        (df['换手率'] > 2) & (df['换手率'] < 20)
    ].copy()
    
    selected = selected[~selected['名称'].str.contains('ST|退', na=False)]
    selected = selected.sort_values('成交额', ascending=False)
    
    print(f"筛选完成，共选出 {len(selected)} 只股票")
    return selected

def save_results(selected, filename='candidates.txt'):
    """保存筛选结果"""
    with open(filename, 'w', encoding='utf-8') as f:
        for code in selected['代码'].tolist():
            f.write(f"{code}\n")
    print(f"候选股票代码已保存到 {filename}")
    
    selected.to_csv('candidates_detail.csv', index=False, encoding='utf-8-sig')
    print("详细信息已保存到 candidates_detail.csv")

if __name__ == '__main__':
    df = get_all_stocks()
    selected = screen_stocks(df)
    save_results(selected)
    
    print("\n=== 候选股票列表（前20只）===")
    print(selected[['代码', '名称', '最新价', '涨跌幅', '成交额', '换手率']].head(20).to_string())