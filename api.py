from fastapi import FastAPI, UploadFile, File, Header, HTTPException
import camelot
import tempfile
import os

app = FastAPI()

API_KEY = "ORGPORTAL_SECRET_KEY"

@app.post("/extract")
async def extract_tables(
    file: UploadFile = File(...),
    x_api_key: str = Header(..., alias="X-API-KEY")
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        pdf_path = tmp.name

    tables = []
    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
    except:
        pass

    if not tables:
        tables = camelot.read_pdf(
            pdf_path,
            pages="all",
            flavor="stream",
            row_tol=10,
            column_tol=10
        )

    extracted_tables = [t.df.values.tolist() for t in tables]

    os.remove(pdf_path)

    return {"tables": extracted_tables}
