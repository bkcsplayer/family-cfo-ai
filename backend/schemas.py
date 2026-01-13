from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from enum import Enum

# Enums
class UserRole(str, Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"

class TransactionStatus(str, Enum):
    PENDING = "Pending"
    POSTED = "Posted"

class AssetType(str, Enum):
    REAL_ESTATE = "RealEstate"
    VEHICLE = "Vehicle"
    STOCK = "Stock"

class SubscriptionCycle(str, Enum):
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class AccountType(str, Enum):
    TFSA = "TFSA"
    RRSP = "RRSP"
    RESP = "RESP"
    FHSA = "FHSA"

class InsuranceType(str, Enum):
    AUTO = "Auto"
    HOME = "Home"
    LIFE = "Life"
    HEALTH = "Health"
    DISABILITY = "Disability"

# v3.0 New Enums
class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    ASSET = "asset"
    LIABILITY = "liability"

class RefreshSource(str, Enum):
    MANUAL = "manual"
    STOCK_API = "stock_api"
    CRYPTO_API = "crypto_api"
    REAL_ESTATE_API = "real_estate_api"

class PaymentFrequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"

class ParsingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# User Schemas
class UserBase(BaseModel):
    username: str
    display_name: str
    role: UserRole = UserRole.VIEWER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    status: str
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionBase(BaseModel):
    date: date
    amount: float
    merchant: str
    category: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING
    source: str = "manual"  # manual, document, email
    is_amortized: bool = False
    linked_subscription_id: Optional[int] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    ai_confidence: Optional[float] = None

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    status: Optional[TransactionStatus] = None
    source: Optional[str] = None
    is_amortized: Optional[bool] = None
    linked_subscription_id: Optional[int] = None
    notes: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    ai_confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Asset Schemas
class AssetBase(BaseModel):
    name: str
    type: AssetType
    value: float
    equity: Optional[float] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionBase(BaseModel):
    name: str
    cost: float
    cycle: SubscriptionCycle
    next_due_date: date
    merchant_keyword: Optional[str] = None
    status: str = "Active"
    notes: Optional[str] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Canadian Account Schemas
class CanadianAccountBase(BaseModel):
    type: AccountType
    institution: str
    holder: str
    current_value: float
    contribution_room: float

class CanadianAccountCreate(CanadianAccountBase):
    pass

class CanadianAccountUpdate(BaseModel):
    type: Optional[AccountType] = None
    institution: Optional[str] = None
    holder: Optional[str] = None
    current_value: Optional[float] = None
    contribution_room: Optional[float] = None

class CanadianAccountResponse(CanadianAccountBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Insurance Policy Schemas
class InsurancePolicyBase(BaseModel):
    provider: str
    type: InsuranceType
    policy_number: str
    renewal_date: date
    premium: float
    frequency: str
    insured_item: Optional[str] = None

class InsurancePolicyCreate(InsurancePolicyBase):
    pass

class InsurancePolicyResponse(InsurancePolicyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class InsurancePolicyUpdate(BaseModel):
    provider: Optional[str] = None
    type: Optional[InsuranceType] = None
    policy_number: Optional[str] = None
    renewal_date: Optional[date] = None
    premium: Optional[float] = None
    frequency: Optional[str] = None
    insured_item: Optional[str] = None

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Budget Schemas
class BudgetBase(BaseModel):
    category: str
    monthly_limit: float
    alert_threshold: Optional[float] = 90.0
    user_id: Optional[int] = None
    is_active: Optional[bool] = True

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    category: Optional[str] = None
    monthly_limit: Optional[float] = None
    alert_threshold: Optional[float] = None
    is_active: Optional[bool] = None

class Budget(BudgetBase):
    id: int
    current_spent: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BudgetStatus(BaseModel):
    id: int
    category: str
    monthly_limit: float
    current_spent: float
    remaining: float
    percentage_used: float
    alert_threshold: float
    is_over_budget: bool
    is_near_limit: bool

    class Config:
        from_attributes = True

# ============================================================================
# v3.0 NEW SCHEMAS
# ============================================================================

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: CategoryType
    parent_id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    is_active: bool = True

class CategoryCreate(CategoryBase):
    user_id: Optional[int] = None  # Will be set from JWT token

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int]
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class CategoryTree(CategoryResponse):
    """Category with nested subcategories"""
    subcategories: List['CategoryTree'] = []

    class Config:
        from_attributes = True

# Asset V3 Schemas
class AssetV3Base(BaseModel):
    name: str = Field(..., max_length=200)
    category_id: int
    current_value: Decimal
    purchase_date: Optional[date] = None
    purchase_value: Optional[Decimal] = None
    appreciation_rate: Optional[Decimal] = None
    refresh_source: RefreshSource = RefreshSource.MANUAL
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_active: bool = True

class AssetV3Create(AssetV3Base):
    user_id: Optional[int] = None  # Will be set from JWT token

class AssetV3Update(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    category_id: Optional[int] = None
    current_value: Optional[Decimal] = None
    purchase_date: Optional[date] = None
    purchase_value: Optional[Decimal] = None
    appreciation_rate: Optional[Decimal] = None
    refresh_source: Optional[RefreshSource] = None
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class AssetV3Response(AssetV3Base):
    id: int
    user_id: int
    last_refreshed: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Liability Schemas
class LiabilityBase(BaseModel):
    name: str = Field(..., max_length=200)
    category_id: int
    principal_balance: Decimal
    interest_rate: Decimal
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
    payment_amount: Optional[Decimal] = None
    next_payment_date: Optional[date] = None
    origination_date: Optional[date] = None
    maturity_date: Optional[date] = None
    lender: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_active: bool = True

class LiabilityCreate(LiabilityBase):
    user_id: Optional[int] = None  # Will be set from JWT token

class LiabilityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    category_id: Optional[int] = None
    principal_balance: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    payment_frequency: Optional[PaymentFrequency] = None
    payment_amount: Optional[Decimal] = None
    next_payment_date: Optional[date] = None
    origination_date: Optional[date] = None
    maturity_date: Optional[date] = None
    lender: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class LiabilityResponse(LiabilityBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    file_name: str = Field(..., max_length=255)
    file_type: Optional[str] = Field(None, max_length=50)
    linked_entity: Optional[str] = Field(None, max_length=50)
    linked_id: Optional[int] = None
    notes: Optional[str] = None

class DocumentCreate(DocumentBase):
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    user_id: Optional[int] = None  # Will be set from JWT token

class DocumentUpdate(BaseModel):
    file_name: Optional[str] = Field(None, max_length=255)
    parsed_data: Optional[Dict[str, Any]] = None
    parsing_status: Optional[ParsingStatus] = None
    ai_confidence: Optional[Decimal] = None
    linked_entity: Optional[str] = Field(None, max_length=50)
    linked_id: Optional[int] = None
    notes: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    file_path: Optional[str]
    file_size: Optional[int]
    upload_date: datetime
    parsed_data: Optional[Dict[str, Any]]
    parsing_status: ParsingStatus
    ai_confidence: Optional[Decimal]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Financial Summary Schemas
class NetWorthSummary(BaseModel):
    """Comprehensive net worth calculation"""
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    asset_breakdown: Dict[str, Decimal]  # Category-wise breakdown
    liability_breakdown: Dict[str, Decimal]
    last_updated: datetime

class FinancialHealthMetrics(BaseModel):
    """CFO-level financial health indicators"""
    net_worth: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_cash_flow: Decimal
    savings_rate: float  # Percentage
    debt_to_income_ratio: float
    total_insurance_coverage: Decimal
    emergency_fund_months: float
    last_calculated: datetime
