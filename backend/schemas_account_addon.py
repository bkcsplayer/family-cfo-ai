# Canadian Account Schemas
class CanadianAccountCreate(BaseModel):
    account_type: str  # TFSA, RRSP, RESP, FHSA
    institution: str
    balance: float
    contribution_room: float

class CanadianAccountUpdate(BaseModel):
    account_type: Optional[str] = None
    institution: Optional[str] = None
    balance: Optional[float] = None
    contribution_room: Optional[float] = None
