# backend/app/api/api_v1/endpoints/pdf_report.py

"""PDF report generation endpoint — Investigator, Analyst, Supervisor only.

Pulls live data from PostgreSQL (CaseMaster, Accused) and generates
a formatted PDF with ReportLab. Returns as binary stream download.
"""

from datetime import date
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_user, RoleChecker
from app.schemas.user import UserBase
from app.core.database import get_db
from app.models.ksp_models import CaseMaster, Accused

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

router = APIRouter()

# Investigators and above can generate reports
report_access = RoleChecker(["Investigator", "Analyst", "Supervisor"])


class ReportRequest(BaseModel):
    include_kpis: bool = True
    include_recent_cases: bool = True
    include_risk_profiles: bool = True


def _build_pdf(data: ReportRequest, db: Session, user_email: str) -> BytesIO:
    """Build PDF from live DB data using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "KSPTitle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "KSPSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=16,
    )
    heading_style = ParagraphStyle(
        "KSPHeading",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#1a365d"),
        spaceBefore=14,
        spaceAfter=6,
    )

    tbl_header_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])

    elements = []

    # Title block
    elements.append(Paragraph("Karnataka State Police", title_style))
    elements.append(Paragraph("Crime Intelligence Platform — Intelligence Report", subtitle_style))
    elements.append(Paragraph(
        f"Generated: {date.today().strftime('%d %B %Y')}  |  Officer: {user_email}",
        subtitle_style,
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a365d")))
    elements.append(Spacer(1, 12))

    # ── KPIs from real DB ──────────────────────────────────────
    if data.include_kpis:
        total_cases = db.query(func.count(CaseMaster.CaseMasterID)).scalar() or 0
        pending = db.query(func.count(CaseMaster.CaseMasterID)).filter(
            CaseMaster.CaseStatusID == 1
        ).scalar() or 0
        total_accused = db.query(func.count(Accused.AccusedMasterID)).scalar() or 0
        heinous = db.query(func.count(CaseMaster.CaseMasterID)).filter(
            CaseMaster.GravityOffenceID == 1
        ).scalar() or 0

        kpi_rows = [
            ["Total Registered Cases", str(total_cases)],
            ["Heinous Offences", str(heinous)],
            ["Total Accused Profiles", str(total_accused)],
            ["Pending Investigations", str(pending)],
        ]
        tbl = Table([["Metric", "Value"]] + kpi_rows, colWidths=[4 * inch, 2.5 * inch])
        tbl.setStyle(tbl_header_style)
        elements.append(Paragraph("Key Performance Indicators", heading_style))
        elements.append(tbl)
        elements.append(Spacer(1, 10))

    # ── Recent Cases from real DB ──────────────────────────────
    if data.include_recent_cases:
        recent = db.query(CaseMaster).order_by(
            CaseMaster.CrimeRegisteredDate.desc()
        ).limit(10).all()
        case_rows = [
            [c.CrimeNo or c.CaseNo, str(c.CrimeRegisteredDate), str(c.CrimeMajorHeadID or "—"), str(c.CaseStatusID or "—")]
            for c in recent
        ]
        tbl = Table(
            [["Case / FIR No.", "Registered", "Crime Head ID", "Status ID"]] + case_rows,
            colWidths=[2.8 * inch, 1.2 * inch, 1.3 * inch, 1.2 * inch],
        )
        tbl.setStyle(tbl_header_style)
        elements.append(Paragraph("Recent Cases (Latest 10)", heading_style))
        elements.append(tbl)
        elements.append(Spacer(1, 10))

    # ── Top Accused (repeat offenders) from real DB ────────────
    if data.include_risk_profiles:
        from sqlalchemy import desc
        top_accused = (
            db.query(
                Accused.AccusedName,
                Accused.AgeYear,
                func.count(Accused.CaseMasterID).label("case_count"),
            )
            .group_by(Accused.AccusedName, Accused.AgeYear)
            .order_by(desc("case_count"))
            .limit(10)
            .all()
        )
        profile_rows = [
            [a.AccusedName or "Unknown", str(a.AgeYear or "—"), str(a.case_count)]
            for a in top_accused
        ]
        tbl = Table(
            [["Name", "Age", "No. of Cases"]] + profile_rows,
            colWidths=[3.5 * inch, 1 * inch, 2 * inch],
        )
        tbl.setStyle(tbl_header_style)
        elements.append(Paragraph("Top Repeat Offender Profiles", heading_style))
        elements.append(tbl)

    doc.build(elements)
    buffer.seek(0)
    return buffer


@router.post("/pdf", tags=["report"])
def generate_report(
    payload: ReportRequest,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(report_access),
):
    """Generate a PDF report from live DB data.

    Role required: Investigator, Analyst, or Supervisor.
    """
    try:
        pdf_bytes = _build_pdf(payload, db, current_user.email)
        filename = f"KSP_Intel_Report_{date.today().isoformat()}.pdf"
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
