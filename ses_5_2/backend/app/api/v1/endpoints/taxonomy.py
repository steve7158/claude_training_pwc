from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.taxonomy import Icd10Code, LoincCode, NdcDrug, SnomedCode
from app.schemas.taxonomy import Icd10CodeOut, LoincCodeOut, NdcDrugOut, SnomedCodeOut

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"], dependencies=[Depends(get_current_user)])


@router.get("/loinc/{code}", response_model=LoincCodeOut)
def get_loinc(code: str, db: Session = Depends(get_db)):
    row = db.get(LoincCode, code)
    if row is None:
        raise HTTPException(status_code=404, detail="LOINC code not found")
    return row


@router.get("/loinc", response_model=list[LoincCodeOut])
def list_loinc(db: Session = Depends(get_db)):
    return db.query(LoincCode).order_by(LoincCode.loinc_code).all()


@router.get("/ndc/{code}", response_model=NdcDrugOut)
def get_ndc(code: str, db: Session = Depends(get_db)):
    row = db.get(NdcDrug, code)
    if row is None:
        raise HTTPException(status_code=404, detail="NDC code not found")
    return row


@router.get("/ndc", response_model=list[NdcDrugOut])
def list_ndc(db: Session = Depends(get_db)):
    return db.query(NdcDrug).order_by(NdcDrug.ndc_code).all()


@router.get("/icd10/{code}", response_model=Icd10CodeOut)
def get_icd10(code: str, db: Session = Depends(get_db)):
    row = db.get(Icd10Code, code.upper())
    if row is None:
        raise HTTPException(status_code=404, detail="ICD-10 code not found")
    return row


@router.get("/icd10", response_model=list[Icd10CodeOut])
def list_icd10(db: Session = Depends(get_db)):
    return db.query(Icd10Code).order_by(Icd10Code.code).all()


@router.get("/snomed/{snomed_id}", response_model=SnomedCodeOut)
def get_snomed(snomed_id: str, db: Session = Depends(get_db)):
    row = db.get(SnomedCode, snomed_id)
    if row is None:
        raise HTTPException(status_code=404, detail="SNOMED code not found")
    return row


@router.get("/snomed", response_model=list[SnomedCodeOut])
def list_snomed(db: Session = Depends(get_db)):
    return db.query(SnomedCode).order_by(SnomedCode.snomed_id).all()
