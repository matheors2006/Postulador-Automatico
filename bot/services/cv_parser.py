"""Extraccion de texto plano desde archivos PDF (CVs)."""

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrae y concatena el texto de todas las paginas de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF del CV.

    Returns:
        El texto plano concatenado de todas las paginas del documento.
    """
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)
