import socket
import threading

from deep_translator import GoogleTranslator, MyMemoryTranslator
from openai import OpenAI

from .config import AI_PROVIDERS, cfg
from utils.errlog import log_error, log_exception, log_warning

# 机械翻译底层库(deep-translator/requests)无内建总超时，
# 且其连接内的 DNS 解析(getaddrinfo)不受 socket 默认超时约束，
# 在黑洞网络的域名上会无限阻塞。除 socket 兜底外，
# 每次引擎尝试再用标准库看门狗线程硬限时（详见 _run_with_timeout）。
socket.setdefaulttimeout(8)

# 单个机械翻译引擎尝试的看门狗上限（秒）
MECH_ATTEMPT_TIMEOUT = 12


class TranslatorCore:
    def __init__(self):
        self.client = None
        # 追踪 (api_key, base_url)，变化时才重建客户端
        self._client_sig = None
        self._setup_client()

    def _setup_client(self):
        """按当前 AI 引擎配置创建/复用 OpenAI 兼容客户端。"""
        provider = cfg.provider()
        api_key = cfg.get(provider["api_key_field"])
        if not api_key:
            if self.client is not None:
                print(f"Warning: {provider['label']} API key is empty")
            self.client = None
            self._client_sig = None
            return
        sig = (api_key, provider["base_url"])
        if self.client is None or self._client_sig != sig:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=provider["base_url"],
                    timeout=30.0  # 30秒超时
                )
                self._client_sig = sig
            except Exception as e:
                msg = f"Failed to create AI client for {provider['label']}: {e}"
                print(msg)
                log_error(msg)
                self.client = None
                self._client_sig = None

    def detect_languages(self, text):
        # Simple heuristic for CN <-> EN
        # If text contains Chinese characters, assume Source=CN, Target=EN
        # Else assume Source=EN, Target=CN
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)

        user_source = cfg.get("source_lang")
        user_target = cfg.get("target_lang")

        if user_source == "auto":
            if has_chinese:
                return "zh-CN", "en"
            else:
                return "en", user_target
        else:
            # If user fixed languages, we might need to swap them if input matches target?
            # User said: "Select A output B, Select B output A"
            # So if input looks like Target, we swap.

            # Check if input matches 'user_source' or 'user_target' roughly
            # This is hard without reliable language detection.
            # Let's trust the "auto" logic for now as default.
            if has_chinese and user_source != "zh-CN":
                 # If input is Chinese but user set Source=EN, we swap
                 return user_target, user_source
            if not has_chinese and user_source == "zh-CN":
                 return user_target, user_source

            return user_source, user_target

    def _map_lang(self, lang, provider):
        """
        Map language codes to provider specific formats.
        注意：MyMemory 语言码大小写敏感（如 en-US），不可整体小写后透传。
        """
        lang_l = (lang or "").lower()
        if provider == "mymemory":
            # 当前 deep-translator 的 MyMemory 表只接受 zh-CN/zh-TW 等完整码，
            # 不支持裸 zh；中文一律映射为简体 zh-CN。
            if lang_l.startswith("zh"):
                return "zh-CN"
            # en/en-us/en-gb/... 统一映射到受支持的 en-US
            if lang_l == "en" or lang_l.startswith("en-"):
                return "en-US"
            return lang
        elif provider == "google":
            if lang_l == "zh":
                return "zh-CN"
            return lang
        return lang

    def mechanical_translate(self, text):
        """
        Uses open source library.
        Respects user preference and handles fallback.
        """
        # 空文本处理
        if not text or not text.strip():
            return None, "Empty text"

        try:
            raw_src, raw_tgt = self.detect_languages(text)

            primary = cfg.get("mech_translator")
            fallback = cfg.get("mech_fallback")

            translators = []

            # Helper to create translator instances safely
            def create_translator(name, s, t):
                s_mapped = self._map_lang(s, name)
                t_mapped = self._map_lang(t, name)
                if name == "google":
                    # Google supports 'auto'
                    return GoogleTranslator(source='auto' if s == 'auto' else s_mapped, target=t_mapped)
                else:
                    # MyMemory needs explicit source usually
                    return MyMemoryTranslator(source=s_mapped, target=t_mapped)

            if primary == "google":
                translators.append(("google", create_translator("google", 'auto', raw_tgt)))
                if fallback:
                    translators.append(("mymemory", create_translator("mymemory", raw_src, raw_tgt)))
            else:  # mymemory
                translators.append(("mymemory", create_translator("mymemory", raw_src, raw_tgt)))
                if fallback:
                    translators.append(("google", create_translator("google", 'auto', raw_tgt)))

            errors = []
            for name, engine in translators:
                kind, value = self._run_with_timeout(
                    engine.translate, (text,), MECH_ATTEMPT_TIMEOUT
                )
                if kind == "ok" and value:
                    return value, None  # Success, No Error
                if kind == "timeout":
                    msg = f"{name}: no response within {MECH_ATTEMPT_TIMEOUT}s (DNS/connect black-hole)"
                    errors.append(msg)
                    print(f"Translator {name} timed out")
                    log_warning(f"Mechanical translator '{name}' timed out")
                elif kind == "error":
                    errors.append(f"{name}: {str(value)}")
                    print(f"Translator {name} failed: {value}")
                    log_warning(f"Mechanical translator '{name}' failed: {value}")

            # 国内免Key端点均受反爬限制（百度/有道/腾讯实测），网络受限环境下
            # 机翻全链路不可达：按用户决策回落当前 AI 引擎兜底翻译。
            ai_result = self._ai_fallback(text)
            if ai_result:
                return ai_result, None

            failure = f"Translation Failed.\nErrors:\n" + "\n".join(errors)
            log_error(failure.replace("\n", " | "))
            return None, failure

        except Exception as e:
            log_exception("translator.mechanical_translate", e)
            return None, f"Translation Error: {str(e)}"

    def _run_with_timeout(self, func, args=(), timeout=MECH_ATTEMPT_TIMEOUT):
        """在守护线程中执行阻塞调用并硬限时。

        返回 ("ok", result) / ("timeout", None) / ("error", exc)。
        超时的线程无法被安全终止（尤其卡在 getaddrinfo 时），
        只能放弃等待；该线程为 daemon，最终随进程退出。
        """
        box = {}

        def target():
            try:
                box["kind"], box["value"] = "ok", func(*args)
            except Exception as e:  # noqa: BLE001 - 引擎异常统一归口
                box["kind"], box["value"] = "error", e

        t = threading.Thread(target=target, daemon=True)
        t.start()
        t.join(timeout)
        if t.is_alive():
            return "timeout", None
        return box.get("kind", "error"), box.get("value")

    def _ai_fallback(self, text):
        """机翻全失败时的 AI 兜底（可用 mech_ai_fallback 关闭）。"""
        if not cfg.get("mech_ai_fallback"):
            return None
        log_warning("All mechanical translators failed; falling back to AI engine")
        result = self.ai_translate(text)
        if result.startswith(("AI Error:", "Error:")):
            # AI 兜底也失败：返回 None 走原有错误提示路径
            return None
        return result

    def ai_translate(self, text):
        """
        Uses the configured AI provider (DeepSeek or Xiaomi MiMo),
        both via OpenAI-compatible Chat Completions APIs.
        """
        # 空文本处理
        if not text or not text.strip():
            return "Error: Empty text"

        # Reload client in case provider/key changed
        self._setup_client()

        if not self.client:
            provider_label = cfg.provider()["label"]
            return f"AI Error: {provider_label} API Key not set."

        src, tgt = self.detect_languages(text)

        provider_id, model_name = cfg.resolve_ai_model()

        style = cfg.get("ai_prompt_style")

        system_prompt = "You are a professional translator."
        user_prompt = f"Translate the following text to {tgt}."

        if style == "Native":
            user_prompt += " The translation should sound native and natural."
        elif style == "Professional":
            user_prompt += " Use a professional and formal tone."

        user_prompt += f"\n\nText:\n{text}"

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False
            )
            # 验证响应结构
            if not response.choices or len(response.choices) == 0:
                msg = f"AI Error: Empty response from {provider_id}"
                log_error(msg)
                return msg
            content = response.choices[0].message.content
            if not content:
                msg = f"AI Error: No content in response from {provider_id}"
                log_error(msg)
                return msg
            return content.strip()
        except Exception as e:
            log_exception(f"translator.ai_translate({provider_id}/{model_name})", e)
            return f"AI Error: {str(e)}"


# Global instance
translator = TranslatorCore()
