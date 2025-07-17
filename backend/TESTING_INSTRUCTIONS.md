# Nightingale 测试流程说明

## 1. Prompt 生成
- 进入 backend 目录，激活 Gemini 虚拟环境：
  ```sh
  cd backend
  venv_gemini\Scripts\activate
  python scripts/generate_prompts.py
  ```
- 生成的 prompt 文件在 `generated_prompts/` 目录下，文件名如 `generated_prompts_YYYYMMDD_HHMMSS.json`
- 你可以手动编辑或筛选 prompt 文件内容

## 2. 批量音频生成
- 激活 Stable Audio 虚拟环境：
  ```sh
  venv_stableaudio\Scripts\activate
  python scripts/generate_audio_from_generated_prompts.py
  ```
- 选择你要用的 prompt 文件，脚本会自动生成音频到 `audio_test_output/generated_YYYYMMDD_HHMMSS/audio_files/`，并生成 web_test_data.json

## 3. Web 端评测
- 激活 API 虚拟环境，启动 web 服务：
  ```sh
  venv_api\Scripts\activate
  python scripts/fixed_test_web.py --data_file audio_test_output/generated_YYYYMMDD_HHMMSS/web_test_data.json --audio_dir audio_test_output/generated_YYYYMMDD_HHMMSS/audio_files --port 8010
  ```
- 在浏览器访问 http://localhost:8010 进行试听和评价

## 目录结构说明
```
backend/
  generated_prompts/
    generated_prompts_YYYYMMDD_HHMMSS.json
  audio_test_output/
    generated_YYYYMMDD_HHMMSS/
      generated_prompts.json
      audio_files/
        test_001.wav
        ...
      web_test_data.json
  scripts/
    generate_prompts.py
    generate_audio_from_generated_prompts.py
    fixed_test_web.py
```

## 只保留以上主链路，其余脚本和目录均可删除。 