import json
import pytest
from datetime import datetime, timedelta


def test_product_sales_report(client, test_order, auth_headers):
    """Test generating a product sales report without date filters"""
    response = client.get('/api/reports/products', headers=auth_headers)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'report' in response_data
    assert 'products' in response_data['report']
    
    # Verify products are in the report and sorted correctly
    products = response_data['report']['products']
    assert len(products) > 0
    
    # Check if products are sorted by total quantity in descending order
    if len(products) > 1:
        for i in range(len(products) - 1):
            assert products[i]['total_quantity'] >= products[i + 1]['total_quantity']


def test_product_sales_report_with_date_range(client, test_order, auth_headers, test_db):
    """Test generating a product sales report with date filters"""
    # Create a date range
    today = datetime.utcnow().date()
    start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Test with date range
    response = client.get(
        f'/api/reports/products?start_date={start_date}&end_date={end_date}',
        headers=auth_headers
    )
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'report' in response_data
    assert response_data['report']['start_date'] == start_date
    assert response_data['report']['end_date'] == end_date


def test_product_sales_report_invalid_date_format(client, auth_headers):
    """Test report with invalid date format"""
    response = client.get(
        '/api/reports/products?start_date=invalid-date',
        headers=auth_headers
    )
    assert response.status_code == 400


def test_product_sales_report_empty_results(client, auth_headers, test_db):
    """Test report with date range that returns no results"""
    # Use future dates to ensure no orders match
    future_date = (datetime.utcnow().date() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    response = client.get(
        f'/api/reports/products?start_date={future_date}',
        headers=auth_headers
    )
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'report' in response_data
    assert 'products' in response_data['report']
    assert len(response_data['report']['products']) == 0