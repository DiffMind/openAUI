import sys, os
import threading, time, logging
from typing import List

sys.path.append(os.path.abspath(".."))
from haystack import Pipeline
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack_integrations.tools.mcp import StreamableHttpServerInfo, MCPToolset
from haystack.components.tools import ToolInvoker
from haystack.components.converters import OutputAdapter
from haystack.dataclasses import ChatMessage
from pathlib import Path
import json
import threading
from mcp.server.fastmcp import FastMCP
from tools import disks
from router import router


class chatter(object):
    def __init__(
        self,
        llm_url: str = "http://127.0.0.1:6060/v1",
        llm_model: str = "gpt-5-min",
        mcp_host: str = "127.0.0.1",
        mcp_port: int = "8083",
        call_back=None,
        logLevel: str = "info",
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.info("initing...")
        self.llm_url = llm_url
        self.llm_model = llm_model

        self.mcp_host = mcp_host
        self.mcp_port = mcp_port

        self.call_back = call_back
        self.logLevel = logLevel

        mcp_server_ready = threading.Event()
        self.threadMcp = threading.Thread(
            target=self.startMcpServer,
            args=(mcp_server_ready, self.mcp_host, self.mcp_port),
            daemon=True,
        )
        self.threadMcp.start()
        if not mcp_server_ready.wait(timeout=10):
            raise TimeoutError("MCP server start failed...")
        self.chatPL = self.initPipLine()

    def startMcpServer(self, envent: threading.Event, host, port):
        mcp = FastMCP(__name__, host=host, port=port)
        disks.register_tools(mcp)
        print(f"MCP Serving on http://{host}:{port}/mcp")
        envent.set()
        mcp.run(transport="streamable-http")

    def initPipLine(self):
        ##########################
        # chat pipeline
        # ########################
        # Components #
        chatPL = Pipeline()

        server_info = StreamableHttpServerInfo(
            url=f"http://{self.mcp_host}:{self.mcp_port}/mcp"
        )
        toolset = MCPToolset(server_info=server_info, eager_connect=True)
        llm_tool = OpenAIChatGenerator(
            api_base_url=self.llm_url,
            model=self.llm_model,
            tools=toolset,
            tools_strict=True,
            generation_kwargs={
                "temperature": 0.1,
            },
        )
        chatPL.add_component("llm_tool", llm_tool)
        chatPL.add_component("llm_router", router())
        chatPL.add_component("tool_invoker", ToolInvoker(tools=toolset))
        chatPL.add_component(
            "tool_adapter",
            OutputAdapter(
                template="{{ initial_msg + initial_tool_messages + tool_messages }}",
                output_type=list[ChatMessage],
                unsafe=True,
            ),
        )
        llm_response = OpenAIChatGenerator(
            api_base_url=self.llm_url,
            model=self.llm_model,
        )
        chatPL.add_component("llm_response", llm_response)

        ##########################
        # Connections
        # ########################
        chatPL.connect("llm_tool.replies", "llm_router.messages")
        chatPL.connect("llm_router.tool", "tool_invoker.messages")
        chatPL.connect("llm_router.tool", "tool_adapter.initial_tool_messages")
        chatPL.connect("tool_invoker.tool_messages", "tool_adapter.tool_messages")
        chatPL.connect("tool_adapter.output", "llm_response.messages")
        if self.logLevel.lower() == "debug":
            chatPL.draw("pipeline.png")
        return chatPL

    def aiChat(self, messages: List[ChatMessage]):
        data = {
            "llm_tool": {"messages": messages},
            "tool_adapter": {"initial_msg": messages},
        }
        result = self.chatPL.run(data=data, include_outputs_from=["llm_router"])
        if "general" in result["llm_router"]:
            return result["llm_router"]["general"][0].text
        else:
            return result["llm_response"]["replies"][0].text
