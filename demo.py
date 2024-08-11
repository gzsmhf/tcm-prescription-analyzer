# -*- coding: utf-8 -*-

from analyze import get_max_sublist, call_llm, format_add_sub, update_herb_name
from config import enable_gpu_on_ocr, system_prompt
import re
import json
import streamlit as st

st.title("中医处方分析助手")

tab1, tab2 = st.tabs(["文字输入", "图片识别"])
with tab1:
    prescription = tab1.text_area("请输入处方并以空格间隔", placeholder="无需输入克数")
    submit = tab1.button("开始分析")
    if submit:
        prescriptions = [update_herb_name(item) for item in re.split(r"[，,。,;； 、]", prescription) if item]
        result = get_max_sublist(prescriptions)
        result = format_add_sub(result)
        user_prompt = f"我的处方是：{prescriptions}'。它是由基本经方{result['formula']['title']}加减得到的。{result['formula']['title']}的功效是{result['formula']['function']}。增加的中药有{result['add']}，减少的中药有{result['sub']}。"
        summary = call_llm(user_prompt, system_prompt)
        tab1.subheader("分析结果")
        tab1.write(summary)
with tab2:
    import easyocr
    uploaded_file = tab2.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        reader = easyocr.Reader(['ch_sim'], gpu = enable_gpu_on_ocr)
        result = reader.readtext(uploaded_file.read(), detail=0)
        ocr_system_prompt = """
        我有一个从ocr导出的文字列表，我希望你从中把所有中药名提取出来，并满足一下几个要求：
            1. 请使用完整中药名，比如生地要改成生地黄。
            2. 去掉药名前的炮制方法，如炙、炒等，如炙某某改成某某，炒某某改成某某。
            3. 如果药名第一个字是生，请去掉生，生姜、生地黄除外，如生某某改成某某。
            4. 只返回字符串列表使用双引号，不需要解释原因及过程。
        """
        user_prompt = f"原始字符串列表：{result}"
        results = call_llm(user_prompt, ocr_system_prompt)
        pattern = r'\[.*?\]'
        results = re.match(pattern, results).group(0)
        prescription = [update_herb_name(item) for item in json.loads(results) if item]
        result = get_max_sublist(prescription)
        result = format_add_sub(result)
        user_prompt = f"我的处方是：{prescription}'。它是由基本经方{result['formula']['title']}加减得到的。{result['formula']['title']}的功效是{result['formula']['function']}。增加的中药有{result['add']}，减少的中药有{result['sub']}。"
        summary = call_llm(user_prompt, system_prompt)
        tab2.subheader("分析结果")
        tab2.write(summary)