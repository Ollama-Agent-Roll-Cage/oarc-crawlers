import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock, call
from contextlib import asynccontextmanager

from oarc_crawlers.core.mcp import MCPManager
from oarc_utils.errors import MCPError

# --- Fixtures ---

@pytest.fixture
def manager():
    """Fixture for MCPManager instance."""
    return MCPManager(name="TestServer", dependencies=["dep1"])

@pytest.fixture
def mock_mcp():
    """Fixture for a mocked FastMCP instance."""
    mcp = MagicMock()
    # Use MagicMock for the return value to track calls on the decorated function mock
    mcp.tool = MagicMock(return_value=MagicMock(side_effect=lambda f: f))
    mcp.resource = MagicMock(return_value=MagicMock(side_effect=lambda f: f))
    mcp.prompt = MagicMock(return_value=MagicMock(side_effect=lambda f: f))
    mcp.run = MagicMock()
    mcp.mount = MagicMock()
    return mcp

@pytest.fixture
def manager_with_mock_mcp(mock_mcp):
    """Fixture for MCPManager with a mocked FastMCP."""
    with patch('oarc_crawlers.core.mcp.mcp_manager.FastMCP', return_value=mock_mcp):
        manager = MCPManager(name="TestServerMocked", dependencies=["dep1"])
        # Manually assign the mock mcp instance if needed for direct assertions
        manager.mcp = mock_mcp
        return manager

@pytest.fixture
def mock_client():
    """Fixture for a mocked MCP Client."""
    client = AsyncMock()
    client.call_tool = AsyncMock(return_value="tool_result")
    client.read_resource = AsyncMock(return_value="resource_result")
    client.get_prompt = AsyncMock(return_value="prompt_result")
    return client

@pytest.fixture
def mock_client_context(mock_client):
    """Fixture for a mocked async context manager for the client."""
    @asynccontextmanager
    async def _mock_context(*args, **kwargs):
        yield mock_client
    return _mock_context

# --- Test Cases ---

def test_mcp_manager_init(manager):
    """Test MCPManager initialization."""
    assert manager.name == "TestServer"
    assert manager.dependencies == ["dep1"]
    assert manager.mcp is not None
    assert manager.mcp.name == "TestServer"
    assert manager.mcp.dependencies == ["dep1"]
    assert manager.tools == {}
    assert manager.resources == {}
    assert manager.prompts == {}

def test_mcp_manager_init_no_deps():
    """Test MCPManager initialization with default dependencies."""
    manager_no_deps = MCPManager(name="NoDepsServer")
    assert manager_no_deps.dependencies == []

@pytest.mark.asyncio
async def test_add_tool_decorator(manager_with_mock_mcp, mock_mcp):
    """Test add_tool using decorator syntax."""
    @manager_with_mock_mcp.add_tool(description="Test tool")
    async def my_tool(arg: str) -> str:
        return f"tool_{arg}"

    assert "my_tool" in manager_with_mock_mcp.tools
    assert manager_with_mock_mcp.tools["my_tool"] == my_tool
    mock_mcp.tool.assert_called_once_with(description="Test tool")
    # Check if the inner decorator mock was called
    mock_mcp.tool.return_value.assert_called_once()

@pytest.mark.asyncio
async def test_add_tool_method(manager_with_mock_mcp, mock_mcp):
    """Test add_tool using method call syntax."""
    async def another_tool(arg: int) -> int:
        return arg + 1

    manager_with_mock_mcp.add_tool(another_tool, name="custom_tool_name")

    assert "another_tool" in manager_with_mock_mcp.tools
    assert manager_with_mock_mcp.tools["another_tool"] == another_tool
    mock_mcp.tool.assert_called_once_with(name="custom_tool_name")
    mock_mcp.tool.return_value.assert_called_once()

@pytest.mark.asyncio
async def test_add_resource_decorator(manager_with_mock_mcp, mock_mcp):
    """Test add_resource using decorator syntax."""
    @manager_with_mock_mcp.add_resource("/test/resource", description="Test resource")
    async def my_resource() -> str:
        return "resource_data"

    assert "/test/resource" in manager_with_mock_mcp.resources
    assert manager_with_mock_mcp.resources["/test/resource"] == my_resource
    mock_mcp.resource.assert_called_once_with("/test/resource", description="Test resource")
    mock_mcp.resource.return_value.assert_called_once()

@pytest.mark.asyncio
async def test_add_resource_method(manager_with_mock_mcp, mock_mcp):
    """Test add_resource using method call syntax."""
    async def another_resource() -> dict:
        return {"key": "value"}

    manager_with_mock_mcp.add_resource("/another", another_resource, name="custom_resource")

    assert "/another" in manager_with_mock_mcp.resources
    assert manager_with_mock_mcp.resources["/another"] == another_resource
    mock_mcp.resource.assert_called_once_with("/another", name="custom_resource")
    mock_mcp.resource.return_value.assert_called_once()

@pytest.mark.asyncio
async def test_add_prompt_decorator(manager_with_mock_mcp, mock_mcp):
    """Test add_prompt using decorator syntax."""
    @manager_with_mock_mcp.add_prompt(description="Test prompt")
    async def my_prompt(topic: str) -> str:
        return f"Prompt about {topic}"

    assert "my_prompt" in manager_with_mock_mcp.prompts
    assert manager_with_mock_mcp.prompts["my_prompt"] == my_prompt
    mock_mcp.prompt.assert_called_once_with(description="Test prompt")
    mock_mcp.prompt.return_value.assert_called_once()

@pytest.mark.asyncio
async def test_add_prompt_method(manager_with_mock_mcp, mock_mcp):
    """Test add_prompt using method call syntax."""
    async def another_prompt(user_input: str) -> str:
        return f"Response to {user_input}"

    manager_with_mock_mcp.add_prompt(another_prompt, name="custom_prompt")

    assert "another_prompt" in manager_with_mock_mcp.prompts
    assert manager_with_mock_mcp.prompts["another_prompt"] == another_prompt
    mock_mcp.prompt.assert_called_once_with(name="custom_prompt")
    mock_mcp.prompt.return_value.assert_called_once()

def test_run(manager_with_mock_mcp, mock_mcp):
    """Test the run method."""
    manager_with_mock_mcp.run(transport="sse", host="localhost", port=8080)
    mock_mcp.run.assert_called_once_with(transport="sse", host="localhost", port=8080)

@patch('oarc_crawlers.core.mcp.mcp_manager.MCPUtils')
def test_install_with_script_path(mock_mcp_utils, manager):
    """Test install method when script_path is provided."""
    mock_mcp_utils.install_mcp.return_value = True
    result = manager.install(script_path="/path/to/script.py", name="CustomInstallName", with_deps=["extra_dep"])

    assert result is True
    mock_mcp_utils.install_mcp.assert_called_once_with(
        script_path="/path/to/script.py",
        name="CustomInstallName",
        mcp_name="TestServer",
        dependencies=["dep1", "extra_dep"]
    )
    mock_mcp_utils.generate_mcp_script.assert_not_called()
    mock_mcp_utils.install_mcp_with_content.assert_not_called()

@patch('oarc_crawlers.core.mcp.mcp_manager.MCPUtils')
def test_install_without_script_path(mock_mcp_utils, manager_with_mock_mcp):
    """Test install method when script_path is None (generates script)."""
    # Add some items to generate code for
    @manager_with_mock_mcp.add_tool
    async def dummy_tool(): pass
    @manager_with_mock_mcp.add_resource("/dummy")
    async def dummy_resource(): pass
    # Add a prompt to ensure generate_prompt_code is called with non-empty dict
    @manager_with_mock_mcp.add_prompt
    async def dummy_prompt(): pass

    mock_mcp_utils.generate_mcp_script.return_value = "script_header\n"
    mock_mcp_utils.generate_tool_code.return_value = "tool_code\n"
    mock_mcp_utils.generate_resource_code.return_value = "resource_code\n"
    mock_mcp_utils.generate_prompt_code.return_value = "prompt_code\n" # Return some code
    mock_mcp_utils.install_mcp_with_content.return_value = True

    result = manager_with_mock_mcp.install(name="GeneratedInstall", with_deps=["extra_dep2"])

    assert result is True
    mock_mcp_utils.generate_mcp_script.assert_called_once_with("TestServerMocked", ["dep1", "extra_dep2"])
    mock_mcp_utils.generate_tool_code.assert_called_once_with(manager_with_mock_mcp.tools)
    mock_mcp_utils.generate_resource_code.assert_called_once_with(manager_with_mock_mcp.resources)
    # Assert call with the actual prompts dictionary
    mock_mcp_utils.generate_prompt_code.assert_called_once_with(manager_with_mock_mcp.prompts)

    expected_script_content = "script_header\n\n# Add tools, resources, and prompts\ntool_code\nresource_code\nprompt_code\n"
    mock_mcp_utils.install_mcp_with_content.assert_called_once_with(
        expected_script_content,
        name="GeneratedInstall",
        mcp_name="TestServerMocked",
        dependencies=["dep1", "extra_dep2"]
    )
    mock_mcp_utils.install_mcp.assert_not_called()

@patch('oarc_crawlers.core.mcp.mcp_manager.MCPUtils')
def test_install_failure(mock_mcp_utils, manager):
    """Test install method when MCPUtils raises an exception."""
    mock_mcp_utils.install_mcp.side_effect = Exception("Install failed")

    with pytest.raises(MCPError, match="Failed to install MCP server: Install failed"):
        manager.install(script_path="/path/to/script.py")

@pytest.mark.asyncio
@patch('oarc_crawlers.core.mcp.mcp_manager.Client', new_callable=MagicMock)
async def test_client_session(mock_client_class, manager_with_mock_mcp, mock_client, mock_client_context):
    """Test the client_session context manager."""
    mock_client_class.return_value.__aenter__.return_value = mock_client # Mock the async context manager
    mock_client_class.return_value.__aexit__.return_value = None
    
    handler = lambda x: x # Define a specific handler for the test

    async with manager_with_mock_mcp.client_session(transport="ws", sampling_handler=handler) as client:
        assert client == mock_client
        # Verify Client was instantiated correctly with the passed handler
        mock_client_class.assert_called_once_with(
            manager_with_mock_mcp.mcp,
            transport="ws",
            sampling_handler=handler # Assert with the specific handler instance
        )
    # Check __aenter__ and __aexit__ were called
    assert mock_client_class.return_value.__aenter__.called
    assert mock_client_class.return_value.__aexit__.called

@pytest.mark.asyncio
@patch('oarc_crawlers.core.mcp.mcp_manager.Client')
async def test_call_tool(mock_client_class, manager_with_mock_mcp, mock_client, mock_client_context):
    """Test calling a tool via the manager."""
    # Setup the mock Client context manager behavior
    mock_instance = mock_client_class.return_value
    mock_instance.__aenter__.return_value = mock_client
    mock_instance.__aexit__ = AsyncMock()

    params = {"arg1": "value1"}
    result = await manager_with_mock_mcp.call_tool("my_tool", params, transport="sse", extra_arg="foo")

    assert result == "tool_result"
    mock_client_class.assert_called_once_with(manager_with_mock_mcp.mcp, transport="sse", extra_arg="foo", sampling_handler=None)
    mock_client.call_tool.assert_awaited_once_with("my_tool", params)
    assert mock_instance.__aenter__.called
    assert mock_instance.__aexit__.called

@pytest.mark.asyncio
@patch('oarc_crawlers.core.mcp.mcp_manager.Client')
async def test_read_resource(mock_client_class, manager_with_mock_mcp, mock_client, mock_client_context):
    """Test reading a resource via the manager."""
    mock_instance = mock_client_class.return_value
    mock_instance.__aenter__.return_value = mock_client
    mock_instance.__aexit__ = AsyncMock()

    uri = "/data/item"
    result = await manager_with_mock_mcp.read_resource(uri, transport="ws")

    assert result == "resource_result"
    mock_client_class.assert_called_once_with(manager_with_mock_mcp.mcp, transport="ws", sampling_handler=None)
    mock_client.read_resource.assert_awaited_once_with(uri)
    assert mock_instance.__aenter__.called
    assert mock_instance.__aexit__.called

@pytest.mark.asyncio
@patch('oarc_crawlers.core.mcp.mcp_manager.Client')
async def test_get_prompt(mock_client_class, manager_with_mock_mcp, mock_client, mock_client_context):
    """Test getting a prompt via the manager."""
    mock_instance = mock_client_class.return_value
    mock_instance.__aenter__.return_value = mock_client
    mock_instance.__aexit__ = AsyncMock()

    params = {"topic": "testing"}
    result = await manager_with_mock_mcp.get_prompt("my_prompt", params)

    assert result == "prompt_result"
    mock_client_class.assert_called_once_with(manager_with_mock_mcp.mcp, transport=None, sampling_handler=None)
    mock_client.get_prompt.assert_awaited_once_with("my_prompt", params)
    assert mock_instance.__aenter__.called
    assert mock_instance.__aexit__.called

@pytest.mark.asyncio
@patch('oarc_crawlers.core.mcp.mcp_manager.Client')
async def test_get_prompt_no_params(mock_client_class, manager_with_mock_mcp, mock_client, mock_client_context):
    """Test getting a prompt via the manager without parameters."""
    mock_instance = mock_client_class.return_value
    mock_instance.__aenter__.return_value = mock_client
    mock_instance.__aexit__ = AsyncMock()

    result = await manager_with_mock_mcp.get_prompt("another_prompt")

    assert result == "prompt_result"
    mock_client_class.assert_called_once_with(manager_with_mock_mcp.mcp, transport=None, sampling_handler=None)
    mock_client.get_prompt.assert_awaited_once_with("another_prompt", {}) # Ensure empty dict is passed
    assert mock_instance.__aenter__.called
    assert mock_instance.__aexit__.called

def test_mount(manager_with_mock_mcp, mock_mcp):
    """Test mounting another MCP instance."""
    other_mcp_mock = MagicMock()
    other_manager = MagicMock(spec=MCPManager)
    other_manager.name = "OtherServer"
    other_manager.mcp = other_mcp_mock

    result = manager_with_mock_mcp.mount("/prefix", other_manager)

    assert result == manager_with_mock_mcp # Check for fluent interface
    mock_mcp.mount.assert_called_once_with("/prefix", other_mcp_mock)
