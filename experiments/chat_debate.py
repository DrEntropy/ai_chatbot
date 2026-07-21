import ollama
 
 
historyPro = [
    {
        "role": "system",
        "content": "You are a proponent of the proposition: \n"
        "Bayesian statistics is superior to frequentist statistics."
        "There will be 5 total turns in the debate."
        "Be concise during your turns."
    }
]

historyCon = [
    {
        "role": "system",
        "content": "You are a opponent of the proposition: \n"
        "Bayesian statistics is superior to frequentist statistics."
        "The proponent will make their case first."
        "Be concise during your turns."
    }
]
 
print("Debate will begin!")
print("-" * 40)
 
number_turns = 5

# initial user message to kick off the debate 
user_input = "The debate will begin. Proponent, make your case."
print(user_input)
historyPro.append({
    "role": "user",
    "content": user_input,
})
historyCon.append({
    "role": "user",
    "content": user_input,
})

for turn in range(number_turns):
    print(f"Turn {turn + 1}:")
    print("-" * 40)


    # Proponent's turn
    stream = ollama.chat(
        model="gemma3:4b",
        messages=historyPro,
        stream=True,
    )

    print("\nProponent: ", end="")
    response_text = ""
    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        response_text += piece
    print()

    historyPro.append({
        "role": "assistant",
        "content": response_text,
    })
    # append propoent's response as 
    # user message for opponent's turn
    historyCon.append({
        "role": "user",
        "content": response_text,
    })

    # Opponent's turn
    stream = ollama.chat(
        model="gemma3:4b",
        messages=historyCon,
        stream=True,
    )

    print("\nOpponent: ", end="")
    response_text = ""
    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        response_text += piece
    print()

    historyCon.append({
        "role": "assistant",
        "content": response_text,
    })
    # append opponent's response as 
    # user message for propoent's turn
    historyPro.append({
        "role": "user",
        "content": response_text,
    })

# Save the debate as a unified transcript
with open("debate_transcript.txt", "w", encoding="utf-8") as f:
    f.write("Debate Transcript\n")
    f.write("=" * 40 + "\n\n")

    # historyPro already contains both sides in chronological order:
    # assistant messages are Pro and user messages after the prompt are Con.
    for msg in historyPro[2:]:
        speaker = "Pro" if msg["role"] == "assistant" else "Con"
        f.write(f"{speaker}:\n{msg['content'].strip()}\n\n")

print("Debate transcript saved to debate_transcript.txt")