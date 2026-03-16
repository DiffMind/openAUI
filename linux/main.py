from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input
from chatter import chatter
from haystack.dataclasses import ChatMessage as hsmessage
from textual import work

# -----------------------------
# Chat Message
# -----------------------------

llm = chatter()


class ChatMessage(Horizontal):

    def __init__(self, role: str, text: str):
        super().__init__()

        self.role = role
        self.text = text
        self.styles.height = "auto"
        self.styles.margin = 1

    def compose(self) -> ComposeResult:
        if self.role == "assistant":
            yield Static("🤖", classes="avatar")
            yield Static(self.text, classes="bubble assistant", shrink=True)

        else:
            yield Static(classes="spacer")
            yield Static(self.text, classes="bubble user")
            yield Static("🧑", classes="avatar", shrink=True)


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

    Screen {
        layout: vertical;
    }

    #main {
        height: 1fr;
    }
    Input {
        dock: bottom;
        border: round #da97ff;
    }

    #chat {
        border: round #613dda;
        width: 1fr;
        overflow: auto;
        padding: 1;
        align: left top;
    }

    .avatar {
        width: 3;
    }
    .bubble{
        max-width:89%;
        min-width:19%;
        width:auto;
        padding: 0 1;
    }
    .spacer{
      width: 1fr;
    }
   
    .assistant {
        padding: 0 0;
        background: rgb(55, 15, 104);
        border: round rgb(55, 15, 104);
        
        color: white;
        
    }

    .user {
        padding: 0 0;
        background: rgb(45,90,241);
        border: round rgb(45,90,241);
        color: white;
        
    }

    """

    def __init__(self):
        super().__init__()
        self.his = []

    def compose(self) -> ComposeResult:
        yield ChatPanel(id="chat")
        yield Input(placeholder="Type message...")

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
        self.waiting_msg = chat.add_message("assistant", "on my way...")
        self.ask_llm(text)

    @work(thread=True)
    def ask_llm(self, text):
        self.his.append(hsmessage.from_user(text))
        nothink = "You are a helpful assistant. Do not output thinking process. Respond directly with the final answer."
        response = llm.aiChat([hsmessage.from_system(nothink)] + self.his[-5:])
        self.call_from_thread(self.update_chat, response)

    def update_chat(self, response):
        chat = self.query_one("#chat", ChatPanel)
        chat.add_message("assistant", response)
        if self.waiting_msg:
            chat.remove_message(self.waiting_msg)
        self.his.append(hsmessage.from_assistant(response))


if __name__ == "__main__":
    AIChatApp().run()
