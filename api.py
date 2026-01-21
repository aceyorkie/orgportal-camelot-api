from fastapi import FastAPI, UploadFile, File, Header, HTTPException
import camelot
import tempfile
import os
from PyPDF2 import PdfReader

app = FastAPI()

API_KEY = "ORGPORTAL_SECRET_KEY"

@app.post("/extract")
async def extract_tables(
    file: UploadFile = File(...),
    x_api_key: str = Header(..., alias="X-API-KEY")
):
    # 🔐 Security check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 1️⃣ Save uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        pdf_path = tmp.name

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    all_tables = []

    # 2️⃣ Extract tables page-by-page
    for page in range(1, total_pages + 1):
        try:
            tables = camelot.read_pdf(
                pdf_path,
                pages=str(page),
                flavor="lattice"
            )
        except:
            tables = []

        if not tables:
            tables = camelot.read_pdf(
                pdf_path,
                pages=str(page),
                flavor="stream",
                row_tol=10,
                column_tol=10
            )

        for table in tables:
            all_tables.append(table.df.values.tolist())

    # 3️⃣ Merge continuation tables across pages
    merged_tables = []

    for table in all_tables:
        if not merged_tables:
            merged_tables.append(table)
            continue

        prev_table = merged_tables[-1]

        # If same column count, assume continuation
        if len(table[0]) == len(prev_table[0]):
            merged_tables[-1].extend(table)
        else:
            merged_tables.append(table)

    # 4️⃣ Clean up temp file
    os.remove(pdf_path)

    # 5️⃣ Return merged tables
    return {
        "tables": merged_tables
    }
