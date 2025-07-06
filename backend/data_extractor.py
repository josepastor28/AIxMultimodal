import logging
import pandas as pd
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import io
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Table, Text, Title, ListItem
import pytesseract
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self):
        """Initialize the data extractor with Unstructured components."""
        logger.info("✅ DataExtractor initialized successfully")
        
    def extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract tables and text data from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            logger.info(f"🔄 Starting extraction from: {file_path}")
            
            # Extract elements from PDF using Unstructured
            elements = partition_pdf(file_path, include_page_breaks=True)
            
            extracted_data = {
                "tables": [],
                "text_sections": [],
                "charts": [],
                "metadata": {
                    "filename": Path(file_path).name,
                    "total_elements": len(elements)
                }
            }
            
            # Process each element
            for i, element in enumerate(elements):
                if isinstance(element, Table):
                    # Extract table data
                    table_data = self._extract_table_data(element)
                    if table_data:
                        extracted_data["tables"].append({
                            "id": f"table_{i}",
                            "data": table_data,
                            "page": getattr(element, 'metadata', {}).get('page_number', 1)
                        })
                        
                elif isinstance(element, (Text, Title, ListItem)):
                    # Extract text content
                    text_content = str(element)
                    if text_content.strip():
                        # Simple text preprocessing
                        processed_text = self._preprocess_text(text_content)
                        extracted_data["text_sections"].append({
                            "id": f"text_{i}",
                            "content": processed_text,
                            "type": type(element).__name__,
                            "page": getattr(element, 'metadata', {}).get('page_number', 1)
                        })
            
            logger.info(f"✅ Extraction completed. Found {len(extracted_data['tables'])} tables and {len(extracted_data['text_sections'])} text sections")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting data from {file_path}: {str(e)}")
            raise
    
    def _extract_table_data(self, table_element: Table) -> Optional[List[List[str]]]:
        """Extract structured data from a table element."""
        try:
            # Convert table to structured data
            table_text = str(table_element)
            rows = table_text.strip().split('\n')
            
            # Parse table structure
            table_data = []
            for row in rows:
                if row.strip():
                    # Split by common delimiters
                    cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                    if cells:
                        table_data.append(cells)
            
            return table_data if table_data else None
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting table data: {str(e)}")
            return None
    
    def _preprocess_text(self, text: str) -> str:
        """Simple text preprocessing."""
        try:
            # Basic text cleaning
            cleaned_text = text.strip()
            # Remove excessive whitespace
            cleaned_text = ' '.join(cleaned_text.split())
            return cleaned_text
            
        except Exception as e:
            logger.warning(f"⚠️ Error preprocessing text: {str(e)}")
            return text
    
    def extract_charts_with_ocr(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract chart data using OCR for image-based charts.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of extracted chart data
        """
        try:
            logger.info(f"🔄 Starting OCR chart extraction from: {file_path}")
            
            # This would require converting PDF pages to images
            # For now, we'll return a placeholder
            # In a full implementation, you'd use pdf2image or similar
            
            charts = []
            # Placeholder for OCR chart extraction
            # charts.append({
            #     "id": "chart_1",
            #     "type": "bar_chart",
            #     "data": extracted_chart_data,
            #     "page": 1
            # })
            
            logger.info(f"✅ OCR chart extraction completed. Found {len(charts)} charts")
            return charts
            
        except Exception as e:
            logger.error(f"❌ Error in OCR chart extraction: {str(e)}")
            return []
    
    def convert_to_excel(self, extracted_data: Dict[str, Any], output_path: str) -> str:
        """
        Convert extracted data to Excel format.
        
        Args:
            extracted_data: Data extracted from PDF
            output_path: Path to save the Excel file
            
        Returns:
            Path to the created Excel file
        """
        try:
            logger.info(f"🔄 Converting extracted data to Excel: {output_path}")
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Write tables to separate sheets
                for i, table in enumerate(extracted_data.get("tables", [])):
                    if table["data"]:
                        df = pd.DataFrame(table["data"][1:], columns=table["data"][0])
                        sheet_name = f"Table_{i+1}"
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Write text sections to a summary sheet
                if extracted_data.get("text_sections"):
                    text_data = []
                    for text_section in extracted_data["text_sections"]:
                        text_data.append({
                            "ID": text_section["id"],
                            "Type": text_section["type"],
                            "Page": text_section["page"],
                            "Content": text_section["content"][:500] + "..." if len(text_section["content"]) > 500 else text_section["content"]
                        })
                    
                    df_text = pd.DataFrame(text_data)
                    df_text.to_excel(writer, sheet_name="Text_Sections", index=False)
                
                # Write metadata
                metadata = extracted_data.get("metadata", {})
                df_meta = pd.DataFrame([metadata])
                df_meta.to_excel(writer, sheet_name="Metadata", index=False)
            
            logger.info(f"✅ Excel file created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error converting to Excel: {str(e)}")
            raise
    
    def extract_and_convert(self, file_path: str, output_path: str) -> Dict[str, Any]:
        """
        Complete extraction and conversion pipeline.
        
        Args:
            file_path: Path to the PDF file
            output_path: Path to save the Excel file
            
        Returns:
            Dictionary with extraction results and file path
        """
        try:
            # Extract data from PDF
            extracted_data = self.extract_from_pdf(file_path)
            
            # Extract charts with OCR (if needed)
            charts = self.extract_charts_with_ocr(file_path)
            extracted_data["charts"] = charts
            
            # Convert to Excel
            excel_path = self.convert_to_excel(extracted_data, output_path)
            
            return {
                "success": True,
                "excel_file": excel_path,
                "extracted_data": extracted_data,
                "summary": {
                    "tables_found": len(extracted_data["tables"]),
                    "text_sections_found": len(extracted_data["text_sections"]),
                    "charts_found": len(extracted_data["charts"])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in extraction pipeline: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "excel_file": None,
                "extracted_data": None
            }

# Global extractor instance
extractor = DataExtractor() 