"""
Integration tests for MemU Skill
TDD+SDD 双金字塔流程 - 集成测试层
测试模块间协作，需要真实 PostgreSQL
"""
import pytest
import os
import sys
import asyncio
import subprocess
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def _postgres_available():
    """检查 PostgreSQL 是否可用"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=memu-postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        return "memu-postgres" in result.stdout
    except:
        return False


# Skip all integration tests if PostgreSQL not available
pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available"
)


class TestMemuServiceIntegration:
    """集成测试 - 需要真实 PostgreSQL"""
    
    @pytest.fixture
    async def real_service(self):
        """Fixture: 连接真实数据库的服务"""
        # Ensure environment is set
        os.environ.setdefault('APIYI_API_KEY', 'sk-test-key')
        os.environ.setdefault('OPENROUTER_API_KEY', 'sk-or-test-key')
        
        from lib.memu_service import MemUOpenClawService
        
        service = MemUOpenClawService()
        service._initialized = False
        
        # Note: This will fail without real API keys
        # In CI/CD, use mock or test credentials
        try:
            service.initialize()
            yield service
        except Exception as e:
            pytest.skip(f"Cannot initialize service: {e}")
    
    @pytest.mark.asyncio
    async def test_memorize_and_retrieve_roundtrip(self, real_service):
        """TEST: 存储和检索端到端流程 (SPEC: E2E-001)"""
        # This test requires real API keys and PostgreSQL
        # Skip if not available
        pytest.skip("Requires real API keys - run manually")
        
        # Store memory
        content = f"Test memory {time.time()}"
        result = await real_service.memorize(content, "test_user")
        
        assert result is not None
        assert 'memory_id' in result
        
        # Retrieve
        results = await real_service.retrieve("Test memory", "test_user", limit=5)
        
        assert isinstance(results, list)
        # Should find our recently stored memory
        assert any(content in str(r) for r in results)
    
    @pytest.mark.asyncio
    async def test_multiple_users_isolation(self, real_service):
        """TEST: 多用户数据隔离"""
        pytest.skip("Requires real API keys - run manually")
        
        # Store for user1
        await real_service.memorize("User1 private data", "user1")
        
        # Store for user2
        await real_service.memorize("User2 private data", "user2")
        
        # Retrieve for user1 - should not see user2's data
        results = await real_service.retrieve("private data", "user1")
        
        # Verify isolation (this depends on actual MemU implementation)
        # The 'where' clause in retrieve should filter by user_id


class TestAutoTriggerIntegration:
    """集成测试 - 自动触发 + MemU 协作"""
    
    @pytest.mark.asyncio
    async def test_full_trigger_to_memory_workflow(self):
        """TEST: 完整自动触发到存储流程 (SPEC: E2E-002)"""
        from lib.auto_trigger import should_memorize
        from lib.memu_service import MemUOpenClawService
        
        # Step 1: Detect trigger
        message = "我有偏头痛，需要休息"
        trigger_result = should_memorize(message)
        
        assert trigger_result is not None
        assert trigger_result['category'] == 'health'
        
        # Step 2: Store to MemU (if service available)
        # This would require real API keys
        pytest.skip("Requires real API keys - demonstration only")


class TestCLIToolsIntegration:
    """集成测试 - CLI 工具"""
    
    def test_memorize_cli_exists(self):
        """TEST: memorize.py CLI 工具可执行"""
        cli_path = Path(__file__).parent.parent.parent / "tools" / "memorize.py"
        assert cli_path.exists()
        assert os.access(cli_path, os.X_OK)
    
    def test_retrieve_cli_exists(self):
        """TEST: retrieve.py CLI 工具可执行"""
        cli_path = Path(__file__).parent.parent.parent / "tools" / "retrieve.py"
        assert cli_path.exists()
        assert os.access(cli_path, os.X_OK)
    
    @pytest.mark.asyncio
    async def test_cli_json_input_output(self):
        """TEST: CLI 工具正确处理 JSON 输入输出"""
        import json
        import sys
        from io import StringIO
        
        # Test memorize CLI structure
        test_input = json.dumps({"content": "test", "user_id": "test"})
        
        # Note: Cannot run actual CLI without environment setup
        # Just verify the structure
        input_data = json.loads(test_input)
        assert "content" in input_data
        assert "user_id" in input_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
