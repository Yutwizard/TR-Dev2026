"""
Treasury Management System - API Router Tests
===============================================

Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoints:
    """Tests for health check endpoints"""
    
    def test_health_check(self, client):
        """Basic health check should return 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_detailed_health(self, client):
        """Detailed health check should return service info"""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "system" in data
    
    def test_ready_endpoint(self, client):
        """Readiness check should return 200"""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True
    
    def test_live_endpoint(self, client):
        """Liveness check should return 200"""
        response = client.get("/live")
        assert response.status_code == 200
        assert response.json()["alive"] is True


class TestAuthEndpoints:
    """Tests for authentication endpoints"""
    
    def test_login_success(self, client):
        """Valid credentials should return tokens"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Invalid credentials should return 401"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "wrong"}
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Should return current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "ADMIN"
    
    def test_protected_endpoint_without_auth(self, client):
        """Protected endpoint without auth should return 401"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_json_login(self, client):
        """JSON login should work"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "trader1", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestSecuritiesEndpoints:
    """Tests for securities API"""
    
    def test_list_securities(self, client, auth_headers):
        """Should list securities"""
        response = client.get("/api/v1/securities", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_filter_by_type(self, client, auth_headers):
        """Should filter by security type"""
        response = client.get(
            "/api/v1/securities?security_type=TBOND",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["security_type"] == "TBOND"
    
    def test_get_security_by_id(self, client, auth_headers):
        """Should get specific security"""
        response = client.get("/api/v1/securities/SEC001", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["security_id"] == "SEC001"
    
    def test_get_security_not_found(self, client, auth_headers):
        """Should return 404 for unknown security"""
        response = client.get("/api/v1/securities/UNKNOWN", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_security_types(self, client):
        """Should list security types (public endpoint)"""
        response = client.get("/api/v1/securities/types/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


class TestBondTradesEndpoints:
    """Tests for bond trades API"""
    
    def test_list_trades(self, client, auth_headers):
        """Should list trades"""
        response = client.get("/api/v1/bond-trades", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    def test_get_trade_by_id(self, client, auth_headers):
        """Should get specific trade"""
        response = client.get("/api/v1/bond-trades/TRD001", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["trade_id"] == "TRD001"
    
    def test_filter_by_status(self, client, auth_headers):
        """Should filter by status"""
        response = client.get(
            "/api/v1/bond-trades?status=PENDING_APPROVAL",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestPositionsEndpoints:
    """Tests for positions API"""
    
    def test_list_bond_positions(self, client, auth_headers):
        """Should list bond positions"""
        response = client.get("/api/v1/positions/bonds", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_cash_positions(self, client, auth_headers):
        """Should list cash positions"""
        response = client.get("/api/v1/positions/cash", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_position_summary(self, client, auth_headers):
        """Should get position summary"""
        response = client.get("/api/v1/positions/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_bond_face_value" in data
        assert "total_cash_balance" in data
    
    def test_limit_utilizations(self, client, auth_headers):
        """Should list limit utilizations"""
        response = client.get("/api/v1/positions/limits", headers=auth_headers)
        assert response.status_code == 200


class TestCalendarEndpoints:
    """Tests for calendar API"""
    
    def test_check_business_day(self, client):
        """Should check if date is business day"""
        response = client.get("/api/v1/calendar/check/2025-09-03")
        assert response.status_code == 200
        data = response.json()
        assert "is_business_day" in data
        assert data["is_business_day"] is True  # Wednesday
    
    def test_check_weekend(self, client):
        """Weekend should not be business day"""
        response = client.get("/api/v1/calendar/check/2025-09-06")
        assert response.status_code == 200
        data = response.json()
        assert data["is_business_day"] is False
        assert data["is_weekend"] is True
    
    def test_settlement_date(self, client):
        """Should calculate settlement date"""
        response = client.get(
            "/api/v1/calendar/settlement-date?trade_date=2025-09-01&days=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["settlement_date"] == "2025-09-03"
    
    def test_holidays_2025(self, client):
        """Should list holidays for 2025"""
        response = client.get("/api/v1/calendar/holidays/2025")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 15  # Thailand has many holidays
    
    def test_add_business_days(self, client):
        """Should add business days"""
        response = client.get(
            "/api/v1/calendar/add-business-days?start_date=2025-09-01&days=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert "result_date" in data
    
    def test_current_info(self, client):
        """Should get current date info"""
        response = client.get("/api/v1/calendar/current-info")
        assert response.status_code == 200
        data = response.json()
        assert "current_date" in data
        assert "is_business_day" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
