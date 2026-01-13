from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Text, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"

class TransactionStatus(str, enum.Enum):
    PENDING = "Pending"
    POSTED = "Posted"

class AssetType(str, enum.Enum):
    REAL_ESTATE = "RealEstate"
    VEHICLE = "Vehicle"
    STOCK = "Stock"

class SubscriptionCycle(str, enum.Enum):
    MONTHLY = "Monthly"
    YEARLY = "Yearly"

class AccountType(str, enum.Enum):
    TFSA = "TFSA"
    RRSP = "RRSP"
    RESP = "RESP"
    FHSA = "FHSA"

class InsuranceType(str, enum.Enum):
    AUTO = "Auto"
    HOME = "Home"
    LIFE = "Life"
    HEALTH = "Health"
    DISABILITY = "Disability"

# v3.0 New Enums
class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    ASSET = "asset"
    LIABILITY = "liability"

class RefreshSource(str, enum.Enum):
    MANUAL = "manual"
    STOCK_API = "stock_api"
    CRYPTO_API = "crypto_api"
    REAL_ESTATE_API = "real_estate_api"

class PaymentFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"

class ParsingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class EntityType(str, enum.Enum):
    INSURANCE = "insurance"
    TRANSACTION = "transaction"
    ASSET = "asset"
    LIABILITY = "liability"
    GOV_BENEFIT = "gov_benefit"

class TransactionSource(str, enum.Enum):
    MANUAL = "manual"
    DOCUMENT = "document"
    EMAIL = "email"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    status = Column(String, default="Active")
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    merchant = Column(String, nullable=False)
    category = Column(String, nullable=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    source = Column(String, default="manual", nullable=False, index=True)  # manual, document, email
    is_amortized = Column(Boolean, default=False)
    linked_subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    notes = Column(String, nullable=True)
    ai_confidence = Column(Numeric(5, 2), nullable=True)  # For AI-extracted transactions
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    subscription = relationship("Subscription", back_populates="transactions")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(AssetType), nullable=False)
    value = Column(Float, nullable=False)
    equity = Column(Float, nullable=True)
    purchase_date = Column(Date, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    cycle = Column(SQLEnum(SubscriptionCycle), nullable=False)
    next_due_date = Column(Date, nullable=False)
    merchant_keyword = Column(String, nullable=True)  # For AI matching
    status = Column(String, default="Active")
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="subscription")

class CanadianAccount(Base):
    __tablename__ = "canadian_accounts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(AccountType), nullable=False)
    institution = Column(String, nullable=False)
    holder = Column(String, nullable=False)  # e.g., "Dad", "Mom"
    current_value = Column(Float, nullable=False)
    contribution_room = Column(Float, nullable=False)  # Remaining room
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    type = Column(SQLEnum(InsuranceType), nullable=False)
    policy_number = Column(String, nullable=False)
    renewal_date = Column(Date, nullable=False)
    premium = Column(Float, nullable=False)  # Cost
    frequency = Column(String, nullable=False)  # Monthly/Yearly
    insured_item = Column(String, nullable=True)  # e.g., "Tesla Model Y"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    monthly_limit = Column(Float, nullable=False)
    current_spent = Column(Float, default=0.0, nullable=False)
    alert_threshold = Column(Float, default=90.0, nullable=False)  # Percentage (e.g., 90%)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", backref="budgets")

# ============================================================================
# v3.0 NEW MODELS
# ============================================================================

class Category(Base):
    """
    Hierarchical category system for income, expenses, assets, and liabilities.
    Supports user-defined categories with parent-child relationships.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(SQLEnum(CategoryType), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    icon = Column(String(50), nullable=True)  # Icon name for frontend
    color = Column(String(20), nullable=True)  # Color code (e.g., "#FF5733")
    is_system = Column(Boolean, default=False, nullable=False)  # System vs user-defined
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    user = relationship("User", backref="categories")

class AssetV3(Base):
    """
    Enhanced asset tracking with API refresh support.
    Tracks current value, appreciation, and supports automated value updates.
    """
    __tablename__ = "assets_v3"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    current_value = Column(Numeric(18, 2), nullable=False)
    purchase_date = Column(Date, nullable=True)
    purchase_value = Column(Numeric(18, 2), nullable=True)
    appreciation_rate = Column(Numeric(5, 2), nullable=True)  # Annual appreciation %
    refresh_source = Column(SQLEnum(RefreshSource), default=RefreshSource.MANUAL, nullable=False)
    last_refreshed = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    extra_data = Column(JSONB, nullable=True)  # Flexible storage for API data, ticker symbols, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", backref="assets")
    user = relationship("User", backref="assets_v3")

class Liability(Base):
    """
    Debt and liability tracking for net worth calculation.
    Supports various loan types with payment schedules.
    """
    __tablename__ = "liabilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    principal_balance = Column(Numeric(18, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)  # Annual interest rate %
    payment_frequency = Column(SQLEnum(PaymentFrequency), default=PaymentFrequency.MONTHLY, nullable=False)
    payment_amount = Column(Numeric(10, 2), nullable=True)
    next_payment_date = Column(Date, nullable=True, index=True)
    origination_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    lender = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    extra_data = Column(JSONB, nullable=True)  # Flexible storage for loan details
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", backref="liabilities")
    user = relationship("User", backref="liabilities")

class GovBenefit(Base):
    """
    Canadian Government Benefits tracking (CCB, GST/HST, OAS, CPP, EI, etc.)
    Tracks recurring government payments and benefits.
    """
    __tablename__ = "government_benefits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # e.g., "CCB (Child Benefit)", "GST/HST Credit"
    benefit_type = Column(String(50), nullable=False)  # e.g., "CCB", "GST", "OAS", "CPP", "EI"
    amount = Column(Numeric(10, 2), nullable=False)  # Monthly or per-payment amount
    frequency = Column(SQLEnum(PaymentFrequency), default=PaymentFrequency.MONTHLY, nullable=False)
    next_payment_date = Column(Date, nullable=True, index=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)  # For benefits with expiry
    government_agency = Column(String(100), nullable=True)  # e.g., "Government of Canada", "CRA"
    beneficiary = Column(String(100), nullable=True)  # Who receives it
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    extra_data = Column(JSONB, nullable=True)  # Additional benefit details
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="government_benefits")

class Document(Base):
    """
    AI-powered document storage and parsing.
    Stores receipts, insurance claims, bank statements, etc.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Storage path or S3 key
    file_type = Column(String(50), nullable=True)  # MIME type
    file_size = Column(Integer, nullable=True)  # Size in bytes
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    parsed_data = Column(JSONB, nullable=True)  # AI-extracted content
    parsing_status = Column(SQLEnum(ParsingStatus), default=ParsingStatus.PENDING, nullable=False)
    ai_confidence = Column(Numeric(5, 2), nullable=True)  # Confidence score 0-100
    linked_entity = Column(String(50), nullable=True)  # 'transaction', 'insurance', 'asset', etc.
    linked_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="documents")

class PendingReview(Base):
    """
    Pending review queue for scanned documents.
    Stores AI-parsed data awaiting human approval before creating formal records.
    """
    __tablename__ = "pending_reviews"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True)  # Type of entity to create (enforced by DB enum)
    parsed_data = Column(JSONB, nullable=False)  # AI-extracted structured data
    ai_confidence = Column(Numeric(5, 2), nullable=True)  # Confidence score 0.00-1.00
    status = Column(String, default="pending", nullable=False, index=True)  # Status (enforced by DB enum reviewstatus)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    original_file_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    linked_entity_id = Column(Integer, nullable=True)  # ID of created entity after approval
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="pending_reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], backref="reviewed_items")
    document = relationship("Document", backref="pending_reviews")
