import ollama
import time

start = time.time()
stream = ollama.chat(
    model="gemma4:12b-mlx",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful pirate assistant. Provide detailed, "
                       "thoughtful answers but talk like a pirate."
        },
        {
            "role": "user",
            "content": "Explain how the internet works in simple terms."
        },
    ],
    stream=True,
)
 
print(type(stream))
for chunk in stream:
    print(chunk["message"]["content"], end="", flush=True)
 
print()

print(f"\nResponse time: {time.time()- start:2f} seconds]")