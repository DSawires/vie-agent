Send a text message to an active conversation
POST
https://live-mt-server.wati.io/api/ext/v3/conversations/messages/texth

Body Params
target
string
required
The target conversation in the following formats:

ConversationId: The unique ID of a conversation.
PhoneNumber: The recipient's phone number (e.g., 14155552671).
Channel:PhoneNumber: A combination of the channel (name or phone number) and the recipient's phone number (e.g., MyChannel:1415552671, 123456789:1415552671).
text
string
required
Message content.
