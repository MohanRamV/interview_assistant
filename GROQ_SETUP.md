# Groq API Setup Guide

## Overview
This project has been migrated from Google Gemini to Groq for AI-powered interview assistance.

## Setup Instructions

### 1. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (it starts with `gsk_`)

### 2. Configure Environment Variables
Create or update your `.env` file in the project root:

```env
# Groq API Configuration
GROQ_API_KEY=gsk-your-api-key-here

# Other existing variables...
MONGODB_URI=your-mongodb-uri
FRONTEND_ORIGIN=http://localhost:3000
```

### 3. Install Dependencies
The project already includes the required `requests` library. If you need to reinstall:

```bash
pip install -r requirements.txt
```

### 4. Test the Setup
Run the test script to verify Groq is working:

```bash
cd tests
python test_simple.py
```

Expected output:
```
API Key: gsk_1234567...
Response: Hello! How can I help you today?
✅ Groq API is working!
Model used: llama3-8b-8192 (Free tier)
```

## Groq Model Information

- **Primary Model**: `llama3-8b-8192` (fast, reliable, free)
- **API Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Max Tokens**: 4000 (configurable)
- **Temperature**: 0.7 (balanced creativity)
- **Free Tier**: Generous limits, no payment required

## Available Free Models

1. **llama3-8b-8192** (Recommended)
   - Fast and reliable
   - Good for general tasks
   - 8192 token context

2. **llama3-70b-8192**
   - More capable model
   - Slightly slower but better quality
   - 8192 token context

3. **mixtral-8x7b-32768**
   - Very fast responses
   - Good for simple tasks
   - 32768 token context

4. **gemma2-9b-it**
   - Good for coding tasks
   - Fast and efficient
   - Medium context

## Migration Notes

### What Changed:
- ✅ Replaced Google Gemini with Groq
- ✅ Updated API calls to use Groq format
- ✅ Maintained compatibility with existing code
- ✅ Commented out Google dependencies

### What Remains the Same:
- ✅ All interview functionality works identically
- ✅ Question generation, scoring, and feedback unchanged
- ✅ Frontend interface remains the same
- ✅ Database structure unchanged

## Benefits of Groq

- **Ultra-fast responses** (2-3x faster than other APIs)
- **Completely free** (no payment required)
- **High availability** (99.9% uptime)
- **OpenAI-compatible API** (easy to integrate)
- **Generous rate limits** (no strict throttling)

## Troubleshooting

### Common Issues:

1. **"GROQ_API_KEY environment variable is required"**
   - Make sure your `.env` file has the correct API key
   - Restart your backend server after updating `.env`

2. **"Groq API error: 401 Unauthorized"**
   - Check that your API key is correct
   - Ensure you have a valid Groq account

3. **"Groq API error: 429 Too Many Requests"**
   - You've hit the rate limit
   - Wait a moment and try again

4. **"Groq API error: 500 Internal Server Error"**
   - Groq service might be temporarily down
   - Check [Groq Status](https://status.groq.com/)

### Performance Notes:
- Groq responses are typically 2-3x faster than Gemini
- Token limits are generous
- Better JSON parsing capabilities
- More reliable uptime

## Support
For Groq API issues, visit:
- [Groq Documentation](https://console.groq.com/docs)
- [Groq Community](https://community.groq.com/)
- [Groq Discord](https://discord.gg/groq) 