
var apigClient;
	apigClient = apigClientFactory.newClient();

var messages = [], 
  lastUserMessage = "", 
  botMessage = "", 
  botName = 'DiningConcierge', 
  talking = false; 

	function chatbotResponse() {
		
		lastUserMessage = userMessage();

		return new Promise(function (resolve, reject) {
			let params = {};
			let additionalParams = {
			};
			var body = {
			"message" : lastUserMessage,
			"userId": "neel"
			}
			apigClient.chatbotPost(params, body, additionalParams)
			.then(function(result){
				
				reply = result.data.body;
				console.log(result);
				//alert(reply);
			
				$("<li class='replies'><img src='https://restuarantchatbot.s3.amazonaws.com/frontend/images/the-bot.jpg' alt='' /><p>" + reply + "</p></li>").appendTo($('.messages ul'));
				$('.message-input input').val(null);
				$('.contact.active .preview').html('<span>You: </span>' + reply);
				$(".messages").animate({ scrollTop: $(document).height() }, "fast");
				
				resolve(result.data.body);
				botMessage = result.data.body;
			}).catch( function(result){
				console.log("fail");
				botMessage = "Couldn't connect"
				reject(result);
			});
		})
	}


//Js for the chat application


$(".messages").animate({ scrollTop: $(document).height() }, "fast");

$("#profile-img").click(function() {
	$("#status-options").toggleClass("active");
});

$(".expand-button").click(function() {
  $("#profile").toggleClass("expanded");
	$("#contacts").toggleClass("expanded");
});

$("#status-options ul li").click(function() {
	$("#profile-img").removeClass();
	$("#status-online").removeClass("active");
	$("#status-away").removeClass("active");
	$("#status-busy").removeClass("active");
	$("#status-offline").removeClass("active");
	$(this).addClass("active");
	
	if($("#status-online").hasClass("active")) {
		$("#profile-img").addClass("online");
	} else if ($("#status-away").hasClass("active")) {
		$("#profile-img").addClass("away");
	} else if ($("#status-busy").hasClass("active")) {
		$("#profile-img").addClass("busy");
	} else if ($("#status-offline").hasClass("active")) {
		$("#profile-img").addClass("offline");
	} else {
		$("#profile-img").removeClass();
	};
	
	$("#status-options").removeClass("active");
});

function userMessage() {

	message = $(".message-input input").val();
	if($.trim(message) == '') {
		return false;
	}

	$('<li class="sent"><img src="https://restuarantchatbot.s3.amazonaws.com/frontend/images/the-user.jpg" alt="" /><p>' + message + '</p></li>').appendTo($('.messages ul'));
	$('.message-input input').val(null);
	$('.contact.active .preview').html('<span>You: </span>' + message);
	$(".messages").animate({ scrollTop: $(document).height() }, "fast");

	return message;
};

$('.submit').click(function() {
	// newMessage();
	chatbotResponse();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
		// newMessage();
		chatbotResponse();
    return false;
  }
});
