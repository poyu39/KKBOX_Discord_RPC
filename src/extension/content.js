function isplaying() {
    if (document.querySelector(`.V9Lcie.k-icon.WveBvd.k-icon-now_playing-play.control`) != null) {
        return false;
    } else if (document.querySelector(`.V9Lcie.k-icon.WveBvd.k-icon-now_playing-pause.control`) != null) {
        if (document.querySelector(`.lzC879.UqH7yc`) != null) {
            return true;
        } else {
            return false;
        }
        
    }
    // if (play_status == '暫停') {
    //     return true;
    // } else if (play_status == '繼續播放') {
    //     return false;
    // }
    
}

function getSongName() {
    let song_name = document.querySelector(`.hayDaa`).querySelector('a').innerText;
    return song_name;
}

function getSongURL() {
    let song_url = document.querySelector(`.hayDaa`).querySelector('a').getAttribute('href');
    return song_url;
}

function getSongPlayTime() {
    let song_now_time = document.querySelector(`.bR5Q8S.H90HDr`).querySelectorAll('span')[0].innerText;
    let song_time_len = document.querySelector(`.bR5Q8S.H90HDr`).querySelectorAll('span')[1].innerText;
    return [song_now_time, song_time_len];
}

function getSongImage() {
    let song_image = document.querySelector(`.kl3pDr`).querySelector('a').querySelector('img').getAttribute('src');
    return song_image;
}

function getSongAuthor() {
    let song_author = document.querySelector(`.yKVKxJ`).innerText;
    return song_author;
}

function send_data_to_bg(result_data) {
    chrome.runtime.sendMessage({type: "kkbox_data", options: { 
        kkbox_data: result_data
    }});
}

function listener() {
    let result_data = {};
    result_data['play_status'] = isplaying();
    if (result_data['play_status'] == true) {
        result_data['song_name'] = getSongName();
        result_data['song_url'] = getSongURL();
        result_data['song_time'] = getSongPlayTime();
        result_data['song_image'] = getSongImage();
        result_data['song_author'] = getSongAuthor();
        send_data_to_bg(JSON.stringify(result_data));
    }
    console.log(JSON.stringify(result_data));
    
}

listener();