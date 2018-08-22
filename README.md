# Receipt Reader

Receipt reader and information extracter project using OpenCV and tesseract.
For now the script extracts date, amount, receipt number and name of the place from the receipt and returns a JSON.

# Example Run:

```bash
python receiptReader.py [-i|-image] image_path 
```

# Feature to be added: 
- Fix turkish character problem.
- Improve accuracy of OCR.
- Cleaning up extracted data.
- Export parsed data to csv.
- Processing multiple images in one run.
- Create a Restful API of this script (using Flask or Django) that will return JSON or directly Excel Spreadsheet.
- Build mobile app (iOS and Android).
