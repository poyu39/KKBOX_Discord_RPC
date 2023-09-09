function kkbox_page_js() {
    chrome.tabs.query({}, function (tabs) {
        tabs.forEach(function (tab) {
            if (tab.url.includes('play.kkbox.com')) {
                chrome.scripting.executeScript({
                    target : {tabId : tab.id},
                    files : [ "content.js" ],
                });
                // console.log(play_status);
            }
        });
    });
}

function send_data_to_host(data) {
    const socket = new WebSocket('ws://localhost:9239');

    socket.onopen = function() {
        socket.send(JSON.stringify(data));
    }
}

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type == "kkbox_data") {
        var kkbox_data = JSON.parse(request.options.kkbox_data);
        send_data_to_host(kkbox_data);
        // console.log(kkbox_data);
    }
});

const intervalTime = 1000;
setInterval(kkbox_page_js, intervalTime);