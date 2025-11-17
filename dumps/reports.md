I tested the app using this command:

```sh
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"https://www.youtube.com/watch?v=Z3VlbKcE5nE","categories":[{"Other":"Science & Tech"},"Informative & Educational"],"userPrompt":"viral potentials"}'
```

or can be use directly:

```sh
uv run fufufafaethon.py "This just makes me so mad.mp4" \
    --api-key="$GOOGLE_GENAI_API_KEY" \
    --prompt="viral potentials" \
    --categories="Science & Tech, Informative & Educational"
```

openai/whisper segments result: [whisper_segments.json](whisper_segments.json)

genai clips result: [genai_result.json](genai_result.json)
