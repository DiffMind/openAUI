from haystack import component
from typing import List
from haystack.dataclasses import ChatMessage


@component
class router:
    @component.output_types(
        general=List[ChatMessage],
        tool=List[ChatMessage],
    )
    def run(self, messages: List[ChatMessage]):
        if messages[0].tool_call or messages[0].tool_calls:
            return {"tool": messages}
        else:
            return {"general": messages}
