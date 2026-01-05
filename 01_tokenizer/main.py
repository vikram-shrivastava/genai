import tiktoken
enc=tiktoken.encoding_for_model("gpt-3.5-turbo")
# text="I am Vikram Shrivastav"
# tokens=enc.encode(text)
# print(f"Tokens: {tokens}")
token=[40, 1097, 29476, 2453, 1443, 77467, 561, 402]
decoded_text=enc.decode(token)
print(f"Decoded text: {decoded_text}")