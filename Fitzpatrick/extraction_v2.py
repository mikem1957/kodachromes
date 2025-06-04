from docx import Document

def get_therapy(document_path, disease_name):
    try:
        doc = Document(document_path)
        found_disease = False
        therapy_started = False
        therapy_text = []

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()

            # Check if we've found the disease section
            if disease_name.lower() in text.lower():
                found_disease = True
                continue  # Move to the next paragraph to find therapy

            if found_disease:
                # Look for therapy-related keywords
                if any(keyword.lower() in text.lower() for keyword in ["Treatment", "Therapy", "Management"]):
                    therapy_started = True
                    continue # Start collecting therapy from the next paragraph

                if therapy_started and text:
                    # Assuming therapy continues until a new major heading or the end of the disease section
                    # You might need more sophisticated logic here based on your document's structure
                    if not any(keyword.lower() in text.lower() for keyword in ["Diagnosis", "Etiology", "Clinical Presentation"]): # Example of stopping conditions
                        therapy_text.append(text)
                    else:
                        break # Stop if a new major section of a different type is found

        if therapy_text:
            return "\n".join(therapy_text)
        else:
            return f"Therapy information not found for '{disease_name}'."

    except FileNotFoundError:
        return f"Error: Document not found at '{document_path}'."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    document_path = 'C:\DOCS\kodachromes\Fitzpatrick\Fitzpatrick Atlas\Edition 9 - 2021\Part 1 (Sec 1 - 13) - ellen\Section 1\SEC-01 Ed 9.docx'

    disease = 'Psoriasis'  # Example disease to search for
    therapy = get_therapy(document_path, disease)
    print(f"Therapy for '{disease}':\n{therapy}")

    disease = 'Eczema' # Another example
    therapy = get_therapy(document_path, disease)
    print(f"\nTherapy for '{disease}':\n{therapy}")
