import ollama
 
 
history = [
    {
        "role": "system",
        "content": "You are a friendly and helpful assistant. "
                   "Be concise but thorough in your answers."
    }
]
 
print("Chat with AI! (type ‘quit’, ‘exit’, or ‘bye’ to exit)")
print("-" * 40)
 
while True:
    user_input = input("\nYou: ")
 
    if user_input.lower() in ("quit", "exit", "bye"):
        print("\nGoodbye!")
        break
 
    history.append({
        "role": "user",
        "content": user_input,
    })
 
    stream = ollama.chat(
        model="gemma3:4b",
        messages=history,
        stream=True,
    )
 
    print("\nAI: ", end="")
    response_text = ""
    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        response_text += piece
 
    print()
 
    history.append({
        "role": "assistant",
        "content": response_text,
    })

with open("chat_log.txt", "w") as f:
    for msg in history:
        role = msg["role"].upper()
        content = msg["content"]
        f.write(f"[{role}\n{content}\n\n")

print("Conversation saved to chat_log.txt")