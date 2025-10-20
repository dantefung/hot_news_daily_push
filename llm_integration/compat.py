#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LangChain 兼容层：提供一个最小可用的 `LLMChain`，
用于在 LangChain 1.x（移除了 langchain.chains）环境下兼容旧代码。

用法：
    from llm_integration.compat import LLMChain
    chain = LLMChain(prompt=prompt, llm=llm)
    # 旧风格 1：
    text = chain.run(text="...", content="...")
    # 旧风格 2：
    resp = chain.invoke({"text": "..."})
    print(resp["text"])  # 与旧版 LLMChain.invoke 返回 dict 类似

注意：
    - 本兼容层内部使用 Runnable 管线：Prompt | LLM | StrOutputParser。
    - `invoke()` 返回 {"text": str} 以便兼容旧代码中对 response.get("text") 的使用。
    - `run(**kwargs)` 直接返回字符串结果，等价于旧版 `LLMChain.run`。
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

from langchain_core.output_parsers import StrOutputParser


class LLMChain:
    def __init__(self, prompt, llm) -> None:
        """以新式 Runnable 组装旧式链路。

        参数：
            prompt: 任意可与 LLM 组合的 Prompt（如 PromptTemplate/ChatPromptTemplate）。
            llm:    LangChain 的聊天/补全模型实例（如 ChatOpenAI 等）。
        """
        # 采用：Prompt -> LLM -> 转字符串
        self._chain = prompt | llm | StrOutputParser()

    # 旧版常用：chain.run(key=value, ...)
    def run(self, **kwargs: Any) -> str:
        """兼容旧版 LLMChain.run，直接返回字符串。"""
        return self._chain.invoke(kwargs)

    # 旧版：chain.invoke({...}) -> mapping，其中包含 "text"
    def invoke(self, input: Mapping[str, Any]) -> Dict[str, str]:  # type: ignore[override]
        """兼容旧版 LLMChain.invoke，返回形如 {"text": "..."} 的字典。"""
        if not isinstance(input, Mapping):
            raise TypeError("LLMChain.invoke 期望传入 Mapping[str, Any]")
        text: str = self._chain.invoke(dict(input))
        return {"text": text}

    # 兜底：允许作为可调用对象使用
    __call__ = invoke

