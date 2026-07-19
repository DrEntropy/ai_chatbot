import ollama
 
response = ollama.chat(
    model="gemma4:12b-mlx",
    messages=[
        {
            "role": "system",
            "content": "You are a friendly science teacher who explains "
                       "concepts using fun analogies. Keep your answers "
                       "under 100 words."
        },
        {
            "role": "user",
            "content": "How does gravity work?"
        },
    ],
)
 
print(response["message"]["content"])