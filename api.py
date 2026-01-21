from fastapi import FastAPI, UploadFile, File, Header, HTTPException
import camelot
import tempfile
import os

app = FastAPI()

# 🔐 Simple API key (we will improve this later)
API_KEY = "ORGPORTAL_SECRET_KEY"

@app.post("/extract")
async def extract_tables(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    # 🔐 Security check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 1️⃣ Save uploaded PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        pdf_path = tmp.name

    # 2️⃣ YOUR ORIGINAL CAMEL0T LOGIC
    tables = []
    try:
        tables = camelot.read_pdf(
            pdf_path,
            pages="all",
            flavor="lattice"
        )
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

    # 3️⃣ Convert tables to JSON-safe lists
    extracted_tables = [t.df.values.tolist() for t in tables]

    # 4️⃣ Clean up
    os.remove(pdf_path)

    # 5️⃣ Return JSON (replaces print(json.dumps))
    return {
        "tables": extracted_tables
    }
