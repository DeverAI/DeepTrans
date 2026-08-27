# DeepTrans v1.4.0

# DeepTrans - 鏅鸿兘缈昏瘧鍔╂墜

鍩轰簬 PyQt6 寮€鍙戠殑妗岄潰缈昏瘧宸ュ叿锛氶€変腑浠绘剰搴旂敤涓殑鏂囨湰锛岃嚜鍔ㄥ脊鍑烘偓娴獥鏄剧ず缈昏瘧缁撴灉銆傛敮鎸?*鍙?AI 寮曟搸**锛堝皬绫?MiMo / DeepSeek锛岄粯璁ゅ皬绫?mimo-v2.5锛変笌鏈烘缈昏瘧鍙屾爮灞曠ず锛屾彁渚涚郴缁熸墭鐩樹笌鍏ㄥ眬鐑敭銆?
---

## 蹇€熷紑濮?
### 1. 鐜鍑嗗

闇€瑕?Python 3.10+锛堝疄娴?Python 3.13 閫氳繃锛夈€傛帹鑽?Miniforge 鎴?Conda锛?
```bash
conda create -n deeptrans python=3.10 -y
conda activate deeptrans
pip install -r requirements.txt
```

鍥藉唴缃戠粶鍙敤娓呭崕闀滃儚鍔犻€燂細

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 鐢熸垚璧勬簮

```bash
python utils/icon_gen.py
```

> 涓嶆墜鍔ㄧ敓鎴愪篃鍙互锛氱▼搴忓惎鍔ㄦ椂妫€娴嬪埌 `assets/icon.ico` 缂哄け浼氳嚜鍔ㄧ敓鎴愩€?
### 3. 閰嶇疆瀵嗛挜

澶嶅埗 `config.example.json` 涓?`config.json` 鍚庣紪杈戯紝鎴栧湪绋嬪簭棣栨杩愯鏃舵寜鍚戝濉啓锛?
- `deepseek_api_key`锛欴eepSeek 瀹樻柟骞冲彴瀵嗛挜锛堝鐢ㄥ紩鎿庯級
- `xiaomi_api_key`锛氬皬绫?token-plan 瀵嗛挜锛堥粯璁ゅ紩鎿庯級
- 浠讳竴寮曟搸閰嶇疆浜嗗瘑閽ュ嵆鍙娇鐢?AI 缈昏瘧

> 鐪熷疄鐨?`config.json` 鍚湁浣犵殑瀵嗛挜锛屾案杩滀笉瑕佹彁浜ゅ埌鐗堟湰搴擄紙宸插湪 .gitignore 鎺掗櫎锛夈€?
### 4. 杩愯绋嬪簭

```bash
python main.py
```

### 5. 鎵撳寘涓哄彲鎵ц鏂囦欢

```bash
python build.py
```

鐢熸垚鐨勫崟鏂囦欢绋嬪簭浣嶄簬 `dist/DeepTrans.exe`銆傛墦鍖呭悗閰嶇疆鏂囦欢涓?Err.log 濮嬬粓璇诲啓 exe 鍚岀骇鐩綍锛宎ssets 绛夊彧璇昏祫婧愪粠 PyInstaller 瑙ｅ寘鐩綍璇诲彇銆?
---

## 鍔熻兘鐗规€?
### 鏍稿績
- **鍒掕瘝缈昏瘧**锛氶€変腑鏂囨湰鍚庤嚜鍔ㄥ湪鍏夋爣闄勮繎鏄剧ず缈昏瘧绐楀彛锛堟ā鎷?Ctrl+C 鎶撳彇鍓创鏉垮疄鐜帮紝璺ㄥ簲鐢ㄩ€氱敤锛?- **鍙?AI 寮曟搸**锛?  - 灏忕背 MiMo锛坱oken-plan 绔偣锛孫penAI 鍏煎锛夛細妯″瀷鍙€?mimo-v2.5 / mimo-v2.5-pro / mimo-v2-pro锛岄粯璁?mimo-v2.5
  - DeepSeek 瀹樻柟锛氭ā鍨嬪彲閫?chat / reasoner
  - 璁剧疆绐楀彛鍐呬竴閿垏鎹紝涓ゅ瀵嗛挜鍚勮嚜淇濆瓨
- **鏈烘缈昏瘧**锛歞eep-translator 搴擄紝MyMemory 涓婚€?+ Google 鑷姩鍥為€€
- **鏈虹炕澶辫触鍥炶惤 AI**锛堥粯璁ゅ紑鍚級锛氭墍鏈夋満姊板紩鎿庡け璐ユ椂鑷姩鏀圭敤褰撳墠 AI 寮曟搸鍏滃簳锛屼繚璇佹満缈绘爮濮嬬粓鏈夊彲鐢ㄤ骇鍑?- **鍏ㄥ眬鐑敭**锛歚Ctrl+Alt+T` 寮€鍏崇洃鍚紱`Ctrl+Shift+C` 澶嶅埗褰撳墠缁撴灉锛圓I 缁撴灉浼樺厛锛?
### 鐣岄潰
- 鏈烘缈昏瘧涓?AI 缈昏瘧鍚岀獥鍒嗘爮瀵规瘮鏄剧ず
- 绐楀彛鍙嫋鍔ㄣ€佸彸涓嬭鍙媺浼搞€佽嚜鍔ㄩ伩璁╁睆骞曡竟缂橈紙澶氭樉绀哄櫒鎸夊厜鏍囨墍鍦ㄥ睆骞曞畾浣嶏級
- 閿欒浠ュ憡璀︽寜閽憟鐜帮紝鐐瑰嚮鏌ョ湅鍙嬪ソ鎻愮ず涓庡畬鏁磋鎯?- 鐣岄潰璇█涓嫳鍙岃鍙垏鎹紙鍒囨崲鍚庨渶閲嶅惎鐢熸晥锛?
### 绋冲畾鎬ц璁?- **Err.log 鑷姩瀛橀敊鏈哄埗**锛氭墍鏈夎繍琛屾椂閿欒锛堝惈鏈崟鑾峰紓甯革級鑷姩杩藉姞鍐欏叆鏍圭洰褰?`Err.log`
- 閰嶇疆鍘熷瓙鍐欏叆锛堜复鏃舵枃浠?+ replace锛夛紝鎹熷潖閰嶇疆鑷姩澶囦唤涓?`config.json.corrupted`
- Worker 绾跨▼缁撴灉甯?ID 杩借釜锛屾棫绾跨▼涓嶄細瑕嗙洊鏂扮粨鏋?- AI 璇锋眰 30 绉掕秴鏃讹紱鏈烘缈昏瘧鐢辫繘绋嬬骇 socket 瓒呮椂锛?0 绉掞級鍏滃簳
- 鎭㈠榛樿璁剧疆**淇濈暀 API 瀵嗛挜**

---

## 鐩綍缁撴瀯

```
DeepTrans/
鈹溾攢鈹€ main.py              # 涓荤▼搴忓叆鍙ｏ紙鍛戒护琛屽弬鏁拌В鏋愩€佸叏灞€寮傚父閽╁瓙锛?鈹溾攢鈹€ config.json          # 鐢ㄦ埛閰嶇疆
鈹溾攢鈹€ requirements.txt     # 渚濊禆娓呭崟
鈹溾攢鈹€ build.py             # PyInstaller 鎵撳寘鑴氭湰
鈹溾攢鈹€ build_instructions.txt # 鏋勫缓璇存槑
鈹溾攢鈹€ assets/
鈹?  鈹斺攢鈹€ icon.ico         # 绋嬪簭鍥炬爣锛堢己澶辨椂鑷姩鐢熸垚锛?鈹溾攢鈹€ core/                # 鏍稿績妯″潡
鈹?  鈹溾攢鈹€ config.py        # 閰嶇疆绠＄悊 + 璺緞瑙ｆ瀽 + AI_PROVIDERS 寮曟搸瀹氫箟
鈹?  鈹溾攢鈹€ translator.py    # 鍙?AI 寮曟搸 + 鏈烘缈昏瘧寮曟搸
鈹?  鈹溾攢鈹€ monitor.py       # 鍏ㄥ眬榧犳爣/閿洏鐩戝惉涓庡垝璇嶉€昏緫
鈹?  鈹溾攢鈹€ errors.py        # 閿欒鍒嗘瀽锛堝啓鍏?Err.log锛?鈹?  鈹斺攢鈹€ i18n.py          # 涓嫳鏂囩晫闈㈡枃妗?鈹溾攢鈹€ gui/                 # 鐣岄潰妯″潡
鈹?  鈹溾攢鈹€ overlay.py       # 鎮诞缈昏瘧绐楀彛
鈹?  鈹溾攢鈹€ settings.py      # 璁剧疆绐楀彛锛堝惈寮曟搸鍒囨崲锛?鈹?  鈹溾攢鈹€ tray.py          # 绯荤粺鎵樼洏锛圗NABLE_TRAY 妯″潡寮€鍏筹級
鈹?  鈹溾攢鈹€ about.py         # 鍏充簬绐楀彛
鈹?  鈹斺攢鈹€ styles.py        # 鍏ㄥ眬鏍峰紡
鈹斺攢鈹€ utils/
    鈹溾攢鈹€ errlog.py        # Err.log 鑷姩瀛橀敊鏈哄埗
    鈹斺攢鈹€ icon_gen.py      # 鍥炬爣鐢熸垚宸ュ叿
```

鏂囨。浣撶郴浣嶄簬鏍圭洰褰曪細`Design.md`锛堝綋鍓嶈璁★級銆乣Techniques.md`锛堟妧鏈柟妗堬級銆乣Fact.md`(浜嬪疄涓庣敤鎴峰亸濂?銆乣FreqErr.md`锛堝父瑙侀敊璇級銆乣Future.md`锛堟湭鏉ラ渶姹傦級銆乣dev_log/`锛堢増鏈紨杩涜褰曪級銆乣Err.log`锛堣繍琛屾湡閿欒锛夈€?
---

## 閰嶇疆璇存槑

| 閰嶇疆椤?| 榛樿鍊?| 璇存槑 |
|--------|--------|------|
| `ai_provider` | "xiaomi" | AI 寮曟搸锛歺iaomi / deepseek |
| `ai_model` | "mimo-v2.5" | 妯″瀷鍚嶏紙椤诲睘浜庢墍閫夊紩鎿庣殑妯″瀷闆嗭級 |
| `xiaomi_api_key` | "" | 灏忕背 token-plan 瀵嗛挜 |
| `deepseek_api_key` | "" | DeepSeek 瀹樻柟瀵嗛挜 |
| `source_lang` | "en-US" | 婧愯瑷€锛堟垨 auto 鑷姩鍒ゆ柇锛?|
| `target_lang` | "zh-CN" | 鐩爣璇█ |
| `mech_translator` | "mymemory" | 鏈虹炕寮曟搸 mymemory / google |
| `mech_fallback` | true | 涓绘満缈诲け璐ユ槸鍚﹀洖閫€鍙︿竴瀹?|
| `mech_ai_fallback` | true | 鏈虹炕寮曟搸鍏ㄩ儴澶辫触鏃舵槸鍚︾敤褰撳墠 AI 寮曟搸鍏滃簳 |
| `mech_trans_enabled` | false | 鏄惁鍚敤鏈烘缈昏瘧鏍?|
| `auto_translate_enabled` | true | 鍒掕瘝鑷姩缈昏瘧鎬诲紑鍏?|
| `trigger_delay` | 1.0 | 閫変腑鍒拌Е鍙?AI 缈昏瘧鐨勫欢杩熺鏁帮紙0-10锛?|
| `shortcut_toggle` | "ctrl+alt+t" | 鐩戝惉寮€鍏崇儹閿?|
| `shortcut_copy_result` | "ctrl+shift+c" | 澶嶅埗缁撴灉鐑敭 |
| `overlay_width` | 450 | 鎮诞绐楀垵濮嬪搴︼紙400-1200 鍙皟锛?|
| `window_opacity` | 0.95 | 涓嶉€忔槑搴︼紙0.1-1.0锛?|
| `window_shadow` | true | 闃村奖寮€鍏?|
| `window_soft_edges` | 10 | 鍦嗚鏌斿寲绋嬪害 |
| `theme_color` / `text_color` / `ui_bg_color` | 钃?榛?鐧?| 棰滆壊涓変欢濂楋紙#RRGGBB锛屼繚瀛樻椂鏍￠獙锛?|
| `ui_language` | "zh" | 鐣岄潰璇█ zh / en |
| `ai_prompt_style` | "None" | 鎻愮ず璇嶉鏍?None / Native / Professional |

璇█鏂瑰悜瑙勫垯锛氭簮鐩爣浠诲～鍏朵竴鍗冲彲涓嫳浜掕瘧鈥斺€旂▼搴忔娴嬭緭鍏ヨ嫢灞炰簬鐩爣璇█鍒欒嚜鍔ㄥ弽鍚戠炕璇戯紱`source_lang=auto` 鏃舵寜鏂囨湰鍐呮槸鍚﹀惈涓枃鍒ゅ畾銆?
---

## 浣跨敤璇存槑

1. **鍚姩**锛歚python main.py`锛屾墭鐩樺嚭鐜板浘鏍囧嵆鍚庡彴灏辩华
2. **鍒掕瘝**锛氫换鎰忓簲鐢ㄩ€変腑鏂囨湰锛岀◢鍊欐偓娴獥寮瑰嚭锛堟満缈诲叧鏃朵粎鏄剧ず AI 鏍忥級
3. **鐑敭**锛歚Ctrl+Alt+T` 鏆傚仠/鎭㈠鐩戝惉锛堟墭鐩樿彍鍗曞悓姝ュ嬀閫夋€侊級锛沗Ctrl+Shift+C` 澶嶅埗缁撴灉
4. **鎷栧姩**锛氭寜浣忔偓娴獥绌虹櫧澶勬嫋鍔紱鍙充笅瑙掓墜鏌勮皟鏁村ぇ灏忥紱鐐瑰嚮绐楀鎴栫孩鑹?X 鍏抽棴
5. **璁剧疆**锛氭墭鐩樺彸閿?-> 璁剧疆锛涙垨鐩存帴淇敼 config.json 鍚庨噸鍚?
## 鍛戒护琛屽弬鏁?
```bash
python main.py [options]
```

| 鍙傛暟 | 璇存槑 |
|------|------|
| `--config PATH` | 鎸囧畾閰嶇疆鏂囦欢璺緞锛堝紑鍙戞ā寮忛粯璁ら殢绋嬪簭鐩綍瑙ｆ瀽锛?|
| `--debug` | 璋冭瘯杈撳嚭锛堟墦鍗板疄闄呭姞杞界殑閰嶇疆璺緞绛夛級 |
| `--no-tray` | 涓嶅垱寤虹郴缁熸墭鐩樺浘鏍?|
| `--portable` | 渚挎惡妯″紡锛氬缁堣鍐欑▼搴忔梺杈圭殑 config.json |

鍙﹀瓨鍦ㄦ簮鐮佺骇妯″潡寮€鍏筹細`gui/tray.py` 鐨?`ENABLE_TRAY = True/False` 鐢ㄤ簬婕旂ず鎴栨帓鏌ユ椂褰诲簳闅愯棌鎵樼洏鍏ュ彛銆?
---

## 鏁呴殰鎺掗櫎

甯歌闂閫熸煡锛堟洿瀹屾暣鐨勯敊璇被鍨嬭 `FreqErr.md`锛夛細

1. **AI 缈昏瘧鎶?API Key not set**
   - 瀵瑰簲寮曟搸瀵嗛挜涓虹┖銆傛墦寮€璁剧疆濉啓锛涚‘璁?`ai_provider` 涓庢墍濉瘑閽ュ尮閰?
2. **鏈烘缈昏瘧澶辫触/瓒呮椂**
   - MyMemory 涓?Google 涓哄厤璐瑰叕鍏辨湇鍔★紝閮ㄥ垎缃戠粶鐜涓嶅彲杈撅紙鏈」鐩儴缃茬幆澧冨疄娴嬪潎杩炴帴瓒呮椂锛夛紱鐧惧害/鏈夐亾绛夊浗鍐呭厤 Key 缃戦〉鎺ュ彛瀹炴祴鍧囨湁鍙嶇埇澧欙紝鏃犳硶浣滀负鍏嶉厤缃紩鎿庢彁渚?   - 榛樿寮€鍚?鏈虹炕澶辫触鍥炶惤 AI"锛屾満缈绘爮涓嶄細绌烘墜鑰屽綊锛涘彲鍦ㄨ缃腑鍏抽棴璇ヨ涓?   - 灞炵綉缁滈檺鍒惰€岄潪绋嬪簭缂洪櫡锛涜鎯呭彲瑙佸憡璀︽寜閽垨 Err.log

3. **绐楀彛涓嶆樉绀?*
   - 纭鐩戝惉宸插紑鍚紙鎵樼洏鍕鹃€夋€侊級锛涜皟鏁?`trigger_delay`锛涙鏌ユ槸鍚﹁鍏朵粬缃《绐楅伄鎸?
4. **鐑敭鏃犳晥**
   - 琚崰鐢ㄦ椂鏇存崲 `shortcut_toggle`/`shortcut_copy_result` 閰嶇疆

5. **鎺掓煡鍒╁櫒 Err.log**
   - 浠讳綍寮傚父閮戒細甯︽椂闂存埑涓庡爢鏍堣拷鍔犲湪鏍圭洰褰?`Err.log`
   - 瀹氫綅骞朵慨澶嶉棶棰樺悗锛屾竻绌鸿鏂囦欢鍐呭鍗冲彲锛堣鍕垮垹闄ゆ枃浠舵湰韬級

## 鎵撳寘鍚庢敞鎰忎簨椤?
- 鍗曟枃浠剁増棣栧惎鍔ㄧ◢鎱㈠睘姝ｅ父锛堣В鍖呰祫婧愶級
- 鏉€杞鎶ユ椂鍙敼鐢?onedir 妯″紡鑷璋冩暣 build.py 鍙傛暟
- 鏇存崲 exe 浣嶇疆涓嶅奖鍝嶉厤缃鍐欙紙濮嬬粓璺熼殢 exe 鎵€鍦ㄧ洰褰曪級

---

## 寮€鍙戣鏄?
- 鎶€鏈爤锛歅ython 3.10+ / PyQt6 / openai SDK / deep-translator / pynput / keyboard / pyautogui / pillow / pyperclip
- 鏋舵瀯鍒嗗眰锛歮ain锛堢紪鎺掍笌绾跨▼锛夈€乧ore锛堜笟鍔★級銆乬ui锛堢晫闈級銆乽tils锛堝伐鍏凤級锛岃瑙?`Design.md`
- 鎵╁睍鏂?AI 寮曟搸锛氬湪 `core/config.py` 鐨?`AI_PROVIDERS` 澧炲姞 provider 瀹氫箟锛坆ase_url/api_key_field/models锛夛紝璁剧疆绐楀彛涓庢牎楠屽櫒鑷姩鐢熸晥
- 鐗堟湰婕旇繘璁板綍瑙?`dev_log/`锛涙湰杞彉鏇存憳瑕佷害鏀跺綍浜庡叾涓?
## 璁稿彲璇?
MIT License锛岃瑙?[LICENSE](LICENSE) 鏂囦欢銆?
## 鑷磋阿

PyQt6銆丏eepSeek銆乆iaomi MiMo銆丮yMemory銆丟oogle Translate 鍙?deep-translator 绛夊紑婧愪笌鏈嶅姟鏀寔銆?