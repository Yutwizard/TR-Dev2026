"""
Treasury Management System - Settlement Message Generator
=========================================================

Generates ISO20022 payment messages for BAHTNET and TSD settlement.

BAHTNET Messages (Manual Upload):
- pacs.008 - Credit Transfer (FI to FI)
- pacs.009 - Direct Debit (FI to FI)

TSD Messages (Bond Settlement):
- DVP instruction generation
- Settlement confirmation

Usage:
    from app.services.settlement_service import BAHTNETMessageGenerator
    
    generator = BAHTNETMessageGenerator()
    message = generator.create_credit_transfer(deal)
    generator.save_to_file(message, "CT001.xml")

⚠️ IMPORTANT: These messages are for MANUAL UPLOAD to BAHTNET portal.
             There is NO API integration - files are generated locally.
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import uuid
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Constants & Enums
# =============================================================================
class TransactionType(str, Enum):
    """BAHTNET Transaction Types"""
    CREDIT_TRANSFER = "CT"      # pacs.008
    DIRECT_DEBIT = "DD"         # pacs.009
    RETURN = "RTN"              # Return of funds


class SettlementSystem(str, Enum):
    """Settlement Systems"""
    BAHTNET = "BAHTNET"
    TSD = "TSD"


class PaymentPurpose(str, Enum):
    """Payment Purpose Codes"""
    INTERBANK_LENDING = "INTC"      # Interbank funds transfer
    INTERBANK_BORROWING = "INTC"    
    REPO_PRINCIPAL = "REPO"         # Repo principal
    REPO_INTEREST = "INTR"          # Interest payment
    BOND_SETTLEMENT = "SECU"        # Securities settlement
    MARGIN_CALL = "COLL"            # Collateral


# =============================================================================
# Data Classes
# =============================================================================
@dataclass
class BankParty:
    """Bank party information"""
    bank_code: str              # BOT bank code (13 chars)
    bic: str                    # SWIFT BIC
    name: str                   # Bank name
    account: Optional[str] = None


@dataclass
class PaymentInstruction:
    """Payment instruction details"""
    instruction_id: str         # Unique ID
    end_to_end_id: str          # E2E reference
    transaction_id: str         # Original transaction (deal/trade ID)
    amount: float
    currency: str = "THB"
    value_date: date = None
    purpose: PaymentPurpose = PaymentPurpose.INTERBANK_LENDING
    debtor: BankParty = None
    creditor: BankParty = None
    remittance_info: str = ""


# =============================================================================
# BAHTNET ISO20022 Message Generator
# =============================================================================
class BAHTNETMessageGenerator:
    """
    Generates ISO20022 payment messages for BAHTNET.
    
    Messages are saved as XML files for MANUAL UPLOAD to BAHTNET portal.
    
    Supported message types:
    - pacs.008.001.08 - FI to FI Customer Credit Transfer
    - pacs.009.001.08 - FI to FI Financial Institution Credit Transfer
    
    Usage:
        generator = BAHTNETMessageGenerator(
            bank_code="0001",
            bic="BABOROPBXXX"
        )
        
        # Create credit transfer message
        instruction = PaymentInstruction(
            instruction_id="INS001",
            end_to_end_id="E2E001",
            transaction_id="IB_LEND_001",
            amount=50000000.00,
            value_date=date(2025, 9, 5),
            debtor=our_bank,
            creditor=counterparty_bank
        )
        
        xml_content = generator.create_credit_transfer(instruction)
        filename = generator.save_to_file(xml_content)
        
        print(f"File ready for upload: {filename}")
    """
    
    # ISO20022 namespace
    NS_PACS008 = "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08"
    NS_PACS009 = "urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08"
    
    def __init__(
        self,
        bank_code: str = None,
        bic: str = None,
        output_path: str = None
    ):
        """
        Initialize BAHTNET message generator.
        
        Args:
            bank_code: Our bank's BOT code (from settings if not provided)
            bic: Our bank's SWIFT BIC
            output_path: Directory to save generated files
        """
        self.bank_code = bank_code or settings.BAHTNET_BANK_CODE
        self.bic = bic or "TMSBBKKK"  # Placeholder
        self.output_path = Path(output_path or settings.BAHTNET_OUTPUT_PATH)
        
        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"BAHTNETMessageGenerator initialized: "
            f"bank_code={self.bank_code}, output={self.output_path}"
        )
    
    def create_credit_transfer(
        self,
        instruction: PaymentInstruction
    ) -> str:
        """
        Create pacs.008 Credit Transfer message.
        
        Used for:
        - Interbank lending (sending funds to counterparty)
        - Repo/RRP cash settlement
        - Interest payments
        
        Args:
            instruction: Payment instruction details
            
        Returns:
            XML content as string
        """
        # Create root element with namespace
        root = ET.Element("Document", xmlns=self.NS_PACS008)
        
        # FIToFICstmrCdtTrf (FI to FI Customer Credit Transfer)
        fi_msg = ET.SubElement(root, "FIToFICstmrCdtTrf")
        
        # Group Header
        grp_hdr = ET.SubElement(fi_msg, "GrpHdr")
        ET.SubElement(grp_hdr, "MsgId").text = self._generate_message_id()
        ET.SubElement(grp_hdr, "CreDtTm").text = datetime.utcnow().isoformat() + "Z"
        ET.SubElement(grp_hdr, "NbOfTxs").text = "1"
        ET.SubElement(grp_hdr, "TtlIntrBkSttlmAmt", Ccy="THB").text = f"{instruction.amount:.2f}"
        ET.SubElement(grp_hdr, "IntrBkSttlmDt").text = instruction.value_date.isoformat()
        
        # Settlement Information
        sttlm_inf = ET.SubElement(grp_hdr, "SttlmInf")
        ET.SubElement(sttlm_inf, "SttlmMtd").text = "CLRG"  # Clearing (BAHTNET)
        
        # Credit Transfer Transaction Information
        cdt_tx = ET.SubElement(fi_msg, "CdtTrfTxInf")
        
        # Payment ID
        pmt_id = ET.SubElement(cdt_tx, "PmtId")
        ET.SubElement(pmt_id, "InstrId").text = instruction.instruction_id
        ET.SubElement(pmt_id, "EndToEndId").text = instruction.end_to_end_id
        ET.SubElement(pmt_id, "UETR").text = str(uuid.uuid4())  # Unique E2E Transaction Reference
        
        # Amount
        ET.SubElement(cdt_tx, "IntrBkSttlmAmt", Ccy="THB").text = f"{instruction.amount:.2f}"
        
        # Debtor (Our Bank - sending)
        if instruction.debtor:
            dbtr = ET.SubElement(cdt_tx, "Dbtr")
            ET.SubElement(dbtr, "Nm").text = instruction.debtor.name
            dbtr_acct = ET.SubElement(cdt_tx, "DbtrAcct")
            dbtr_acct_id = ET.SubElement(dbtr_acct, "Id")
            ET.SubElement(dbtr_acct_id, "Othr").text = instruction.debtor.account or ""
            
            dbtr_agt = ET.SubElement(cdt_tx, "DbtrAgt")
            dbtr_agt_id = ET.SubElement(dbtr_agt, "FinInstnId")
            ET.SubElement(dbtr_agt_id, "BICFI").text = instruction.debtor.bic
        
        # Creditor (Counterparty - receiving)
        if instruction.creditor:
            cdtr = ET.SubElement(cdt_tx, "Cdtr")
            ET.SubElement(cdtr, "Nm").text = instruction.creditor.name
            cdtr_acct = ET.SubElement(cdt_tx, "CdtrAcct")
            cdtr_acct_id = ET.SubElement(cdtr_acct, "Id")
            ET.SubElement(cdtr_acct_id, "Othr").text = instruction.creditor.account or ""
            
            cdtr_agt = ET.SubElement(cdt_tx, "CdtrAgt")
            cdtr_agt_id = ET.SubElement(cdtr_agt, "FinInstnId")
            ET.SubElement(cdtr_agt_id, "BICFI").text = instruction.creditor.bic
        
        # Purpose
        purp = ET.SubElement(cdt_tx, "Purp")
        ET.SubElement(purp, "Cd").text = instruction.purpose.value
        
        # Remittance Information
        if instruction.remittance_info:
            rmt_inf = ET.SubElement(cdt_tx, "RmtInf")
            ET.SubElement(rmt_inf, "Ustrd").text = instruction.remittance_info[:140]
        
        return self._prettify_xml(root)
    
    def create_direct_debit(
        self,
        instruction: PaymentInstruction
    ) -> str:
        """
        Create pacs.009 Direct Debit message.
        
        Used for:
        - Interbank borrowing (receiving funds from counterparty)
        - Reverse repo cash receive
        
        Args:
            instruction: Payment instruction details
            
        Returns:
            XML content as string
        """
        # Create root element with namespace
        root = ET.Element("Document", xmlns=self.NS_PACS009)
        
        # FICdtTrf (FI Credit Transfer)
        fi_msg = ET.SubElement(root, "FICdtTrf")
        
        # Group Header
        grp_hdr = ET.SubElement(fi_msg, "GrpHdr")
        ET.SubElement(grp_hdr, "MsgId").text = self._generate_message_id()
        ET.SubElement(grp_hdr, "CreDtTm").text = datetime.utcnow().isoformat() + "Z"
        ET.SubElement(grp_hdr, "NbOfTxs").text = "1"
        ET.SubElement(grp_hdr, "IntrBkSttlmDt").text = instruction.value_date.isoformat()
        
        # Settlement Information
        sttlm_inf = ET.SubElement(grp_hdr, "SttlmInf")
        ET.SubElement(sttlm_inf, "SttlmMtd").text = "CLRG"
        
        # Credit Transfer Transaction
        cdt_tx = ET.SubElement(fi_msg, "CdtTrfTxInf")
        
        # Payment ID
        pmt_id = ET.SubElement(cdt_tx, "PmtId")
        ET.SubElement(pmt_id, "InstrId").text = instruction.instruction_id
        ET.SubElement(pmt_id, "EndToEndId").text = instruction.end_to_end_id
        
        # Amount
        intrk_amt = ET.SubElement(cdt_tx, "IntrBkSttlmAmt", Ccy="THB")
        intrk_amt.text = f"{instruction.amount:.2f}"
        
        return self._prettify_xml(root)
    
    def create_interbank_lending_message(
        self,
        deal_id: str,
        counterparty_bic: str,
        counterparty_name: str,
        amount: float,
        value_date: date,
        interest_rate: float = None
    ) -> str:
        """
        Convenience method to create IB lending message.
        
        Args:
            deal_id: Interbank deal ID
            counterparty_bic: Counterparty SWIFT BIC
            counterparty_name: Counterparty name
            amount: Principal amount
            value_date: Settlement date
            interest_rate: Optional rate for remittance info
        """
        instruction = PaymentInstruction(
            instruction_id=f"IBLND_{deal_id}",
            end_to_end_id=f"E2E_{deal_id}",
            transaction_id=deal_id,
            amount=amount,
            value_date=value_date,
            purpose=PaymentPurpose.INTERBANK_LENDING,
            debtor=BankParty(
                bank_code=self.bank_code,
                bic=self.bic,
                name="Our Bank"
            ),
            creditor=BankParty(
                bank_code="",
                bic=counterparty_bic,
                name=counterparty_name
            ),
            remittance_info=f"IB LENDING {deal_id}" + 
                           (f" @ {interest_rate}%" if interest_rate else "")
        )
        
        return self.create_credit_transfer(instruction)
    
    def create_repo_settlement_message(
        self,
        repo_id: str,
        counterparty_bic: str,
        counterparty_name: str,
        amount: float,
        value_date: date,
        is_opening: bool = True
    ) -> str:
        """
        Create repo cash settlement message.
        
        Args:
            repo_id: Repo trade ID
            counterparty_bic: Counterparty SWIFT BIC
            counterparty_name: Counterparty name
            amount: Cash amount
            value_date: Settlement date
            is_opening: True for opening leg, False for closing
        """
        leg = "OPEN" if is_opening else "CLOSE"
        
        instruction = PaymentInstruction(
            instruction_id=f"REPO_{leg}_{repo_id}",
            end_to_end_id=f"E2E_REPO_{repo_id}",
            transaction_id=repo_id,
            amount=amount,
            value_date=value_date,
            purpose=PaymentPurpose.REPO_PRINCIPAL,
            debtor=BankParty(
                bank_code=self.bank_code,
                bic=self.bic,
                name="Our Bank"
            ),
            creditor=BankParty(
                bank_code="",
                bic=counterparty_bic,
                name=counterparty_name
            ),
            remittance_info=f"REPO {leg} {repo_id}"
        )
        
        return self.create_credit_transfer(instruction)
    
    def save_to_file(
        self,
        xml_content: str,
        filename: str = None
    ) -> str:
        """
        Save XML message to file.
        
        Args:
            xml_content: XML content string
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Full path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"BAHTNET_{timestamp}.xml"
        
        filepath = self.output_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        logger.info(f"BAHTNET message saved: {filepath}")
        return str(filepath)
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TMS{timestamp}{uuid.uuid4().hex[:8].upper()}"
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Convert ElementTree to pretty-printed XML string"""
        rough = ET.tostring(elem, encoding="unicode")
        parsed = minidom.parseString(rough)
        return parsed.toprettyxml(indent="  ")


# =============================================================================
# TSD Message Generator (Bond Settlement)
# =============================================================================
class TSDMessageGenerator:
    """
    Generates settlement instructions for TSD (DVP settlement).
    
    Used for:
    - Bond buy/sell settlement
    - Repo collateral transfer
    
    Messages are generated as structured text/CSV for manual input.
    
    Usage:
        generator = TSDMessageGenerator(participant_code="ABC123")
        instruction = generator.create_dvp_instruction(trade)
        generator.save_to_file(instruction)
    """
    
    def __init__(
        self,
        participant_code: str = None,
        output_path: str = None
    ):
        self.participant_code = participant_code or settings.TSD_PARTICIPANT_CODE
        self.output_path = Path(output_path or settings.TSD_OUTPUT_PATH)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"TSDMessageGenerator initialized: participant={self.participant_code}")
    
    def create_dvp_instruction(
        self,
        trade_id: str,
        isin: str,
        quantity: float,
        price: float,
        settlement_amount: float,
        settlement_date: date,
        counterparty_code: str,
        is_buy: bool = True
    ) -> Dict[str, Any]:
        """
        Create DVP settlement instruction.
        
        Args:
            trade_id: Bond trade ID
            isin: Security ISIN
            quantity: Number of units
            price: Clean price
            settlement_amount: Total settlement amount
            settlement_date: Settlement date
            counterparty_code: Counterparty TSD participant code
            is_buy: True for buy (receive securities), False for sell
            
        Returns:
            Dictionary with instruction details
        """
        return {
            "instruction_type": "DVP",
            "instruction_id": f"TSD_{trade_id}",
            "trade_reference": trade_id,
            "direction": "RECEIVE" if is_buy else "DELIVER",
            "participant_code": self.participant_code,
            "counterparty_code": counterparty_code,
            "isin": isin,
            "quantity": quantity,
            "price": price,
            "settlement_amount": settlement_amount,
            "settlement_date": settlement_date.isoformat(),
            "currency": "THB",
            "created_at": datetime.now().isoformat(),
            "status": "PENDING_SUBMISSION"
        }
    
    def create_fop_instruction(
        self,
        instruction_id: str,
        isin: str,
        quantity: float,
        settlement_date: date,
        counterparty_code: str,
        is_deliver: bool = True,
        reason: str = "COLLATERAL"
    ) -> Dict[str, Any]:
        """
        Create Free-of-Payment (FoP) instruction.
        
        Used for:
        - Collateral transfer
        - Collateral return
        
        Args:
            instruction_id: Unique instruction ID
            isin: Security ISIN
            quantity: Number of units
            settlement_date: Settlement date
            counterparty_code: Counterparty TSD code
            is_deliver: True to deliver, False to receive
            reason: Reason for transfer
        """
        return {
            "instruction_type": "FOP",
            "instruction_id": f"TSD_FOP_{instruction_id}",
            "direction": "DELIVER" if is_deliver else "RECEIVE",
            "participant_code": self.participant_code,
            "counterparty_code": counterparty_code,
            "isin": isin,
            "quantity": quantity,
            "settlement_date": settlement_date.isoformat(),
            "reason": reason,
            "created_at": datetime.now().isoformat(),
            "status": "PENDING_SUBMISSION"
        }
    
    def format_as_csv(self, instructions: List[Dict[str, Any]]) -> str:
        """Format instructions as CSV for bulk upload"""
        if not instructions:
            return ""
        
        headers = list(instructions[0].keys())
        lines = [",".join(headers)]
        
        for inst in instructions:
            values = [str(inst.get(h, "")) for h in headers]
            lines.append(",".join(values))
        
        return "\n".join(lines)
    
    def save_to_file(
        self,
        instruction: Dict[str, Any],
        filename: str = None
    ) -> str:
        """Save instruction to JSON file"""
        import json
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"TSD_{instruction.get('instruction_type', 'INST')}_{timestamp}.json"
        
        filepath = self.output_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(instruction, f, indent=2, default=str)
        
        logger.info(f"TSD instruction saved: {filepath}")
        return str(filepath)


# =============================================================================
# Factory Functions
# =============================================================================
_bahtnet_generator = None
_tsd_generator = None


def get_bahtnet_generator() -> BAHTNETMessageGenerator:
    """Get singleton BAHTNET generator"""
    global _bahtnet_generator
    if _bahtnet_generator is None:
        _bahtnet_generator = BAHTNETMessageGenerator()
    return _bahtnet_generator


def get_tsd_generator() -> TSDMessageGenerator:
    """Get singleton TSD generator"""
    global _tsd_generator
    if _tsd_generator is None:
        _tsd_generator = TSDMessageGenerator()
    return _tsd_generator
