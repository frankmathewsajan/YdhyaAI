from transformers import pipeline

summarizer = pipeline("summarization")
long_text = "Recursion is a method in computer science where a function calls itself..."
summarized_text = summarizer(long_text, max_length=50, min_length=25, do_sample=True)[0]['summary_text']
print(summarized_text)
