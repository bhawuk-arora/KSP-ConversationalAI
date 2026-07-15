# backend/app/models/ksp_models.py
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Numeric, Text, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, CheckConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base

# =========================================================================
# 1. Administrative & Demographic Master Tables
# =========================================================================

class State(Base):
    __tablename__ = "state"

    StateID = Column(Integer, primary_key=True)
    StateName = Column(String(100), nullable=False)
    NationalityID = Column(Integer, default=1)
    Active = Column(Boolean, default=True)

    districts = relationship("District", back_populates="state")
    units = relationship("Unit", back_populates="state")
    courts = relationship("Court", back_populates="state")


class District(Base):
    __tablename__ = "district"

    DistrictID = Column(Integer, primary_key=True)
    DistrictName = Column(String(100), nullable=False)
    StateID = Column(Integer, ForeignKey("state.StateID"))
    Active = Column(Boolean, default=True)

    state = relationship("State", back_populates="districts")
    courts = relationship("Court", back_populates="district")
    units = relationship("Unit", back_populates="district")
    employees = relationship("Employee", back_populates="district")


class Court(Base):
    __tablename__ = "court"

    CourtID = Column(Integer, primary_key=True)
    CourtName = Column(String(255), nullable=False)
    DistrictID = Column(Integer, ForeignKey("district.DistrictID"))
    StateID = Column(Integer, ForeignKey("state.StateID"))
    Active = Column(Boolean, default=True)

    district = relationship("District", back_populates="courts")
    state = relationship("State", back_populates="courts")
    cases = relationship("CaseMaster", back_populates="court")


class UnitType(Base):
    __tablename__ = "unittype"

    UnitTypeID = Column(Integer, primary_key=True)
    UnitTypeName = Column(String(100), nullable=False)
    CityDistState = Column(String(50))
    Hierarchy = Column(Integer)
    Active = Column(Boolean, default=True)

    units = relationship("Unit", back_populates="unit_type")


class Unit(Base):
    __tablename__ = "unit"

    UnitID = Column(Integer, primary_key=True)
    UnitName = Column(String(150), nullable=False)
    TypeID = Column(Integer, ForeignKey("unittype.UnitTypeID"))
    ParentUnit = Column(Integer, ForeignKey("unit.UnitID"))
    NationalityID = Column(Integer, default=1)
    StateID = Column(Integer, ForeignKey("state.StateID"))
    DistrictID = Column(Integer, ForeignKey("district.DistrictID"))
    Active = Column(Boolean, default=True)

    unit_type = relationship("UnitType", back_populates="units")
    state = relationship("State", back_populates="units")
    district = relationship("District", back_populates="units")
    
    parent = relationship("Unit", remote_side=[UnitID], backref="sub_units")
    employees = relationship("Employee", back_populates="unit")
    cases = relationship("CaseMaster", back_populates="station")


class Rank(Base):
    __tablename__ = "rank"

    RankID = Column(Integer, primary_key=True)
    RankName = Column(String(100), nullable=False)
    Hierarchy = Column(Integer)
    Active = Column(Boolean, default=True)

    employees = relationship("Employee", back_populates="rank")


class Designation(Base):
    __tablename__ = "designation"

    DesignationID = Column(Integer, primary_key=True)
    DesignationName = Column(String(100), nullable=False)
    Active = Column(Boolean, default=True)
    SortOrder = Column(Integer)

    employees = relationship("Employee", back_populates="designation")


class Employee(Base):
    __tablename__ = "employee"

    EmployeeID = Column(Integer, primary_key=True)
    DistrictID = Column(Integer, ForeignKey("district.DistrictID"))
    UnitID = Column(Integer, ForeignKey("unit.UnitID"))
    RankID = Column(Integer, ForeignKey("rank.RankID"))
    DesignationID = Column(Integer, ForeignKey("designation.DesignationID"))
    KGID = Column(String(50), unique=True, nullable=False)
    FirstName = Column(String(100), nullable=False)
    EmployeeDOB = Column(Date)
    GenderID = Column(Integer)
    BloodGroupID = Column(Integer)
    PhysicallyChallenged = Column(Boolean, default=False)
    AppointmentDate = Column(Date)

    district = relationship("District", back_populates="employees")
    unit = relationship("Unit", back_populates="employees")
    rank = relationship("Rank", back_populates="employees")
    designation = relationship("Designation", back_populates="employees")
    cases = relationship("CaseMaster", back_populates="investigator")


class CasteMaster(Base):
    __tablename__ = "castemaster"

    caste_master_id = Column(Integer, primary_key=True)
    caste_master_name = Column(String(100), nullable=False)


class ReligionMaster(Base):
    __tablename__ = "religionmaster"

    ReligionID = Column(Integer, primary_key=True)
    ReligionName = Column(String(100), nullable=False)


class OccupationMaster(Base):
    __tablename__ = "occupationmaster"

    OccupationID = Column(Integer, primary_key=True)
    OccupationName = Column(String(150), nullable=False)


class CaseCategory(Base):
    __tablename__ = "casecategory"

    CaseCategoryID = Column(Integer, primary_key=True)
    LookupValue = Column(String(50), nullable=False)


class GravityOffence(Base):
    __tablename__ = "gravityoffence"

    GravityOffenceID = Column(Integer, primary_key=True)
    LookupValue = Column(String(50), nullable=False)


class CaseStatusMaster(Base):
    __tablename__ = "casestatusmaster"

    CaseStatusID = Column(Integer, primary_key=True)
    CaseStatusName = Column(String(100), nullable=False)

# =========================================================================
# 2. Legal Acts, Sections & Offence Classifications
# =========================================================================

class CrimeHead(Base):
    __tablename__ = "crimehead"

    CrimeHeadID = Column(Integer, primary_key=True)
    CrimeGroupName = Column(String(150), nullable=False)
    Active = Column(Boolean, default=True)

    sub_heads = relationship("CrimeSubHead", back_populates="crime_head")
    cases = relationship("CaseMaster", back_populates="major_head")


class CrimeSubHead(Base):
    __tablename__ = "crimesubhead"

    CrimeSubHeadID = Column(Integer, primary_key=True)
    CrimeHeadID = Column(Integer, ForeignKey("crimehead.CrimeHeadID"))
    CrimeHeadName = Column(String(150), nullable=False)
    SeqID = Column(Integer)

    crime_head = relationship("CrimeHead", back_populates="sub_heads")
    cases = relationship("CaseMaster", back_populates="minor_head")


class Act(Base):
    __tablename__ = "act"

    ActCode = Column(String(50), primary_key=True)
    ActDescription = Column(String(255), nullable=False)
    ShortName = Column(String(50))
    Active = Column(Boolean, default=True)

    sections = relationship("Section", back_populates="act")


class Section(Base):
    __tablename__ = "section"

    ActCode = Column(String(50), ForeignKey("act.ActCode"), primary_key=True)
    SectionCode = Column(String(50), primary_key=True)
    SectionDescription = Column(Text)
    Active = Column(Boolean, default=True)

    act = relationship("Act", back_populates="sections")


class CrimeHeadActSection(Base):
    __tablename__ = "crimeheadactsection"

    CrimeHeadID = Column(Integer, ForeignKey("crimehead.CrimeHeadID"), primary_key=True)
    ActCode = Column(String(50), primary_key=True)
    SectionCode = Column(String(50), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["ActCode", "SectionCode"],
            ["section.ActCode", "section.SectionCode"]
        ),
    )

# =========================================================================
# 3. Case Records & Associated Entities
# =========================================================================

class CaseMaster(Base):
    __tablename__ = "casemaster"

    CaseMasterID = Column(Integer, primary_key=True)
    CrimeNo = Column(String(50), unique=True, nullable=False)
    CaseNo = Column(String(50), nullable=False)
    CrimeRegisteredDate = Column(Date, nullable=False)
    PolicePersonID = Column(Integer, ForeignKey("employee.EmployeeID"))
    PoliceStationID = Column(Integer, ForeignKey("unit.UnitID"))
    CaseCategoryID = Column(Integer, ForeignKey("casecategory.CaseCategoryID"))
    GravityOffenceID = Column(Integer, ForeignKey("gravityoffence.GravityOffenceID"))
    CrimeMajorHeadID = Column(Integer, ForeignKey("crimehead.CrimeHeadID"))
    CrimeMinorHeadID = Column(Integer, ForeignKey("crimesubhead.CrimeSubHeadID"))
    CaseStatusID = Column(Integer, ForeignKey("casestatusmaster.CaseStatusID"))
    CourtID = Column(Integer, ForeignKey("court.CourtID"))
    IncidentFromDate = Column(DateTime)
    IncidentToDate = Column(DateTime)
    InfoReceivedPSDate = Column(DateTime)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    BriefFacts = Column(Text)

    investigator = relationship("Employee", back_populates="cases")
    station = relationship("Unit", back_populates="cases")
    court = relationship("Court", back_populates="cases")
    major_head = relationship("CrimeHead", back_populates="cases")
    minor_head = relationship("CrimeSubHead", back_populates="cases")

    complainants = relationship("ComplainantDetails", back_populates="case", cascade="all, delete-orphan")
    victims = relationship("Victim", back_populates="case", cascade="all, delete-orphan")
    accused_persons = relationship("Accused", back_populates="case", cascade="all, delete-orphan")
    act_section_assocs = relationship("ActSectionAssociation", back_populates="case", cascade="all, delete-orphan")
    arrests = relationship("ArrestSurrender", back_populates="case", cascade="all, delete-orphan")
    chargesheets = relationship("ChargesheetDetails", back_populates="case", cascade="all, delete-orphan")


class ComplainantDetails(Base):
    __tablename__ = "complainantdetails"

    ComplainantID = Column(Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("casemaster.CaseMasterID", ondelete="CASCADE"))
    ComplainantName = Column(String(255), nullable=False)
    AgeYear = Column(Integer)
    OccupationID = Column(Integer, ForeignKey("occupationmaster.OccupationID"))
    ReligionID = Column(Integer, ForeignKey("religionmaster.ReligionID"))
    CasteID = Column(Integer, ForeignKey("castemaster.caste_master_id"))
    GenderID = Column(Integer)

    case = relationship("CaseMaster", back_populates="complainants")


class Victim(Base):
    __tablename__ = "victim"

    VictimMasterID = Column(Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("casemaster.CaseMasterID", ondelete="CASCADE"))
    VictimName = Column(String(255), nullable=False)
    AgeYear = Column(Integer)
    GenderID = Column(Integer)
    VictimPolice = Column(String(10))

    case = relationship("CaseMaster", back_populates="victims")


class Accused(Base):
    __tablename__ = "accused"

    AccusedMasterID = Column(Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("casemaster.CaseMasterID", ondelete="CASCADE"))
    AccusedName = Column(String(255), nullable=False)
    AgeYear = Column(Integer)
    GenderID = Column(String(10))  # Updated to VARCHAR to fit actual 'M', 'F', 'T' values
    PersonID = Column(String(10), nullable=False)

    case = relationship("CaseMaster", back_populates="accused_persons")
    arrests = relationship("ArrestSurrender", back_populates="accused", cascade="all, delete-orphan")


class ActSectionAssociation(Base):
    __tablename__ = "actsectionassociation"

    CaseMasterID = Column(Integer, ForeignKey("casemaster.CaseMasterID", ondelete="CASCADE"), primary_key=True)
    ActID = Column(String(50), primary_key=True)
    SectionID = Column(String(50), primary_key=True)
    ActOrderID = Column(Integer)
    SectionOrderID = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ["ActID", "SectionID"],
            ["section.ActCode", "section.SectionCode"]
        ),
    )

    case = relationship("CaseMaster", back_populates="act_section_assocs")


class ArrestSurrender(Base):
    __tablename__ = "arrestsurrender"

    ArrestSurrenderID = Column(Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("casemaster.CaseMasterID", ondelete="CASCADE"))
    ArrestSurrenderTypeID = Column(Integer)
    ArrestSurrenderDate = Column(Date, nullable=False)
    ArrestSurrenderStateId = Column(Integer, ForeignKey("state.StateID"))
    ArrestSurrenderDistrictId = Column(Integer, ForeignKey("district.DistrictID"))
    PoliceStationID = Column(Integer, ForeignKey("unit.UnitID"))
    IOID = Column(Integer, ForeignKey("employee.EmployeeID"))
    CourtID = Column(Integer, ForeignKey("court.CourtID"))
    AccusedMasterID = Column(Integer, ForeignKey("accused.AccusedMasterID", ondelete="CASCADE"))
    IsAccused = Column(Boolean, default=True)
    IsComplainantAccused = Column(Boolean, default=False)

    case = relationship("CaseMaster", back_populates="arrests")
    accused = relationship("Accused", back_populates="arrests")


class ChargesheetDetails(Base):
    __tablename__ = "chargesheetdetails"

    CSID = Column(Integer, primary_key=True)
    CaseMasterID = Column(Integer, ForeignKey("casemaster.CaseMasterID", ondelete="CASCADE"))
    csdate = Column(DateTime, nullable=False)
    cstype = Column(String(1)) # A, B, C
    PolicePersonID = Column(Integer, ForeignKey("employee.EmployeeID"))

    __table_args__ = (
        CheckConstraint("cstype IN ('A', 'B', 'C')", name="check_cstype"),
    )

    case = relationship("CaseMaster", back_populates="chargesheets")
