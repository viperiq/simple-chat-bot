$(document).ready(function () {
  $('#send-button').click(function () {
      sendMessage();
  });

  $('#user-message').keypress(function (e) {
      if (e.which === 13) {
          sendMessage();
      }
  });

  var chatContainer = $('#chat-container');
  var chatToggle = $('#chat-toggle');
  var chatHistory = $('#chat-history');

  chatToggle.click(function () {
      chatContainer.toggle();
      if (chatContainer.is(":visible")) {
          chatHistory.scrollTop(chatHistory[0].scrollHeight);
      }
  });

  function sendMessage() {
      var userMessage = $('#user-message').val();
      if (userMessage !== '') {
          $('#chat-history').append('<div class="user-message">' + userMessage + '</div>');
          $('#user-message').val('');

          
          $.ajax({
              type: 'POST',
              url: '/chat',
              contentType: 'application/json;charset=UTF-8',
              data: JSON.stringify({'message': userMessage}),
              success: function (response) {
                  var botMessage = response.bot_message;
                  $('#chat-history').append('<div class="bot-message">' + botMessage + '</div>');
                  $('#chat-history').scrollTop($('#chat-history')[0].scrollHeight);
              }
          });
      }
  }
});

