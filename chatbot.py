
# this file is just for experimenting with ollama api.
import json
import os
 
import ollama
#import streamlit as st

 
 
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

 
    print(f"\nEval count: {chunk.eval_count}, Prompt eval count: {chunk.prompt_eval_count}")
  
    history.append({
        "role": "assistant",
        "content": response_text,
    })
 