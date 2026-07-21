
# this file is just for experimenting with ollama api.
import json
import os
 
import ollama
#import streamlit as st

MODEL_NAME = "gemma3:4b"

 
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
        model=MODEL_NAME,
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
    ps = ollama.ps()
    model = next(
        (model for model in ps.models if model.model == MODEL_NAME),
        None,
    )
    if model is None:
        raise RuntimeError(f"{MODEL_NAME} is not currently loaded")
    tokens_remaining = model.context_length - chunk.eval_count -chunk.prompt_eval_count
    print(f"Context length: {model.context_length}")
    print(f"tokens remaining : {tokens_remaining}")
  
    history.append({
        "role": "assistant",
        "content": response_text,
    })
 