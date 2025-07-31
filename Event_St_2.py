import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================== 配置区 ==================
DATA_FILE = "party_activity.csv"
VIEWER_PASSWORD = "666666"  # 查看和管理数据的密码（建议后续用 st.secrets）

# ================== 数据读写函数（防乱码）==================
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, encoding='utf-8-sig')
    else:
        return pd.DataFrame(columns=["姓名", "所属部门", "交通方式", "提交时间"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# ================== 确保数据文件存在 ==================
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["姓名", "所属部门", "交通方式", "提交时间"])
    save_data(df_init)

# ================== 页面标题 ==================
st.title("📊 技术党支部实践活动参与统计")

# ================== 填写表单区域（所有人可见，无需密码）==================
st.subheader("📝 请参与党员填写信息")

# 加载当前数据（用于防重）
df = load_data()
existing_names = df["姓名"].str.strip().tolist()

with st.form(key="participant_form", clear_on_submit=True):
    name = st.text_input("姓名", placeholder="请输入您的真实姓名")
    department = st.text_input("所属部门", placeholder="例如：前端组、后端组")
    transport = st.radio("交通方式", ["自行驾车", "乘坐统一交通工具"])
    submitted = st.form_submit_button("提交")

if submitted:
    name_clean = name.strip()
    dept_clean = department.strip()

    if not name_clean or not dept_clean:
        st.error("姓名和所属部门不能为空！")
    elif name_clean in existing_names:
        st.warning(f"⚠️ {name_clean} 已提交过，不可重复填写！")
    else:
        new_record = pd.DataFrame([{
            "姓名": name_clean,
            "所属部门": dept_clean,
            "交通方式": transport,
            "提交时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        df_updated = pd.concat([df, new_record], ignore_index=True)
        save_data(df_updated)
        st.success(f"✅ 提交成功！感谢 {name_clean} 的参与！")
        st.balloons()
        st.rerun()  # 刷新以更新数据

st.markdown("---")

# ================== 查看与管理区域（需密码）==================
st.subheader("🔐 查看与管理参与情况（需登录）")

# 使用 session_state 保存登录状态
if 'view_authenticated' not in st.session_state:
    st.session_state.view_authenticated = False

if not st.session_state.view_authenticated:
    pwd = st.text_input("请输入查看密码", type="password")
    if st.button("验证密码"):
        if pwd == VIEWER_PASSWORD:
            st.session_state.view_authenticated = True
            st.success("密码正确，正在加载数据...")
            st.rerun()
        else:
            st.error("密码错误！")
else:
    st.success("✅ 已登录，可查看和管理数据")

    # 显示当前数据
    df = load_data()
    st.write(f"📊 当前共 {len(df)} 人参与")

    if len(df) == 0:
        st.info("暂无提交记录")
    else:
        # 显示每条记录，并提供删除按钮
        st.write("### 参与名单（点击可删除）")
        for index, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 3, 1])
            col1.write(f"**{row['姓名']}**")
            col2.write(f"{row['所属部门']} | {row['交通方式']}")
            if col3.button("🗑️ 删除", key=f"del_{index}"):
                df = df.drop(index).reset_index(drop=True)
                save_data(df)
                st.success(f"已删除 {row['姓名']} 的记录")
                st.rerun()  # 实时刷新

    # 导出功能（可选）
    if st.button("📤 导出数据为 CSV"):
        tmp_df = df.copy()
        tmp_df.to_csv("导出_活动参与统计.csv", index=False, encoding='utf-8-sig')
        with open("导出_活动参与统计.csv", "r", encoding='utf-8-sig') as f:
            st.download_button(
                "⬇️ 下载文件",
                f.read(),
                "党支部活动参与统计.csv",
                "text/csv",
                key='download-csv'
            )

    # 登出按钮
    if st.button("🔚 退出登录"):
        st.session_state.view_authenticated = False
        st.rerun()
