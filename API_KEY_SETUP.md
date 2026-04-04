# 🔑 How to Get a Qwen API Key

The TourStats app uses AI (Qwen/LLM) to extract excursion data from natural language messages. You need an API key for this to work.

## Option 1: Use Alibaba Cloud Qwen (Recommended)

1. **Sign up** at [Alibaba Cloud](https://www.alibabacloud.com/)
2. **Go to** [DashScope Console](https://dashscope.console.aliyun.com/apiKey)
3. **Create an API key** (it's free with some credits)
4. **Copy the key** (starts with `sk-`)
5. **Add to `.env` file**:
   ```
   QWEN_API_KEY=sk-your-actual-key-here
   ```

## Option 2: Use OpenAI Instead

If you have an OpenAI key, you can use it:

```env
QWEN_API_KEY=sk-proj-your-openai-key
QWEN_BASE_URL=https://api.openai.com/v1
QWEN_MODEL=gpt-3.5-turbo
```

## Option 3: Use Any OpenAI-Compatible Provider

The app works with any OpenAI-compatible API:

```env
QWEN_API_KEY=your-key
QWEN_BASE_URL=https://your-custom-endpoint/v1
QWEN_MODEL=your-model-name
```

## After Adding Your Key

Restart the services:

```bash
docker compose restart backend nanobot
```

Or rebuild if you changed the `.env`:

```bash
docker compose up -d --build backend nanobot
```

## Test It

1. Open http://localhost:3000
2. Type: "Just finished a tour with 15 people"
3. The AI should respond with extracted data!

---

**Don't have a key yet?** The app will still work for viewing statistics and the UI, but AI features (chat, data extraction) will show an error with instructions.
