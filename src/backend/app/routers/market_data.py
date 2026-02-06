"""
Treasury Management System - Market Data Router
================================================

API endpoints for ThaiBMA market data management.

Endpoints:
- POST /import: Import Mark2Market CSV file
- GET /: List market data with filtering
- GET /{security_id}/latest: Get latest price for security
- GET /{security_id}/history: Get price history
- GET /import-log: View import history
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, UserInToken
from app.database import get_db
from app.services.market_data_service import (
    MarketDataService, 
    import_thaibma_market_data,
    get_latest_price
)
from app.models.market_data import ThaiBMAMarketData, MarketDataImportLog


router = APIRouter(prefix="/market-data", tags=["Market Data"])


# =============================================================================
# Request/Response Models
# =============================================================================
class MarketDataResponse(BaseModel):
    """Market data response"""
    id: int
    data_date: date
    security_id: str
    thaibma_symbol: str
    isin: Optional[str]
    clean_price: float
    dirty_price: Optional[float]
    accrued_interest: Optional[float]
    market_yield: Optional[float]
    modified_duration: Optional[float]
    bond_type: Optional[str]
    
    class Config:
        from_attributes = True


class MarketDataListResponse(BaseModel):
    """List of market data"""
    items: List[MarketDataResponse]
    total: int
    page: int
    size: int


class PriceHistoryResponse(BaseModel):
    """Price history for a security"""
    security_id: str
    thaibma_symbol: str
    from_date: date
    to_date: date
    data_points: List[MarketDataResponse]


class ImportRequest(BaseModel):
    """Import request"""
    import_date: Optional[date] = Field(None, description="Date this data represents")


class ImportResponse(BaseModel):
    """Import response"""
    batch_id: str
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    price_alerts: int
    missing_securities: int
    message: str


class ImportLogResponse(BaseModel):
    """Import log entry"""
    batch_id: str
    import_date: date
    file_name: str
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    price_movement_alerts: int
    started_at: Optional[date]
    completed_at: Optional[date]
    
    class Config:
        from_attributes = True


class LatestPriceResponse(BaseModel):
    """Latest price response"""
    security_id: str
    thaibma_symbol: Optional[str]
    data_date: date
    clean_price: float
    accrued_interest: Optional[float]
    dirty_price: Optional[float]
    market_yield: Optional[float]
    source: str


# =============================================================================
# Endpoints
# =============================================================================
@router.post("/import", response_model=ImportResponse)
async def import_market_data(
    import_date: Optional[date] = Query(None, description="Date this data represents (defaults to today)"),
    file: UploadFile = File(..., description="ThaiBMA Mark2Market CSV file"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Import ThaiBMA Mark2Market CSV file.
    
    Upload the daily EOD price file from ThaiBMA portal.
    The system will:
    - Parse bond symbols and match to security master
    - Validate prices for unusual movements (>5% warning, >10% alert, >20% critical)
    - Store clean prices, yields, and risk metrics
    - Log import statistics
    
    **Required Permission:** IMPORT_MARKET_DATA
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Import the file
        import_log = import_thaibma_market_data(
            db=db,
            file_path=temp_path,
            import_date=import_date,
            user_id=current_user.user_id
        )
        
        # Clean up temp file
        import os
        os.remove(temp_path)
        
        # Build response
        message = f"Import {import_log.status.lower()}"
        if import_log.price_movement_alerts > 0:
            message += f" with {import_log.price_movement_alerts} price alerts"
        if import_log.missing_securities > 0:
            message += f", {import_log.missing_securities} securities not found"
        
        return ImportResponse(
            batch_id=import_log.batch_id,
            status=import_log.status,
            total_records=import_log.total_records,
            successful_records=import_log.successful_records,
            failed_records=import_log.failed_records,
            price_alerts=import_log.price_movement_alerts,
            missing_securities=import_log.missing_securities,
            message=message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("", response_model=MarketDataListResponse)
async def list_market_data(
    data_date: Optional[date] = Query(None, description="Filter by specific date"),
    security_id: Optional[str] = Query(None, description="Filter by security ID"),
    thaibma_symbol: Optional[str] = Query(None, description="Filter by ThaiBMA symbol"),
    bond_type: Optional[str] = Query(None, description="Filter by bond type (Government, SOE, Corporate)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    List market data with filtering options.
    
    Returns daily EOD prices and related metrics from ThaiBMA.
    """
    service = MarketDataService(db)
    
    query = db.query(ThaiBMAMarketData).filter(ThaiBMAMarketData.is_valid == True)
    
    if data_date:
        query = query.filter(ThaiBMAMarketData.data_date == data_date)
    if security_id:
        query = query.filter(ThaiBMAMarketData.security_id == security_id)
    if thaibma_symbol:
        query = query.filter(ThaiBMAMarketData.thaibma_symbol.ilike(f"%{thaibma_symbol}%"))
    if bond_type:
        query = query.filter(ThaiBMAMarketData.bond_type.ilike(f"%{bond_type}%"))
    
    total = query.count()
    items = query.order_by(ThaiBMAMarketData.data_date.desc()).offset((page - 1) * size).limit(size).all()
    
    return MarketDataListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )


@router.get("/{security_id}/latest", response_model=LatestPriceResponse)
async def get_latest_market_price(
    security_id: str,
    as_of_date: Optional[date] = Query(None, description="Get price as of this date"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get the latest market price for a security.
    
    Returns the most recent clean price, accrued interest, and yield data.
    """
    service = MarketDataService(db)
    data = service.get_latest_market_data(security_id, as_of_date)
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No market data found for security {security_id}"
        )
    
    return LatestPriceResponse(
        security_id=data.security_id,
        thaibma_symbol=data.thaibma_symbol,
        data_date=data.data_date,
        clean_price=float(data.clean_price),
        accrued_interest=float(data.accrued_interest) if data.accrued_interest else None,
        dirty_price=float(data.dirty_price) if data.dirty_price else None,
        market_yield=float(data.market_yield) if data.market_yield else None,
        source="ThaiBMA"
    )


@router.get("/{security_id}/history", response_model=PriceHistoryResponse)
async def get_price_history(
    security_id: str,
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get price history for a security over a date range.
    
    Useful for charting price trends and analysis.
    """
    service = MarketDataService(db)
    
    # Get security info
    first_record = service.get_latest_market_data(security_id)
    if not first_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security {security_id} not found"
        )
    
    history = service.get_price_history(security_id, from_date, to_date)
    
    return PriceHistoryResponse(
        security_id=security_id,
        thaibma_symbol=first_record.thaibma_symbol,
        from_date=from_date,
        to_date=to_date,
        data_points=history
    )


@router.get("/import-log", response_model=List[ImportLogResponse])
async def list_import_logs(
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    status: Optional[str] = Query(None, description="Filter by status (PENDING, COMPLETED, FAILED)"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    List market data import history.
    
    Track import batches and troubleshoot issues.
    """
    query = db.query(MarketDataImportLog)
    
    if from_date:
        query = query.filter(MarketDataImportLog.import_date >= from_date)
    if to_date:
        query = query.filter(MarketDataImportLog.import_date <= to_date)
    if status:
        query = query.filter(MarketDataImportLog.status == status.upper())
    
    logs = query.order_by(MarketDataImportLog.import_date.desc()).limit(limit).all()
    return logs


@router.get("/import-log/{batch_id}", response_model=ImportLogResponse)
async def get_import_log_detail(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: UserInToken = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific import batch.
    """
    log = db.query(MarketDataImportLog).filter(MarketDataImportLog.batch_id == batch_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Import batch {batch_id} not found"
        )
    
    return log
