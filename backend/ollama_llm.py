import ollama

# modellll
model_name = "llama3.1:8b"

query = """
[{'policy': 'Content Security Policy', 'status': 'No'}, {'policy': 'Strict Transport Security', 'status': 'No'}, {'policy': 'X-Content-Type-Options', 'status': 'No'}, {'policy': 'X-Frame-Options', 'status': 'Yes'}, {'policy': 'X-XSS-Protection', 'status': 'Yes'}]


I hear that you summarize the above structure understandable. What should users understand from here. Afterwards, you can offer the substance mine solution suggestions etc.

The content you will write should consist of the following headings:

1-summary
2-risks
3-protections
4-recomedations

```

"""


response = ollama.chat(model=model_name, messages=[{"role": "user", "content": query}])

print(response["message"]["content"])
