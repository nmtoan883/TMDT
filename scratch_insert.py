import uuid

with open('core/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

if 'LiveChatSession' not in text:
    if 'import uuid' not in text:
        text = 'import uuid\n' + text

    chat_models = """
class LiveChatSession(models.Model):
    session_key = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Live Chat Session'
        verbose_name_plural = 'Live Chat Sessions'

    def __str__(self):
        return f"Chat Session: {str(self.session_key)[:8]}"

class LiveChatMessage(models.Model):
    session = models.ForeignKey(LiveChatSession, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def __str__(self):
        prefix = 'Admin' if self.is_admin else 'User'
        return f"{prefix}: {self.content[:30]}"
"""
    text += '\n' + chat_models
    with open('core/models.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Models added successfully')
else:
    print('Models already exist')
