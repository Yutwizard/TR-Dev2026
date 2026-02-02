"""
Treasury Management System - Settlement Service Tests
=======================================================

Unit tests for BAHTNET and TSD message generators.
"""

import pytest
from datetime import date
from decimal import Decimal
import xml.etree.ElementTree as ET
import json

from app.services.settlement_service import (
    BAHTNETMessageGenerator,
    TSDMessageGenerator,
    get_bahtnet_generator,
    get_tsd_generator,
)


class TestBAHTNETMessageGenerator:
    """Tests for BAHTNET ISO20022 message generation"""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance"""
        return BAHTNETMessageGenerator(
            bank_code="0020000000000",  # Sample BOT code
            bank_name="Test Bank PCL",
            bank_bic="TESTHTHBXXX"
        )
    
    def test_create_credit_transfer(self, generator):
        """Should create valid pacs.008 credit transfer"""
        xml = generator.create_credit_transfer(
            amount=100000000.00,
            debtor_account="1234567890",
            creditor_bic="KASITHBKXXX",
            creditor_name="Kasikorn Bank",
            creditor_account="0987654321",
            value_date=date(2025, 9, 3),
            end_to_end_id="IB20250901001",
            remittance_info="Interbank Lending Settlement"
        )
        
        assert xml is not None
        assert "pacs.008" in xml
        assert "<IntrBkSttlmAmt" in xml
        assert "100000000" in xml
        assert "KASITHBKXXX" in xml
    
    def test_credit_transfer_is_valid_xml(self, generator):
        """Credit transfer should be valid XML"""
        xml = generator.create_credit_transfer(
            amount=50000000.00,
            debtor_account="1234567890",
            creditor_bic="SCBKTHBKXXX",
            creditor_name="SCB",
            creditor_account="0987654321",
            value_date=date(2025, 9, 3),
            end_to_end_id="TEST001"
        )
        
        # Should not raise
        root = ET.fromstring(xml)
        assert root.tag is not None
    
    def test_create_direct_debit(self, generator):
        """Should create valid pacs.009 direct debit"""
        xml = generator.create_direct_debit(
            amount=50000000.00,
            creditor_account="1234567890",
            debtor_bic="BABORATHXXX",
            debtor_name="Bank of Ayudhya",
            debtor_account="0987654321",
            value_date=date(2025, 9, 3),
            end_to_end_id="IB20250901002",
            remittance_info="Interbank Borrowing Receipt"
        )
        
        assert xml is not None
        assert "pacs.009" in xml
        assert "50000000" in xml
    
    def test_create_interbank_lending_message(self, generator):
        """Should create interbank lending message"""
        xml = generator.create_interbank_lending_message(
            deal_id="IB001",
            counterparty_bic="KASITHBKXXX",
            counterparty_name="Kasikorn Bank",
            amount=100000000.00,
            value_date=date(2025, 9, 3)
        )
        
        assert xml is not None
        assert "Credit Transfer" in xml or "pacs.008" in xml
    
    def test_create_repo_settlement_message(self, generator):
        """Should create repo settlement message"""
        xml = generator.create_repo_settlement_message(
            trade_id="REPO001",
            counterparty_bic="SCBKTHBKXXX",
            counterparty_name="SCB",
            amount=200000000.00,
            value_date=date(2025, 9, 3),
            is_near_leg=True
        )
        
        assert xml is not None
        assert "200000000" in xml
    
    def test_amount_formatting(self, generator):
        """Amount should be formatted correctly"""
        xml = generator.create_credit_transfer(
            amount=1500000.50,
            debtor_account="1234567890",
            creditor_bic="KASITHBKXXX",
            creditor_name="Test",
            creditor_account="0987654321",
            value_date=date(2025, 9, 3),
            end_to_end_id="TEST"
        )
        
        # Amount should have 2 decimal places
        assert "1500000.50" in xml


class TestTSDMessageGenerator:
    """Tests for TSD settlement instruction generation"""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance"""
        return TSDMessageGenerator(
            participant_code="TSD001",
            participant_name="Test Bank PCL"
        )
    
    def test_create_dvp_instruction(self, generator):
        """Should create DVP settlement instruction"""
        instruction = generator.create_dvp_instruction(
            trade_id="TRD001",
            isin="TH0623A3B702",
            security_name="LB236A",
            face_value=Decimal("10000000"),
            settlement_amount=Decimal("10250000"),
            counterparty_code="TSD002",
            counterparty_name="Kasikorn Bank",
            settlement_date=date(2025, 9, 3),
            is_buy=True
        )
        
        assert instruction is not None
        assert instruction["instruction_type"] == "DVP"
        assert instruction["isin"] == "TH0623A3B702"
        assert instruction["face_value"] == 10000000
        assert instruction["is_buy"] is True
    
    def test_create_fop_instruction(self, generator):
        """Should create FoP instruction for collateral"""
        instruction = generator.create_fop_instruction(
            trade_id="REPO001",
            isin="TH0623A3B702",
            security_name="LB236A",
            face_value=Decimal("15000000"),
            counterparty_code="TSD002",
            counterparty_name="SCB",
            settlement_date=date(2025, 9, 3),
            is_deliver=True,
            purpose="COLLATERAL"
        )
        
        assert instruction is not None
        assert instruction["instruction_type"] == "FOP"
        assert instruction["face_value"] == 15000000
        assert instruction["purpose"] == "COLLATERAL"
    
    def test_dvp_instruction_is_valid_json(self, generator):
        """DVP instruction should be valid JSON"""
        instruction = generator.create_dvp_instruction(
            trade_id="TRD001",
            isin="TH0623A3B702",
            security_name="LB236A",
            face_value=Decimal("10000000"),
            settlement_amount=Decimal("10250000"),
            counterparty_code="TSD002",
            counterparty_name="Test",
            settlement_date=date(2025, 9, 3),
            is_buy=True
        )
        
        # Should serialize to JSON without error
        json_str = json.dumps(instruction, default=str)
        parsed = json.loads(json_str)
        assert parsed["isin"] == "TH0623A3B702"
    
    def test_fop_is_deliver_flag(self, generator):
        """FoP instruction should have correct delivery flag"""
        deliver = generator.create_fop_instruction(
            trade_id="REPO001",
            isin="TH0623A3B702",
            security_name="LB236A",
            face_value=Decimal("10000000"),
            counterparty_code="TSD002",
            counterparty_name="Test",
            settlement_date=date(2025, 9, 3),
            is_deliver=True,
            purpose="COLLATERAL"
        )
        
        receive = generator.create_fop_instruction(
            trade_id="REPO002",
            isin="TH0623A3B702",
            security_name="LB236A",
            face_value=Decimal("10000000"),
            counterparty_code="TSD002",
            counterparty_name="Test",
            settlement_date=date(2025, 9, 8),
            is_deliver=False,
            purpose="COLLATERAL_RETURN"
        )
        
        assert deliver["is_deliver"] is True
        assert receive["is_deliver"] is False


class TestSettlementServiceSingletons:
    """Tests for service singleton pattern"""
    
    def test_bahtnet_generator_singleton(self):
        """Should return same instance"""
        gen1 = get_bahtnet_generator()
        gen2 = get_bahtnet_generator()
        
        assert gen1 is gen2
    
    def test_tsd_generator_singleton(self):
        """Should return same instance"""
        gen1 = get_tsd_generator()
        gen2 = get_tsd_generator()
        
        assert gen1 is gen2


class TestMessageFileSaving:
    """Tests for saving messages to files"""
    
    def test_bahtnet_save_to_file(self, tmp_path):
        """Should save BAHTNET message to file"""
        generator = BAHTNETMessageGenerator(
            bank_code="0020000000000",
            bank_name="Test Bank",
            bank_bic="TESTHTHB",
            output_path=str(tmp_path)
        )
        
        xml = generator.create_credit_transfer(
            amount=100000000.00,
            debtor_account="1234567890",
            creditor_bic="KASITHBKXXX",
            creditor_name="Test",
            creditor_account="0987654321",
            value_date=date(2025, 9, 3),
            end_to_end_id="TEST001"
        )
        
        filepath = generator.save_to_file(xml)
        
        assert filepath is not None
        # Check file exists and contains content
        with open(filepath, 'r') as f:
            content = f.read()
            assert "pacs.008" in content
    
    def test_tsd_save_to_file(self, tmp_path):
        """Should save TSD instruction to file"""
        generator = TSDMessageGenerator(
            participant_code="TSD001",
            participant_name="Test Bank",
            output_path=str(tmp_path)
        )
        
        instruction = generator.create_dvp_instruction(
            trade_id="TRD001",
            isin="TH0623A3B702",
            security_name="LB236A",
            face_value=Decimal("10000000"),
            settlement_amount=Decimal("10250000"),
            counterparty_code="TSD002",
            counterparty_name="Test",
            settlement_date=date(2025, 9, 3),
            is_buy=True
        )
        
        filepath = generator.save_to_file(instruction)
        
        assert filepath is not None
        with open(filepath, 'r') as f:
            content = json.load(f)
            assert content["isin"] == "TH0623A3B702"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
