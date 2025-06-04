from docx import Document
from transformers import pipeline

def ai_extract_section(document_text, disease_name, section_name):
    """Uses AI to extract a specific section for a given disease."""
    qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")
    question = f"What is the {section_name} for {disease_name}?"
    result = qa_pipeline(question=question, context=document_text)
    return result['answer'] if result['answer'] else "Not found."

def advanced_extract_disease_info_ai(document_path, disease_name, sections_to_extract):
    try:
        doc = Document(document_path)
        full_text = "\n".join([p.text for p in doc.paragraphs])
        extracted_data = {}

        for section in sections_to_extract:
            print(f"Extracting '{section}' for '{disease_name}'...")
            extracted_data[section] = ai_extract_section(full_text, disease_name, section)

        return extracted_data

    except FileNotFoundError:
        return f"Error: Document not found at '{document_path}'."
    except Exception as e:
        return f"An error occurred: {e}"

def save_to_file(filename, data):
    """Saves the extracted data to a text file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for section, content in data.items():
                f.write(f"--- {section} ---\n")
                f.write(content + "\n\n")
        print(f"Extracted data saved to '{filename}'")
    except Exception as e:
        print(f"Error saving to file: {e}")

if __name__ == '__main__':
    # document_path = 'your_fitzpatrick_document.docx'  # Replace with the actual path
    document_path = 'C:\DOCS\kodachromes\Fitzpatrick\Fitzpatrick Atlas\Edition 9 - 2021\Part 1 (Sec 1 - 13) - ellen\Section 1\SEC-01 Ed 9.docx'
    disease = 'Psoriasis'  # Example disease
    sections = ["Synopsis", "Codes", "Look For", "Diagnostic Pearls", "Differential Diagnosis & Pitfalls", "Best Tests", "Management Pearls", "Therapy", "Drug Reaction Data", "References"]
    extracted_info = advanced_extract_disease_info_ai(document_path, disease, sections)
    print(f"\nExtracted information for '{disease}':")
    for section, content in extracted_info.items():
        print(f"--- {section} ---\n{content}\n")

    save_to_file(f"ai_fitzpatrick_info_for_{disease.lower().replace(' ', '_')}.txt", extracted_info)

    disease = 'Eczema' # Another example
    extracted_info_eczema = advanced_extract_disease_info_ai(document_path, disease, sections)
    print(f"\nExtracted information for '{disease}':")
    for section, content in extracted_info_eczema.items():
        print(f"--- {section} ---\n{content}\n")

    save_to_file(f"ai_fitzpatrick_info_for_{disease.lower().replace(' ', '_')}.txt", extracted_info_eczema)
    