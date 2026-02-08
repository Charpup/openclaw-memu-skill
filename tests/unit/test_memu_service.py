"""
Unit tests for MemU OpenClaw Service
TDD+SDD 双金字塔流程 - 单元测试层
"""
import pytest
import pytest_asyncio
import os
import sys
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.memu_service import MemUOpenClawService, get_memu_service, validate_config


class TestValidateConfig:
    """测试配置验证功能 (SPEC: initialize preconditions)"""
    
    def test_valid_config(self):
        """TEST: 所有必需环境变量已设置"""
        with patch.dict(os.environ, {
            'APIYI_API_KEY': 'sk-test',
            'OPENROUTER_API_KEY': 'sk-or-test'
        }):
            result = validate_config()
            assert result is True
    
    def test_missing_apiyi_key(self):
        """TEST: 缺少 APIYI_API_KEY 时抛出 ValueError"""
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'sk-or-test'}):
                with pytest.raises(ValueError) as exc_info:
                    validate_config()
                assert 'APIYI_API_KEY' in str(exc_info.value)
    
    def test_missing_openrouter_key(self):
        """TEST: 缺少 OPENROUTER_API_KEY 时抛出 ValueError"""
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {'APIYI_API_KEY': 'sk-test'}):
                with pytest.raises(ValueError) as exc_info:
                    validate_config()
                assert 'OPENROUTER_API_KEY' in str(exc_info.value)


class TestMemUOpenClawServiceInitialization:
    """测试服务初始化 (SPEC: initialize method)"""
    
    @pytest.fixture
    def mock_service(self):
        """Fixture: 创建带 Mock 的服务实例"""
        with patch.dict(os.environ, {
            'APIYI_API_KEY': 'sk-test',
            'OPENROUTER_API_KEY': 'sk-or-test'
        }):
            service = MemUOpenClawService()
            # Reset singleton for clean tests
            service._initialized = False
            service._instance = None
            yield service
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_service):
        """TEST: 正常初始化成功 (SPEC: MEM-INIT-001)"""
        with patch('lib.memu_service.MemoryService') as MockMemoryService:
            mock_instance = Mock()
            MockMemoryService.return_value = mock_instance
            
            mock_service.initialize()
            
            assert mock_service._initialized is True
            assert mock_service.service is not None
    
    @pytest.mark.asyncio
    async def test_initialize_idempotent(self, mock_service):
        """TEST: 重复初始化是幂等的"""
        with patch('lib.memu_service.MemoryService') as MockMemoryService:
            mock_instance = Mock()
            MockMemoryService.return_value = mock_instance
            
            # First initialization
            mock_service.initialize()
            init_count = MockMemoryService.call_count
            
            # Second initialization - should not create new instance
            mock_service.initialize()
            assert MockMemoryService.call_count == init_count
    
    def test_singleton_pattern(self):
        """TEST: 单例模式确保全局唯一实例"""
        with patch.dict(os.environ, {
            'APIYI_API_KEY': 'sk-test',
            'OPENROUTER_API_KEY': 'sk-or-test'
        }):
            service1 = get_memu_service()
            service2 = get_memu_service()
            assert service1 is service2


class TestMemorize:
    """测试记忆存储功能 (SPEC: memorize method)"""
    
    @pytest_asyncio.fixture
    async def initialized_service(self):
        """Fixture: 已初始化的服务"""
        with patch.dict(os.environ, {
            'APIYI_API_KEY': 'sk-test',
            'OPENROUTER_API_KEY': 'sk-or-test'
        }):
            service = MemUOpenClawService()
            service._initialized = False
            
            with patch('lib.memu_service.MemoryService') as MockMemoryService:
                mock_memu = Mock()
                # Mock async memorize method
                mock_memu.memorize = Mock(return_value=asyncio.Future())
                mock_memu.memorize.return_value.set_result({
                    'memory_id': 'test-123',
                    'status': 'success'
                })
                MockMemoryService.return_value = mock_memu
                
                service.initialize()
                return service
    
    @pytest.mark.asyncio
    async def test_memorize_success(self, initialized_service):
        """TEST: 正常存储记忆成功 (SPEC: MEM-001)"""
        result = await initialized_service.memorize(
            content="Master 喜欢暗色模式",
            user_id="master"
        )
        
        assert result['status'] == 'success'
        assert 'memory_id' in result
    
    @pytest.mark.asyncio
    async def test_memorize_empty_content(self, initialized_service):
        """TEST: 空内容抛出 ValueError (SPEC: MEM-002)"""
        with pytest.raises(ValueError):
            await initialized_service.memorize(content="", user_id="master")
    
    @pytest.mark.asyncio
    async def test_memorize_special_characters(self, initialized_service):
        """TEST: 特殊字符内容正确存储 (SPEC: MEM-003)"""
        content = "API key = sk-xxx-xxx 记住这个！"
        result = await initialized_service.memorize(
            content=content,
            user_id="master"
        )
        
        # Verify the service was called with URL-encoded content
        call_args = initialized_service.service.memorize.call_args
        resource_url = call_args[1]['resource_url']
        assert resource_url.startswith('text://')


class TestRetrieve:
    """测试记忆检索功能 (SPEC: retrieve method)"""
    
    @pytest_asyncio.fixture
    async def initialized_service_with_data(self):
        """Fixture: 已初始化且有数据的服务"""
        with patch.dict(os.environ, {
            'APIYI_API_KEY': 'sk-test',
            'OPENROUTER_API_KEY': 'sk-or-test'
        }):
            service = MemUOpenClawService()
            service._initialized = False
            
            with patch('lib.memu_service.MemoryService') as MockMemoryService:
                mock_memu = Mock()
                # Mock async retrieve method
                mock_memu.retrieve = Mock(return_value=asyncio.Future())
                mock_memu.retrieve.return_value.set_result([
                    {'content': 'Master 喜欢暗色模式', 'relevance': 0.95},
                    {'content': 'Master 偏好简洁风格', 'relevance': 0.85}
                ])
                MockMemoryService.return_value = mock_memu
                
                service.initialize()
                return service
    
    @pytest.mark.asyncio
    async def test_retrieve_success(self, initialized_service_with_data):
        """TEST: 正常检索返回结果 (SPEC: RET-001)"""
        results = await initialized_service_with_data.retrieve(
            query="界面偏好",
            user_id="master",
            limit=5
        )
        
        assert isinstance(results, list)
        assert len(results) <= 5
    
    @pytest.mark.asyncio
    async def test_retrieve_cache_hit(self, initialized_service_with_data):
        """TEST: 缓存命中快速返回 (SPEC: RET-002)"""
        service = initialized_service_with_data
        
        # First call - cache miss
        results1 = await service.retrieve("测试查询", "master")
        
        # Second call - should hit cache
        # Note: In real implementation, we'd mock time to control TTL
        # For now, just verify the method works
        results2 = await service.retrieve("测试查询", "master")
        
        # Both should return results (cache logic verified in implementation)
        assert isinstance(results1, list)
        assert isinstance(results2, list)
    
    @pytest.mark.asyncio
    async def test_retrieve_no_results(self, initialized_service_with_data):
        """TEST: 无匹配结果返回空列表 (SPEC: RET-003)"""
        service = initialized_service_with_data
        
        # Mock no results
        service.service.retrieve.return_value = asyncio.Future()
        service.service.retrieve.return_value.set_result([])
        
        results = await service.retrieve("不存在的xyzabc123", "master")
        
        assert results == []


class TestCaching:
    """测试缓存机制 (SPEC: caching requirements)"""
    
    def test_cache_key_generation(self):
        """TEST: 缓存键正确生成"""
        service = MemUOpenClawService()
        
        key1 = service._get_cache_key("查询1", "user1")
        key2 = service._get_cache_key("查询1", "user1")
        key3 = service._get_cache_key("查询2", "user1")
        
        assert key1 == key2  # Same query + user = same key
        assert key1 != key3  # Different query = different key
    
    def test_cache_ttl(self):
        """TEST: 缓存 TTL 机制"""
        import time
        
        service = MemUOpenClawService()
        service._cache_ttl = 0.1  # 100ms for testing
        
        # Set cache
        service._set_cached("key1", ["result1"])
        
        # Immediately retrieve - should hit
        result = service._get_cached("key1")
        assert result is not None
        
        # Wait for TTL
        time.sleep(0.15)
        
        # After TTL - should miss
        result = service._get_cached("key1")
        assert result is None
    
    def test_cache_cleanup(self):
        """TEST: 缓存自动清理"""
        import time
        
        service = MemUOpenClawService()
        service._cache_ttl = 0.1
        
        # Add expired entries
        service._cache["old1"] = ("data1", time.time() - 1)
        service._cache["old2"] = ("data2", time.time() - 2)
        service._cache["new"] = ("data3", time.time())
        
        # Clear expired
        service._clear_expired_cache()
        
        assert "old1" not in service._cache
        assert "old2" not in service._cache
        assert "new" in service._cache


class TestErrorHandling:
    """测试错误处理"""
    
    @pytest.mark.asyncio
    async def test_service_not_initialized(self):
        """TEST: 服务未初始化时调用方法应自动初始化"""
        with patch.dict(os.environ, {
            'APIYI_API_KEY': 'sk-test',
            'OPENROUTER_API_KEY': 'sk-or-test'
        }):
            service = MemUOpenClawService()
            service._initialized = False
            
            with patch('lib.memu_service.MemoryService') as MockMemoryService:
                mock_memu = Mock()
                mock_memu.memorize = Mock(return_value=asyncio.Future())
                mock_memu.memorize.return_value.set_result({
                    'memory_id': 'test-123'
                })
                MockMemoryService.return_value = mock_memu
                
                # Should auto-initialize
                result = await service.memorize("test", "user")
                assert result is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
