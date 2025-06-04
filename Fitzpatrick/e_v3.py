from docx import Document

def get_therapy(document_path, disease_name):
    try:
        doc = Document(document_path)
        found_disease = False
        therapy_started = False
        therapy_text = []

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()

            if disease_name.lower() in text.lower():
                found_disease = True
                continue

            if found_disease:
                if any(keyword.lower() in text.lower() for keyword in ["Treatment", "Therapy", "Management"]):
                    therapy_started = True
                    continue

                if therapy_started and text:
                    if not any(keyword.lower() in text.lower() for keyword in ["Diagnosis", "Etiology", "Clinical Presentation"]):
                        therapy_text.append(text)
                    else:
                        break

        if therapy_text:
            return "\n".join(therapy_text)
        else:
            return f"Therapy information not found for '{disease_name}'."

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
    document_path = 'C:\DOCS\kodachromes\Fitzpatrick\Fitzpatrick Atlas\Edition 9 - 2021\Part 1 (Sec 1 - 13) - ellen\Section 1\SEC-01 Ed 9.docx'
    disease = 'Psoriasis'  # Example disease to search for
    therapy = get_therapy(document_path, disease)
    print(f"Therapy for '{disease}':\n{therapy}")
    save_to_file(f"therapy_for_{disease.lower().replace(' ', '_')}.txt", therapy)

    disease = 'Eczema' # Another example
    therapy = get_therapy(document_path, disease)
    print(f"\nTherapy for '{disease}':\n{therapy}")
    save_to_file(f"therapy_for_{disease.lower().replace(' ', '_')}.txt", therapy)
