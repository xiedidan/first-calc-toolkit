"""
测试成本基准管理的错误处理
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.models.cost_benchmark import CostBenchmark
from backend.app.models.model_version import ModelVersion
from backend.app.models.hospital import Hospital


client = TestClient(app)


def get_auth_headers(hospital_id: int = 1) -> dict:
    """获取认证头"""
    # 这里需要根据实际的认证机制获取token
    # 简化处理，假设已经有token
    return {
        "Authorization": "Bearer test_token",
        "X-Hospital-ID": str(hospital_id)
    }


class TestErrorHandling:
    """测试错误处理"""
    
    def test_create_with_missing_fields(self):
        """测试创建时缺少必填字段"""
        # 缺少科室代码
        response = client.post(
            "/api/v1/cost-benchmarks",
            json={
                "department_name": "内科",
                "version_id": 1,
                "version_name": "V1.0",
                "dimension_code": "DIM001",
                "dimension_name": "业务量",
                "benchmark_value": 100.00
            },
            headers=get_auth_headers()
        )
        assert response.status_code == 422  # Pydantic validation error
        
    def test_create_with_invalid_benchmark_value(self):
        """测试创建时基准值无效"""
        # 基准值为0
        response = client.post(
            "/api/v1/cost-benchmarks",
            json={
                "department_code": "DEPT001",
                "department_name": "内科",
                "version_id": 1,
                "version_name": "V1.0",
                "dimension_code": "DIM001",
                "dimension_name": "业务量",
                "benchmark_value": 0
            },
            headers=get_auth_headers()
        )
        assert response.status_code == 400
        assert "基准值必须大于0" in response.json()["detail"]
        
        # 基准值为负数
        response = client.post(
            "/api/v1/cost-benchmarks",
            json={
                "department_code": "DEPT001",
                "department_name": "内科",
                "version_id": 1,
                "version_name": "V1.0",
                "dimension_code": "DIM001",
                "dimension_name": "业务量",
                "benchmark_value": -10.00
            },
            headers=get_auth_headers()
        )
        assert response.status_code == 400
        assert "基准值必须大于0" in response.json()["detail"]
        
        # 基准值超过最大值
        response = client.post(
            "/api/v1/cost-benchmarks",
            json={
                "department_code": "DEPT001",
                "department_name": "内科",
                "version_id": 1,
                "version_name": "V1.0",
                "dimension_code": "DIM001",
                "dimension_name": "业务量",
                "benchmark_value": 9999999999.99
            },
            headers=get_auth_headers()
        )
        assert response.status_code == 400
        assert "基准值不能超过" in response.json()["detail"]
    
    def test_create_duplicate(self):
        """测试创建重复记录"""
        # 第一次创建
        data = {
            "department_code": "DEPT001",
            "department_name": "内科",
            "version_id": 1,
            "version_name": "V1.0",
            "dimension_code": "DIM001",
            "dimension_name": "业务量",
            "benchmark_value": 100.00
        }
        response = client.post(
            "/api/v1/cost-benchmarks",
            json=data,
            headers=get_auth_headers()
        )
        
        if response.status_code == 201:
            # 第二次创建相同记录
            response = client.post(
                "/api/v1/cost-benchmarks",
                json=data,
                headers=get_auth_headers()
            )
            assert response.status_code == 400
            assert "已存在" in response.json()["detail"]
    
    def test_get_nonexistent_benchmark(self):
        """测试获取不存在的成本基准"""
        response = client.get(
            "/api/v1/cost-benchmarks/999999",
            headers=get_auth_headers()
        )
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_update_nonexistent_benchmark(self):
        """测试更新不存在的成本基准"""
        response = client.put(
            "/api/v1/cost-benchmarks/999999",
            json={"benchmark_value": 200.00},
            headers=get_auth_headers()
        )
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_delete_nonexistent_benchmark(self):
        """测试删除不存在的成本基准"""
        response = client.delete(
            "/api/v1/cost-benchmarks/999999",
            headers=get_auth_headers()
        )
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_export_empty_data(self):
        """测试导出空数据"""
        # 使用不存在的筛选条件
        response = client.get(
            "/api/v1/cost-benchmarks/export",
            params={"version_id": 999999},
            headers=get_auth_headers()
        )
        assert response.status_code == 400
        assert "没有可导出的数据" in response.json()["detail"]
    
    def test_cross_tenant_access(self):
        """测试跨租户访问"""
        # 创建一个成本基准
        data = {
            "department_code": "DEPT001",
            "department_name": "内科",
            "version_id": 1,
            "version_name": "V1.0",
            "dimension_code": "DIM001",
            "dimension_name": "业务量",
            "benchmark_value": 100.00
        }
        response = client.post(
            "/api/v1/cost-benchmarks",
            json=data,
            headers=get_auth_headers(hospital_id=1)
        )
        
        if response.status_code == 201:
            benchmark_id = response.json()["id"]
            
            # 尝试用另一个医疗机构访问
            response = client.get(
                f"/api/v1/cost-benchmarks/{benchmark_id}",
                headers=get_auth_headers(hospital_id=2)
            )
            assert response.status_code in [403, 404]
    
    def test_invalid_version_id(self):
        """测试无效的版本ID"""
        response = client.post(
            "/api/v1/cost-benchmarks",
            json={
                "department_code": "DEPT001",
                "department_name": "内科",
                "version_id": 999999,
                "version_name": "不存在的版本",
                "dimension_code": "DIM001",
                "dimension_name": "业务量",
                "benchmark_value": 100.00
            },
            headers=get_auth_headers()
        )
        assert response.status_code == 404
        assert "版本不存在" in response.json()["detail"]
    
    def test_pagination_parameters(self):
        """测试分页参数验证"""
        # 无效的页码
        response = client.get(
            "/api/v1/cost-benchmarks",
            params={"page": 0},
            headers=get_auth_headers()
        )
        assert response.status_code == 422
        
        # 无效的每页数量
        response = client.get(
            "/api/v1/cost-benchmarks",
            params={"size": 0},
            headers=get_auth_headers()
        )
        assert response.status_code == 422
        
        # 超过最大每页数量
        response = client.get(
            "/api/v1/cost-benchmarks",
            params={"size": 10000},
            headers=get_auth_headers()
        )
        assert response.status_code == 422


class TestNetworkErrorHandling:
    """测试网络错误处理（前端）"""
    
    def test_timeout_handling(self):
        """测试超时处理"""
        # 这个测试需要在前端进行
        # 可以通过模拟慢速API来测试
        pass
    
    def test_network_error_handling(self):
        """测试网络错误处理"""
        # 这个测试需要在前端进行
        # 可以通过断开网络连接来测试
        pass


class TestFormValidation:
    """测试表单验证（前端）"""
    
    def test_required_field_validation(self):
        """测试必填字段验证"""
        # 这个测试需要在前端进行
        # 使用Vue Test Utils或Cypress
        pass
    
    def test_number_field_validation(self):
        """测试数字字段验证"""
        # 这个测试需要在前端进行
        pass
    
    def test_range_validation(self):
        """测试范围验证"""
        # 这个测试需要在前端进行
        pass


if __name__ == "__main__":
    print("运行错误处理测试...")
    print("\n注意：这些测试需要：")
    print("1. 后端服务正在运行")
    print("2. 数据库已初始化")
    print("3. 有效的认证token")
    print("4. 测试数据已准备")
    print("\n运行命令: pytest test_cost_benchmark_error_handling.py -v")
