import ollama

response = ollama.chat(model = "gemma3:4b", 
                        messages=[
                            {"role": "user", "content":"What is the capital of Italy?"}
                        ],
                    )

print(response["message"]["content"])