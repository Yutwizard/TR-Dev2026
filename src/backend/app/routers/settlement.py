"""
Treasury Management System - Settlement Router
===============================================

API endpoints for settlement operations:
- BAHTNET: Cash transfers (interbank, payment leg of repos)
- TSD: Securities settlement (bond trades, collateral)

Endpoints:
- GET /pending: List pending settlements
- POST /bahtnet/generate: Generate BAHTNET message
- POST /tsd/generate: Generate TSD instruction
- GET /status/{ref}: Check settlement status
- POST /confirm/{ref}: Confirm settlement
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from enum import Enum

from app.core.auth import get_current_active_user, UserInToken


router = APIRouter()


# =============================================================================
# Enums
# =============================================================================
class SettlementSystem(str, Enum):
    BAHTNET = "BAHTNET"
    TSD = "TSD"


class SettlementType(str, Enum):
    CASH = "CASH"
    SECURITIES = "SECURITIES"
    DVP = "DVP"  # Delivery vs Payment


class SettlementDirection(str, Enum):
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"


class SettlementStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    CONFIRMED = "CONFIRMED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class TradeType(str, Enum):
    BOND_TRADE = "BOND_TRADE"
    INTERBANK_DEAL = "INTERBANK_DEAL"
    REPO_TRADE = "REPO_TRADE"


# =============================================================================
# Request/Response Models
# =============================================================================
class PendingSettlement(BaseModel):
    """Settlement pending execution"""
    settlement_id: str
    trade_ref: str
    trade_type: str
    settlement_system: str
    settlement_type: str
    direction: str
    currency: str
    amount: Decimal
    security_isin: Optional[str]
    security_quantity: Optional[Decimal]
    counterparty_id: str
    counterparty_name: str
    value_date: date
    status: str
    message_generated: bool
    message_ref: Optional[str]
    created_at: datetime


class BAHTNETMessage(BaseModel):
    """BAHTNET message structure"""
    message_ref: str
    message_type: str  # MT103, MT202
    sender_bic: str
    receiver_bic: str
    amount: Decimal
    currency: str
    value_date: date
    sender_reference: str
    related_reference: Optional[str]
    beneficiary_account: Optional[str]
    remittance_info: str
    xml_content: str
    generated_at: datetime


class TSDInstruction(BaseModel):
    """TSD settlement instruction"""
    instruction_ref: str
    instruction_type: str  # DVP, FOP, PLEDGE
    participant_code: str
    counterparty_code: str
    isin: str
    security_name: str
    quantity: Decimal
    amount: Decimal
    settlement_date: date
    buyer_seller: str  # B or S
    matching_status: str
    json_content: str
    generated_at: datetime


class SettlementConfirmation(BaseModel):
    """Settlement confirmation"""
    settlement_id: str
    external_ref: str
    status: str
    confirmed_at: datetime
    confirmed_by: str
    notes: Optional[str]


class SettlementSummary(BaseModel):
    """Daily settlement summary"""
    settlement_date: date
    total_bahtnet_outgoing: Decimal
    total_bahtnet_incoming: Decimal
    net_bahtnet: Decimal
    total_securities_delivered: int
    total_securities_received: int
    pending_count: int
    settled_count: int
    failed_count: int


# =============================================================================
# Mock Data
# =============================================================================
MOCK_PENDING_SETTLEMENTS = [
    PendingSettlement(
        settlement_id="STL001",
        trade_ref="BT202502010001",
        trade_type="BOND_TRADE",
        settlement_system="TSD",
        settlement_type="DVP",
        direction="OUTGOING",
        currency="THB",
        amount=Decimal("102456789.00"),
        security_isin="TH0623A3B702",
        security_quantity=Decimal("100000000.00"),
        counterparty_id="CPTY001",
        counterparty_name="Bangkok Bank PCL",
        value_date=date(2025, 2, 3),
        status="PENDING",
        message_generated=False,
        message_ref=None,
        created_at=datetime.now()
    ),
    PendingSettlement(
        settlement_id="STL002",
        trade_ref="IB202502010001",
        trade_type="INTERBANK_DEAL",
        settlement_system="BAHTNET",
        settlement_type="CASH",
        direction="OUTGOING",
        currency="THB",
        amount=Decimal("100000000.00"),
        security_isin=None,
        security_quantity=None,
        counterparty_id="CPTY001",
        counterparty_name="Bangkok Bank PCL",
        value_date=date(2025, 2, 1),
        status="SENT",
        message_generated=True,
        message_ref="BAHT20250201001",
        created_at=datetime.now()
    ),
    PendingSettlement(
        settlement_id="STL003",
        trade_ref="RP202502010001",
        trade_type="REPO_TRADE",
        settlement_system="BAHTNET",
        settlement_type="CASH",
        direction="INCOMING",
        currency="THB",
        amount=Decimal("100000000.00"),
        security_isin=None,
        security_quantity=None,
        counterparty_id="CPTY001",
        counterparty_name="Bangkok Bank PCL",
        value_date=date(2025, 2, 3),
        status="PENDING",
        message_generated=False,
        message_ref=None,
        created_at=datetime.now()
    ),
]


# =============================================================================
# Helper Functions
# =============================================================================
def generate_bahtnet_xml(msg: BAHTNETMessage) -> str:
    """Generate BAHTNET XML message content"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<BahtnetMessage xmlns="urn:bot:bahtnet:1.0">
    <MessageHeader>
        <MessageReference>{msg.message_ref}</MessageReference>
        <MessageType>{msg.message_type}</MessageType>
        <SenderBIC>{msg.sender_bic}</SenderBIC>
        <ReceiverBIC>{msg.receiver_bic}</ReceiverBIC>
        <CreationDateTime>{msg.generated_at.isoformat()}</CreationDateTime>
    </MessageHeader>
    <PaymentDetails>
        <Amount Currency="{msg.currency}">{msg.amount}</Amount>
        <ValueDate>{msg.value_date.isoformat()}</ValueDate>
        <SenderReference>{msg.sender_reference}</SenderReference>
        <RelatedReference>{msg.related_reference or ''}</RelatedReference>
        <RemittanceInformation>{msg.remittance_info}</RemittanceInformation>
    </PaymentDetails>
</BahtnetMessage>"""


def generate_tsd_json(instr: TSDInstruction) -> str:
    """Generate TSD JSON instruction"""
    import json
    return json.dumps({
        "instructionRef": instr.instruction_ref,
        "instructionType": instr.instruction_type,
        "participantCode": instr.participant_code,
        "counterpartyCode": instr.counterparty_code,
        "security": {
            "isin": instr.isin,
            "name": instr.security_name,
            "quantity": str(instr.quantity)
        },
        "settlement": {
            "amount": str(instr.amount),
            "date": instr.settlement_date.isoformat(),
            "buyerSeller": instr.buyer_seller
        },
        "generatedAt": instr.generated_at.isoformat()
    }, indent=2)


# =============================================================================
# Endpoints
# =============================================================================
@router.get("/pending", response_model=List[PendingSettlement])
async def list_pending_settlements(
    settlement_date: Optional[date] = Query(None),
    system: Optional[SettlementSystem] = Query(None),
    direction: Optional[SettlementDirection] = Query(None),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    List all pending settlements.
    
    Filters by settlement date, system (BAHTNET/TSD), and direction.
    """
    settlements = MOCK_PENDING_SETTLEMENTS.copy()
    
    if settlement_date:
        settlements = [s for s in settlements if s.value_date == settlement_date]
    if system:
        settlements = [s for s in settlements if s.settlement_system == system.value]
    if direction:
        settlements = [s for s in settlements if s.direction == direction.value]
    
    return settlements


@router.get("/summary", response_model=SettlementSummary)
async def get_settlement_summary(
    settlement_date: date = Query(default_factory=date.today),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get settlement summary for a specific date.
    
    Shows total cash flows, securities transfers, and status counts.
    """
    # Calculate from mock data
    outgoing = sum(
        s.amount for s in MOCK_PENDING_SETTLEMENTS
        if s.direction == "OUTGOING" and s.settlement_system == "BAHTNET"
        and s.value_date == settlement_date
    )
    incoming = sum(
        s.amount for s in MOCK_PENDING_SETTLEMENTS
        if s.direction == "INCOMING" and s.settlement_system == "BAHTNET"
        and s.value_date == settlement_date
    )
    
    return SettlementSummary(
        settlement_date=settlement_date,
        total_bahtnet_outgoing=outgoing,
        total_bahtnet_incoming=incoming,
        net_bahtnet=incoming - outgoing,
        total_securities_delivered=1,
        total_securities_received=0,
        pending_count=2,
        settled_count=1,
        failed_count=0
    )


@router.post("/bahtnet/generate", response_model=BAHTNETMessage)
async def generate_bahtnet_message(
    settlement_id: str = Query(...),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Generate BAHTNET XML message for a settlement.
    
    Creates the message in manual mode for upload to BAHTNET system.
    Returns the XML content and reference number.
    """
    settlement = next(
        (s for s in MOCK_PENDING_SETTLEMENTS if s.settlement_id == settlement_id),
        None
    )
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    if settlement.settlement_system != "BAHTNET":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settlement is not for BAHTNET"
        )
    
    if settlement.message_generated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message already generated: {settlement.message_ref}"
        )
    
    # Generate message
    message_ref = f"BAHT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    msg = BAHTNETMessage(
        message_ref=message_ref,
        message_type="MT202" if settlement.direction == "OUTGOING" else "MT103",
        sender_bic="BKKBTHBKXXX",  # Our bank's BIC
        receiver_bic="KASITHBKXXX",  # Counterparty's BIC
        amount=settlement.amount,
        currency=settlement.currency,
        value_date=settlement.value_date,
        sender_reference=settlement.trade_ref,
        related_reference=None,
        beneficiary_account="1234567890",
        remittance_info=f"Payment for {settlement.trade_type} {settlement.trade_ref}",
        xml_content="",  # Will be filled
        generated_at=datetime.now()
    )
    
    msg.xml_content = generate_bahtnet_xml(msg)
    
    return msg


@router.post("/tsd/generate", response_model=TSDInstruction)
async def generate_tsd_instruction(
    settlement_id: str = Query(...),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Generate TSD settlement instruction.
    
    Creates DVP/FOP instruction for securities settlement.
    """
    settlement = next(
        (s for s in MOCK_PENDING_SETTLEMENTS if s.settlement_id == settlement_id),
        None
    )
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    if settlement.settlement_system != "TSD":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settlement is not for TSD"
        )
    
    if not settlement.security_isin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No security information for TSD instruction"
        )
    
    instruction_ref = f"TSD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    instr = TSDInstruction(
        instruction_ref=instruction_ref,
        instruction_type="DVP",
        participant_code="TH0001",  # Our TSD code
        counterparty_code="TH0002",  # Counterparty's TSD code
        isin=settlement.security_isin,
        security_name="Government Bond (LB236A)",
        quantity=settlement.security_quantity or Decimal("0"),
        amount=settlement.amount,
        settlement_date=settlement.value_date,
        buyer_seller="S" if settlement.direction == "OUTGOING" else "B",
        matching_status="UNMATCHED",
        json_content="",
        generated_at=datetime.now()
    )
    
    instr.json_content = generate_tsd_json(instr)
    
    return instr


@router.get("/status/{settlement_id}", response_model=PendingSettlement)
async def get_settlement_status(
    settlement_id: str,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Get current status of a settlement."""
    settlement = next(
        (s for s in MOCK_PENDING_SETTLEMENTS if s.settlement_id == settlement_id),
        None
    )
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    return settlement


@router.post("/confirm/{settlement_id}", response_model=SettlementConfirmation)
async def confirm_settlement(
    settlement_id: str,
    external_ref: str = Query(..., description="External reference from BAHTNET/TSD"),
    notes: Optional[str] = Query(None),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Confirm that a settlement has been completed.
    
    Used for manual confirmation after checking BAHTNET/TSD systems.
    Updates trade status and creates audit trail.
    """
    settlement = next(
        (s for s in MOCK_PENDING_SETTLEMENTS if s.settlement_id == settlement_id),
        None
    )
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    if settlement.status in ["SETTLED", "CONFIRMED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settlement already confirmed"
        )
    
    return SettlementConfirmation(
        settlement_id=settlement_id,
        external_ref=external_ref,
        status="CONFIRMED",
        confirmed_at=datetime.now(),
        confirmed_by=current_user.username,
        notes=notes
    )


@router.post("/retry/{settlement_id}", response_model=PendingSettlement)
async def retry_failed_settlement(
    settlement_id: str,
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Retry a failed settlement.
    
    Resets status to PENDING for regeneration and resubmission.
    """
    settlement = next(
        (s for s in MOCK_PENDING_SETTLEMENTS if s.settlement_id == settlement_id),
        None
    )
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    if settlement.status not in ["FAILED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed or rejected settlements"
        )
    
    # Reset for retry
    updated = settlement.model_copy(update={
        "status": "PENDING",
        "message_generated": False,
        "message_ref": None
    })
    
    return updated


@router.get("/daily-report", response_model=dict)
async def get_daily_settlement_report(
    report_date: date = Query(default_factory=date.today),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Generate daily settlement report.
    
    Summarizes all settlements for the day with status breakdown.
    """
    settlements = [s for s in MOCK_PENDING_SETTLEMENTS if s.value_date == report_date]
    
    return {
        "report_date": report_date.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "generated_by": current_user.username,
        "summary": {
            "total_settlements": len(settlements),
            "bahtnet_count": len([s for s in settlements if s.settlement_system == "BAHTNET"]),
            "tsd_count": len([s for s in settlements if s.settlement_system == "TSD"]),
            "pending": len([s for s in settlements if s.status == "PENDING"]),
            "sent": len([s for s in settlements if s.status == "SENT"]),
            "settled": len([s for s in settlements if s.status == "SETTLED"]),
            "failed": len([s for s in settlements if s.status == "FAILED"])
        },
        "cash_flows": {
            "outgoing": str(sum(s.amount for s in settlements if s.direction == "OUTGOING")),
            "incoming": str(sum(s.amount for s in settlements if s.direction == "INCOMING")),
            "net": str(
                sum(s.amount for s in settlements if s.direction == "INCOMING") -
                sum(s.amount for s in settlements if s.direction == "OUTGOING")
            )
        },
        "settlements": [
            {
                "id": s.settlement_id,
                "trade_ref": s.trade_ref,
                "type": s.trade_type,
                "system": s.settlement_system,
                "direction": s.direction,
                "amount": str(s.amount),
                "status": s.status
            }
            for s in settlements
        ]
    }
