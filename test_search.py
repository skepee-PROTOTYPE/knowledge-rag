from wiki_rag import search_wikipedia

# Test the function
question = "What is Machine Learning?"
print(f"Searching for: {question}")
results = search_wikipedia(question)
print(f"Results: {results}")
print(f"Type: {type(results)}")
print(f"Length: {len(results)}")
print(f"Bool: {bool(results)}")
