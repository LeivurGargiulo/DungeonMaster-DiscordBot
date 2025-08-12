# OpenRouter Setup Guide

This guide explains how to set up and use OpenRouter as an LLM provider for the Mini Dungeon Master bot.

## What is OpenRouter?

OpenRouter is a unified API that provides access to multiple AI models from various providers (OpenAI, Anthropic, Google, Meta, etc.) through a single interface. This gives you more flexibility in choosing models and potentially better pricing.

## Setup Instructions

### 1. Get an OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to your API keys section
4. Create a new API key
5. Copy the API key (it starts with `sk-or-`)

### 2. Configure Environment Variables

Set the following environment variables:

```bash
export LLM_PROVIDER="openrouter"
export OPENROUTER_API_KEY=sk-or-your-api-key-here
export OPENROUTER_MODEL="openai/gpt-3.5-turbo"
```

### 3. Choose a Model

OpenRouter supports many models. Here are some popular options:

- `openai/gpt-3.5-turbo` - Fast and cost-effective
- `openai/gpt-4` - More capable but more expensive
- `anthropic/claude-3-haiku` - Good balance of speed and capability
- `meta-llama/llama-3.1-8b-instruct` - Open source option
- `google/gemini-pro` - Google's model

You can browse all available models at [OpenRouter Models](https://openrouter.ai/models).

### 4. Test the Setup

Run the bot and try the `/start` command. If everything is configured correctly, you should see AI-generated welcome messages and story content.

## Configuration Examples

### Basic Setup
```bash
export LLM_PROVIDER="openrouter"
export OPENROUTER_API_KEY=sk-or-your-key
export OPENROUTER_MODEL="openai/gpt-3.5-turbo"
```

### Using Claude
```bash
export LLM_PROVIDER="openrouter"
export OPENROUTER_API_KEY=sk-or-your-key
export OPENROUTER_MODEL="anthropic/claude-3-haiku"
```

### Using Gemini
```bash
export LLM_PROVIDER="openrouter"
export OPENROUTER_API_KEY=sk-or-your-key
export OPENROUTER_MODEL="google/gemini-pro"
```

## Troubleshooting

### Common Issues

1. **"No module named 'requests'"**
   - Install the requests library: `pip install requests`

2. **"OpenRouter API error"**
   - Check that your API key is correct
   - Verify the model name is valid
   - Ensure you have sufficient credits in your OpenRouter account

3. **"LLM not available"**
   - Check that `LLM_PROVIDER` is set to "openrouter"
   - Verify your API key is set correctly

### Fallback Behavior

If OpenRouter is not available or fails, the bot will automatically fall back to static text responses. This ensures the bot continues to work even if there are API issues.

## Cost Considerations

- OpenRouter charges per token used
- Different models have different pricing
- You can monitor usage in your OpenRouter dashboard
- Consider setting up usage limits to control costs

## Model Comparison

| Model | Speed | Capability | Cost |
|-------|-------|------------|------|
| gpt-3.5-turbo | Fast | Good | Low |
| gpt-4 | Slow | Excellent | High |
| claude-3-haiku | Fast | Good | Medium |
| gemini-pro | Medium | Good | Low |

Choose based on your needs for speed, quality, and budget.