from chats.models import ChatGroup
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .forms import ChatMessageCreateForm


@login_required
def chat_view(request):
    chat_group = get_object_or_404(ChatGroup, group_name="public-chat")
    chat_messages = chat_group.chat_messages_rel.all()[:30]
    form = ChatMessageCreateForm()

    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                "message": message,
                "user": request.user,
            }
            return render(request, "chats/partials/chat_message_p.html", context)

    return render(
        request,
        "chats/chat.html",
        {
            "chat_messages": chat_messages,
            "form": form,
        },
    )
