# backend/app/api/api_v1/endpoints/pdf_report.py

"""PDF report generation endpoint.

Generates a PDF using ReportLab based on the selected sections sent in the request body.
The endpoint returns the PDF as a binary stream with appropriate headers for download.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO

# Import the user dependency to ensure only authenticated users can generate reports
from app.api.deps import get_current_user
from app.schemas.user import UserBase

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter()


class ReportRequest(BaseModel):
    include_kpis: bool = True
    include_recent_cases: bool = True
    include_risk_profiles: bool = True
    # Future extensions could add filters for date ranges, stations, etc.


def _build_pdf(data: ReportRequest) -> BytesIO:
    """Create a PDF document in memory based on the requested sections.
    This placeholder implementation generates static example tables.
    In a real system you would query the database for the actual data.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title = Paragraph("KSP Crime Intelligence Report", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    if data.include_kpis:
        kpi_data = [
            ["Total Cases (Q2 2026)", "2,042"],
            ["Heinous Offences", "142"],
            ["Repeat Suspects", "394"],
            ["Pending Case Files", "842"]
        ]
        tbl = Table([["Metric", "Value"]] + kpi_data, hAlign="LEFT")
        tbl.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ])
        )
        elements.append(Paragraph("Key Performance Indicators", styles["Heading2"]))
        elements.append(tbl)
        elements.append(Spacer(1, 12))

    if data.include_recent_cases:
        recent_cases = [
            ["FIR:100120257202500001", "2025-05-20", "Body Offences", "Chargesheeted"],
            ["FIR:100020027202600001", "2026-06-01", "Property Offences", "Under Investigation"],
            ["FIR:300040077202600001", "2026-06-10", "Property Offences", "Under Investigation"]
        ]
        tbl = Table([
            ["Case ID", "Date", "Crime Head", "Status"]
        ] + recent_cases, hAlign="LEFT")
        tbl.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ])
        )
        elements.append(Paragraph("Recent Cases", styles["Heading2"]))
        elements.append(tbl)
        elements.append(Spacer(1, 12))

    if data.include_risk_profiles:
        risk_profiles = [
            ["Ravi alias Kariya", "31", "84%"],
            ["Ganesh alias Gani", "26", "76%"],
            ["Imran Khan", "24", "72%"]
        ]
        tbl = Table([
            ["Name", "Age", "Risk %"]
        ] + risk_profiles, hAlign="LEFT")
        tbl.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ])
        )
        elements.append(Paragraph("Habitual Offender Risk Profiles", styles["Heading2"]))
        elements.append(tbl)
        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer


@router.post("/pdf", tags=["report"])
def generate_report(payload: ReportRequest, current_user: UserBase = Depends(get_current_user)):
    """Generate a PDF report for the current user.
    The report sections are controlled by the request payload.
    """
    try:
        pdf_bytes = _build_pdf(payload)
        filename = f"KSP_Report_{current_user.email.replace('@', '_')}.pdf"
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
