from transformers import pipeline


def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=150)[0]["summary_text"]
    return summary


def main():
    conversation = "The rapid advancement of artificial intelligence (AI) is transforming industries across the globe. From automating mundane tasks to driving innovation in healthcare and finance, AI's impact is undeniable. However, this technological revolution also raises important ethical considerations. Concerns about job displacement, algorithmic bias, and the potential misuse of AI technologies are increasingly prevalent. Experts emphasize the need for responsible AI development and deployment, with a focus on fairness, transparency, and accountability. Collaboration between researchers, policymakers, and industry leaders is crucial to ensure that AI benefits society as a whole while mitigating potential risks."

    # Generate summary of the conversation
    summary = summarize_text(conversation)
    print("Original conversation:")
    print(conversation)
    print("\nGenerated summary:")
    print(summary)


if __name__ == "__main__":
    main()
