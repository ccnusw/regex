import streamlit as st
import re
import pandas as pd
from io import StringIO


def read_file_content(file):
    try:
        content = file.read()  # 读取文件内容为字节类型
        content = content.decode('utf-8')  # 解码为字符串
        return content
    except UnicodeDecodeError:
        st.error("文件不是UTF-8编码，请将文件转换为UTF-8格式后再上传。")
        return None


def convert_file_to_one_sentence_per_line(file):
    text = read_file_content(file)
    if text is None:
        return []

    # 去掉多余的换行符
    text = re.sub(r'\s+', '', text)

    # 使用正则表达式匹配所有完整的句子
    sentences = re.findall(r'.+?[。！？…]', text)

    # 如果有剩余部分没有句末标点符号，将其视为单独的句子
    remaining = re.sub(r'.+?[。！？…]', '', text).strip()
    if remaining:
        sentences.append(remaining)

    return sentences


def process_file_for_regex(file_content, regex):
    try:
        pattern = re.compile(regex)
    except re.error:
        return None, "正则表达式错误，请修改！"

    matched_sentences = []

    for i, sentence in enumerate(file_content.splitlines()):
        if pattern.search(sentence):
            highlighted_sentence = pattern.sub(r'<mark style="background-color: yellow">\g<0></mark>', sentence)
            matched_sentences.append((i + 1, highlighted_sentence, sentence))

    return matched_sentences, None


def save_processed_file(content, filename="processed_file.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for line in content:
            f.write(line + "\n")
    return filename


def save_matches(matches):
    output_file = "regex_matches.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, match in enumerate(matches, 1):
            f.write(f"{idx}. {match[2]}\n")  # 写入原始句子
    return output_file


# Streamlit app
st.markdown("<h3 style='text-align: center;'>🏃文本处理与正则表达式工具</h3>", unsafe_allow_html=True)
# st.write("")  # 空行
# st.title("文本处理与正则表达式工具")

# Sidebar with options
option = st.sidebar.radio("选择功能", ("转换文件为一句话一行", "正则表达式检索"))

if option == "转换文件为一句话一行":

    # st.title("转换文件为一句话一行")
    st.markdown("<h5 style='text-align: center;'>转换文件为一句话一行</h5>", unsafe_allow_html=True)
    st.write("")  # 空行
    st.write("")  # 空行
    st.write("")  # 空行
    uploaded_file = st.file_uploader("请上传一个txt文件", type=["txt"])

    if uploaded_file:
        if st.button("清洗文件"):
            with st.spinner("处理文件中..."):
                sentences = convert_file_to_one_sentence_per_line(uploaded_file)
                if sentences:
                    output_file = save_processed_file(sentences)
                    st.success("处理完毕！")

                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="下载处理好的文件",
                            data=file,
                            file_name=output_file,
                            mime="text/plain"
                        )
                else:
                    st.error("文件处理失败，请检查文件格式。")

elif option == "正则表达式检索":
    # st.title("正则表达式检索")
    st.markdown("<h5 style='text-align: center;'>正则表达式检索</h5>", unsafe_allow_html=True)
    st.write("")  # 空行st.write("")  # 空行
    st.write("")  # 空行
    st.write("")  # 空行
    # 文件上传组件
    uploaded_file = st.file_uploader("请上传一个txt文件", type=["txt"])

    # 正则表达式输入框
    regex_input = st.text_input("输入正则表达式")

    # 匹配按钮
    if st.button("匹配正则表达式"):
        if uploaded_file and regex_input:
            file_content = read_file_content(uploaded_file)
            matches, error = process_file_for_regex(file_content, regex_input)

            if error:
                st.error(error)
            else:
                if matches:
                    st.success(f"匹配成功！共找到 {len(matches)} 个句子。")

                    df = pd.DataFrame(matches, columns=["原始序号", "句子", "纯文本句子"])
                    df = df.drop(columns=["原始序号", "纯文本句子"])  # 隐藏原始序号和纯文本列
                    df.insert(0, "序号", range(1, len(df) + 1))  # 添加从1开始的序号

                    page_size = 25
                    total_pages = len(df) // page_size + int(len(df) % page_size > 0)
                    current_page = st.number_input("页码", min_value=1, max_value=total_pages, step=1)

                    start_idx = (current_page - 1) * page_size
                    end_idx = start_idx + page_size

                    # 使用 st.markdown 和 unsafe_allow_html=True 渲染 HTML 高亮
                    for index, row in df.iloc[start_idx:end_idx].iterrows():
                        st.markdown(f"**{row['序号']}.** {row['句子']}", unsafe_allow_html=True)

                    output_file = save_matches(matches)
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="下载检索结果",
                            data=file,
                            file_name=output_file,
                            mime="text/plain"
                        )
                else:
                    st.warning("未找到匹配結果。")
        else:
            st.warning("请上传文件并输入正则表达式")

# Right sidebar with common regex patterns
st.sidebar.title("常见正则表达式")
st.sidebar.write(r"匹配电子邮件地址: `[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+`")
st.sidebar.write(r"匹配手机号码: `\d{3}-\d{3}-\d{4}`")
st.sidebar.write(r"匹配网址: `https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+`")
st.sidebar.write(r"匹配日期 (YYYY-MM-DD): `\d{4}-\d{2}-\d{2}`")
# 添加分割线和版权信息，固定在页面底部
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    text-align: center;
    padding: 10px 0;
    border-top: 1px solid #ddd;
    font-family: KaiTi;
}
.email {
    font-family: KaiTi,Times New Roman;
}
</style>
<div class="footer">
    Copyright © 2024-长期 版权所有：华师沈威，在使用中如果有任何问题可以发邮件至：sw@ccnu.edu.cn
</div>
""", unsafe_allow_html=True)

