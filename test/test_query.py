# test_query.py

from app import ask_question

# Example Question (Change as needed)
question = "What is this document about?"

print("\n🔍 Testing Q&A System...")

answer = ask_question(question)

print("\n✅ Response:\n")
print(answer)
print("\n🔍 Test completed.")