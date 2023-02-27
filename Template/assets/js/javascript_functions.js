
window.SpeechRecognition = window.SpeechRecognition
    || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.interimResults = true;


const synth = window.speechSynthesis;
const voices = synth.getVoices();

recognition.onspeechend = function () {
    recognition.stop();
    $("#mic_button").css("background-color", "#006fe6");
    request_data();
}


recognition.addEventListener('result', e => {
    const transcript = Array.from(e.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('')
    $("#text_input").val(transcript);
    console.log(transcript);
});


function start_speech() {
    if (synth.speaking) {
        synth.cancel();
    }
    
    recognition.start();
    $("#mic_button").css("background-color", "red");
}


function text_to_speech(text_input) {
    text_input = ", " + text_input;
    let utter_this = new SpeechSynthesisUtterance(text_input);

    utter_this.onend = () => {
        console.log(text_input)
    };

    voices.forEach(element => {
        if (element.lang == "en-IN") {
            utter_this.voice = element;
        }
    });

    if (synth.speaking) {
        synth.cancel();
    }
    synth.speak(utter_this);
}


function request_data(input_command = "") {
    let text_input = $("#text_input").val();
    text_input = text_input.trim();

    if (input_command == "select_recipe") {
        text_input = "select_recipe";
    }
    else {
        insert_chat_sequence("request", text_input);
    }

    if (text_input == "") {
        return;
    }

    $("#text_input").val("");
    let request_data = {
        "unique_id": unique_id,
        "text": text_input,
    };

    $.ajax({
        type: "POST",
        url: base_url + "enter_text",
        data: JSON.stringify(request_data),
        contentType: "application/json",
        success: function (response) {
            insert_chat_sequence("response", response);
            text_to_speech(response);
        },
        dataType: "json"
    });
}

function insert_chat_sequence(chat_type, chat_text) {
    if (chat_type == "response") {
        let str_val = `
                <div class="row">
                    <div class="col"
                        style="width: 20%;padding-left: 102px;padding-right: 26px;margin-right: 2px;margin-bottom: 0px;margin-top: 7px;">
                        <div
                            style="border-radius: 6px;border-bottom-left-radius: 6px;border-bottom-right-radius: 0px;padding-left: 0px;padding-right: 1px;margin-right: 440px;padding-bottom: 0.4em;border: 1.7px solid var(--bs-blue);margin-bottom: 4px;">
                            <em><strong>Bot</strong></em><br>{chat_text}</div>
                    </div>
                </div>
                `;
        str_val = str_val.replace("{chat_text}", chat_text);
        str_val = str_val + $("#chat_history").html();
        $("#chat_history").html(str_val);
    }
    if (chat_type == "request") {
        let str_val = `
                <div class="row">
                    <div class="col"
                        style="width: 20%;padding-left: 102px;padding-right: 26px;margin-right: 2px;margin-top: -1px;margin-bottom: -1px;">
                        <div
                            style="border-radius: 6px;border-bottom-left-radius: 0px;border-bottom-right-radius: 6px;padding-left: 0px;padding-bottom: 0.4em;margin-bottom: 5px;margin-left: 314px;padding-right: 0px;margin-right: 55px;text-align: right;border: 1.7px solid var(--bs-green);margin-top: 2px;">
                            <em><strong>You</strong></em><br>{chat_text}</div>
                    </div>
                </div>
                `;
        str_val = str_val.replace("{chat_text}", chat_text);
        str_val = str_val + $("#chat_history").html();
        $("#chat_history").html(str_val);
    }
}