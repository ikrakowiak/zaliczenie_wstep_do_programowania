// BAZA ZDAŃ

const texts = [
    "Ala ma kota",
    "Python to świetny język programowania",
    "Flask jest lekkim frameworkiem webowym",
    "Programowanie wymaga cierpliwości",
    "Uczenie się przez praktykę daje najlepsze efekty",
    "Poranek był chłodny, ale pełen jasnego światła",
    "Na przystanku autobusowym panowała cisza",
    "Kawa pachniała intensywnie i dodawała energii",
    "W parku dzieci bawiły się bez pośpiechu",
    "Stare drzewa szumiały na wietrze",
    "Książka leżała otwarta na biurku",
    "Deszcz zaczął padać niespodziewanie",
    "Telefon zawibrował w kieszeni płaszcza",
    "Miasto budziło się powoli do życia",
    "Na niebie pojawiły się ciemne chmury",
    "Muzyka cicho grała w tle",
    "Kot przeciągnął się leniwie na kanapie",
    "Zapach świeżego chleba wypełnił kuchnię",
    "Zegar tykał miarowo",
    "Okno było lekko uchylone",
    "Kartka papieru pozostała pusta",
    "Myśli krążyły wokół nowych planów",
    "Ulica była mokra po nocnym deszczu",
    "Ktoś śmiał się głośno za rogiem",
    "Światło latarni odbijało się w kałużach",
    "Komputer uruchamiał się dłużej niż zwykle",
    "W pokoju panował przyjemny półmrok",
    "Drzwi zamknęły się cicho",
    "Herbata powoli stygnęła w kubku",
]

// ZMIENNE GLOBALNE

let currentText = "";
let time = 60;
let timer = null;
let gameRunning = false;
let score = 0;

// START GRY

function startGame() {
    score = 0;
    document.getElementById("result").innerText = "";

    currentText = getRandomText();
    document.getElementById("reference-text").innerText = currentText;

    time = 60;
    document.getElementById("time").innerText = time;

    const input = document.getElementById("text-input");
    input.value = "";
    input.disabled = false;
    input.focus();

    gameRunning = true;

    clearInterval(timer);
    timer = setInterval(() => {
        time--;
        document.getElementById("time").innerText = time;

        if (time <= 0) {
            stopGame();
        }
    }, 1000);
}

// ZATRZYMANIE GRY

function stopGame() {
    if (!gameRunning) return;

    gameRunning = false;
    clearInterval(timer);

    document.getElementById("text-input").disabled = true;

    document.getElementById("result").innerText =
        `Twój wynik: ${score}`;

    saveScore(score);
}

// LOSOWANIE NOWEGO ZDANIA

function getRandomText() {
    let newText;
    do {
        newText = texts[Math.floor(Math.random() * texts.length)];
    } while (newText === currentText);
    return newText;
}

// WERYFIKACJA WPISYWANEGO TEKSTU

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("text-input").addEventListener("input", () => {
        if (!gameRunning) return;

        const input = document.getElementById("text-input");

        if (input.value.trim() === currentText) {
            score += currentText.length;

            currentText = getRandomText();
            document.getElementById("reference-text").innerText = currentText;

            input.value = "";
        }
    });
});

// ZAPISYWANIE WYNIKU

function saveScore(points) {
    fetch("/save_score", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "points=" + points
    });
}