from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input
from chatter import chatter
from haystack.dataclasses import ChatMessage as hsmessage
from textual import work
from textual.reactive import reactive
from excutor import *

# -----------------------------
# Chat Message
# -----------------------------

llm = chatter()


class ChatMessage(Horizontal):
    text: reactive[str] = reactive("")

    def __init__(self, role: str, text: str, is_error: bool = False):
        super().__init__()

        self.role = role
        self.text = text
        self.is_error = is_error
        self.styles.height = "auto"
        self.styles.margin = 1

    def compose(self) -> ComposeResult:
        if self.role == "assistant":
            yield Static("🤖", classes="avatar")
            if self.is_error:
                yield Static(
                    self.text,
                    classes="bubble assistant-error",
                    shrink=True,
                    id="message_text",
                )
            else:
                yield Static(
                    self.text,
                    classes="bubble assistant",
                    shrink=True,
                    id="message_text",
                )

        else:
            yield Static(classes="spacer")
            yield Static(self.text, classes="bubble user", id="message_text")
            yield Static("🧑", classes="avatar", shrink=True)

    def watch_text(self, old_value: str, new_value: str) -> None:
        try:
            text_widget = self.query_one("#message_text", Static)
            text_widget.update(new_value)
            self.styles.height = "auto"
        except Exception:
            pass

    def set_error_style(self):
        def _apply():
            text_widget = self.query_one("#message_text", Static)
            text_widget.remove_class("assistant")
            text_widget.add_class("assistant-error")

        self.call_after_refresh(_apply)


# -----------------------------
# Chat Panel
# -----------------------------


class ChatPanel(Vertical):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_message(self, role, text):
        msg = ChatMessage(role, text)
        self.mount(msg)
        self.scroll_end(animate=False)
        return msg

    def remove_message(self, message_widget: ChatMessage):
        message_widget.remove()


# -----------------------------
# Main App
# -----------------------------


class AIChatApp(App):

    CSS = """
    Static {
       padding: 0;
    }
    Horizontal {
       padding: 0;
    }
    Screen {
        layout: vertical;
    }

    #main {
        height: 1fr;
    }
    
    Input {
        dock: bottom;
        border: round #344156;
        border-title-style: bold ;
        border-title-color: #9cc169;
        border-title-align: center;
    }

    #chat {
        border: round #344156;
        width: 1fr;
        overflow: auto;
        align: left top;
    }
    .avatar {
        width: auto;
        padding:1 1;
    }
    .bubble{
        max-width:93%;
        min-width:0%;
        width:auto;
        padding: 0 0;
    }
    .spacer{
      width: 1fr;
    }
   
    .assistant {
        padding: 0 0;
        border: round #323e53;
        color: #afafaf;
    }

    .assistant-error {
        padding: 0 0;
        border: round #ff4d2a;
        color: #f24af3;
    }

    .user {
        padding: 0 0;
        border: round #0f6e65;
        color: #e9c053;
        
    }

    """

    def __init__(self):
        super().__init__()
        self.his = []

    def compose(self) -> ComposeResult:
        yield ChatPanel(id="chat")
        input = Input(placeholder="Type message...")
        input.border_title = "CWD /home/liangtao"
        yield input

    def on_mount(self):
        chat = self.query_one("#chat", ChatPanel)
        greet = "How can I help you?"
        chat.add_message("assistant", greet)
        self.his.append(hsmessage.from_assistant(greet))

    def on_input_submitted(self, event: Input.Submitted):
        text = event.value
        event.input.value = ""
        chat = self.query_one("#chat", ChatPanel)
        chat.add_message("user", text)
        self.his.append(hsmessage.from_user(text))
        if not is_shell_command(text):
            self.ai_msg = chat.add_message("assistant", "on my way...")
            self.ask_llm()
        else:
            self.ai_msg = chat.add_message("assistant", "")
            resp, code = run_cmd(text)
            if not resp:
                resp = "Done"
            else:
                resp = resp.rstrip("\n")
            self.update_response(resp, code != 0)
            if text.startswith("cd"):
                if code == 0:
                    parts = text.split(maxsplit=1)
                    path = parts[1].strip() if len(parts) > 1 else ""
                    event.input.border_title = f"CWD {path}"

    @work(thread=True)
    def ask_llm(self):
        def on_stream(chunk: str):
            self.call_from_thread(self.update_response, chunk)

        llm.aiChat(self.his[-5:], call_back=on_stream)
        self.call_from_thread(self.finish_response)

    def update_response(self, chunk, is_error: bool = False):
        if self.ai_msg:
            if self.ai_msg.text == "on my way...":
                self.ai_msg.text = chunk
            else:
                self.ai_msg.text += chunk
            if is_error:
                self.ai_msg.set_error_style()

    def finish_response(self):
        if self.ai_msg:
            self.his.append(hsmessage.from_assistant(self.ai_msg.text))


if __name__ == "__main__":
    AIChatApp().run()
