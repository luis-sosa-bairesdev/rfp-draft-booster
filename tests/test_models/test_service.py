"""
Unit tests for Service model.

Tests cover:
- Service creation and validation
- ServiceCategory enum
- Service JSON serialization/deserialization
- Helper methods and utility functions
- Load services from JSON file
- Get default services
"""

import pytest
from models.service import (
    Service, 
    ServiceCategory, 
    load_services_from_json, 
    get_default_services
)
import json
import tempfile
import os


class TestServiceModel:
    """Test Service model creation and validation."""
    
    def test_create_service_with_defaults(self):
        """Test creating a service with default values."""
        service = Service(
            id="svc-001",
            name="Cloud Infrastructure",
            category=ServiceCategory.TECHNICAL,
            description="AWS cloud services",
            capabilities=["AWS", "Docker", "Kubernetes"]
        )
        
        assert service.id == "svc-001"
        assert service.name == "Cloud Infrastructure"
        assert service.description == "AWS cloud services"
        assert service.category == ServiceCategory.TECHNICAL
        assert service.success_rate == 0.95
        assert service.tags == []
    
    def test_create_service_with_tags(self):
        """Test creating a service with tags."""
        service = Service(
            id="svc-002",
            name="Mobile Development",
            category=ServiceCategory.FUNCTIONAL,
            description="iOS and Android development",
            capabilities=["iOS", "Android", "React Native"],
            tags=["ios", "android", "react-native"]
        )
        
        assert len(service.tags) == 3
        assert "ios" in service.tags
    
    def test_service_to_dict(self):
        """Test converting service to dictionary."""
        service = Service(
            id="svc-003",
            name="QA Testing",
            category=ServiceCategory.FUNCTIONAL,
            description="Quality assurance",
            capabilities=["Automated testing", "Manual testing"],
            tags=["automation", "manual"]
        )
        
        service_dict = service.to_dict()
        
        assert service_dict["id"] == "svc-003"
        assert service_dict["name"] == "QA Testing"
        assert service_dict["category"] == "functional"
        assert len(service_dict["tags"]) == 2
    
    def test_service_from_dict(self):
        """Test creating service from dictionary."""
        data = {
            "id": "svc-004",
            "name": "DevOps",
            "category": "technical",
            "description": "CI/CD pipeline",
            "capabilities": ["Docker", "Kubernetes", "Jenkins"],
            "tags": ["docker", "kubernetes"]
        }
        
        service = Service.from_dict(data)
        
        assert service.id == "svc-004"
        assert service.name == "DevOps"
        assert service.category == ServiceCategory.TECHNICAL
        assert len(service.tags) == 2


class TestServiceCategory:
    """Test ServiceCategory enum."""
    
    def test_service_category_values(self):
        """Test all service category values."""
        assert ServiceCategory.TECHNICAL.value == "technical"
        assert ServiceCategory.FUNCTIONAL.value == "functional"
        assert ServiceCategory.TIMELINE.value == "timeline"
        assert ServiceCategory.BUDGET.value == "budget"
        assert ServiceCategory.COMPLIANCE.value == "compliance"


class TestLoadServices:
    """Test loading services from JSON."""
    
    def test_load_services_from_json_valid(self):
        """Test loading services from a valid JSON file."""
        # Create temporary JSON file with correct format
        services_data = {
            "version": "1.0",
            "last_updated": "2025-01-13",
            "services": [
                {
                    "id": "svc-001",
                    "name": "Test Service",
                    "category": "technical",
                    "description": "Test description",
                    "capabilities": ["Test capability"],
                    "tags": ["test"]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(services_data, f)
            temp_path = f.name
        
        try:
            services = load_services_from_json(temp_path)
            
            assert len(services) == 1
            assert services[0].id == "svc-001"
            assert services[0].name == "Test Service"
        finally:
            os.unlink(temp_path)
    
    def test_load_services_from_json_file_not_found(self):
        """Test loading services from non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_services_from_json("nonexistent.json")
    
    def test_load_services_from_json_invalid_json(self):
        """Test loading services from invalid JSON raises error."""
        # Create temporary invalid JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_services_from_json(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_get_default_services(self):
        """Test getting default services."""
        services = get_default_services()
        
        assert len(services) > 0
        assert all(isinstance(s, Service) for s in services)
        
        # Check that all default services have required fields
        for service in services:
            assert service.id
            assert service.name
            assert service.description
            assert service.category

