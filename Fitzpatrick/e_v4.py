from docx import Document
from transformers import pipeline

def advanced_get_therapy(document_path, disease_name):
    try:
        doc = Document(document_path)
        full_text = "\n".join([p.text for p in doc.paragraphs])

        # Create a question-answering pipeline using a SQuAD-finetuned BERT model
        qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

        # Formulate a question for the AI
        question = f"What is the therapy or treatment for {disease_name}?"

        # Get the AI's answer from the document text
        result = qa_pipeline(question=question, context=full_text)

        if result['answer']:
            return result['answer']
        else:
            return f"Could not find specific therapy information for '{disease_name}' using AI."

    except FileNotFoundError:
        return f"Error: Document not found at '{document_path}'."
    except Exception as e:
        return f"An error occurred: {e}"

def save_to_file(filename, content):
    """Saves the given content to the specified filename."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Results saved to '{filename}'")
    except Exception as e:
        print(f"Error saving to file: {e}")

if __name__ == '__main__':
    # document_path = 'your_fitzpatrick_document.docx'  # Replace with the actual path
    document_path = 'C:\DOCS\kodachromes\Fitzpatrick\Fitzpatrick Atlas\Edition 9 - 2021\Part 1 (Sec 1 - 13) - ellen\Section 1\SEC-01 Ed 9.docx'
    disease = 'Psoriasis'  # Example disease to search for
    therapy = advanced_get_therapy(document_path, disease)
    print(f"AI-extracted therapy for '{disease}':\n{therapy}")
    save_to_file(f"ai_therapy_for_{disease.lower().replace(' ', '_')}.txt", therapy)

    disease = 'Eczema' # Another example
    therapy = advanced_get_therapy(document_path, disease)
    print(f"\nAI-extracted therapy for '{disease}':\n{therapy}")
    save_to_file(f"ai_therapy_for_{disease.lower().replace(' ', '_')}.txt", therapy)
    